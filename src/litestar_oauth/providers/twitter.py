"""Twitter/X OAuth2 provider implementation."""

from __future__ import annotations

import hashlib
import secrets
from base64 import urlsafe_b64encode
from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider
from litestar_oauth.types import OAuthToken

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class TwitterOAuthProvider(BaseOAuthProvider):
    """Twitter/X OAuth2 provider with PKCE support.

    Implements OAuth2 authentication flow for Twitter/X.
    Twitter requires PKCE (Proof Key for Code Exchange) for enhanced security.

    Default scopes:
        - users.read: Access basic user information
        - tweet.read: Access user's tweets

    User Info Mapping:
        - oauth_id: Twitter user ID
        - email: Not available (Twitter doesn't provide email in basic scope)
        - username: Twitter username (handle)
        - first_name: Extracted from name field (first word)
        - last_name: Extracted from name field (remaining words)
        - avatar_url: Twitter profile image URL
        - profile_url: Twitter profile URL

    Args:
        client_id: Twitter OAuth2 client ID.
        client_secret: Twitter OAuth2 client secret.
        scope: Optional custom scopes. Defaults to ["users.read", "tweet.read"].

    Note:
        Twitter OAuth2 requires PKCE. This provider automatically generates
        and manages the code_verifier and code_challenge parameters.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: list[str] | None = None,
    ) -> None:
        """Initialize the Twitter OAuth provider.

        Args:
            client_id: Twitter OAuth2 client ID.
            client_secret: Twitter OAuth2 client secret.
            scope: List of OAuth scopes to request. Defaults to provider-specific scopes.
        """
        super().__init__(client_id, client_secret, scope)
        self._code_verifier: str | None = None

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'twitter'.
        """
        return "twitter"

    @property
    def authorize_url(self) -> str:
        """Return Twitter authorization endpoint.

        Returns:
            Twitter OAuth2 authorization URL.
        """
        return "https://twitter.com/i/oauth2/authorize"

    @property
    def token_url(self) -> str:
        """Return Twitter token exchange endpoint.

        Returns:
            Twitter OAuth2 token URL.
        """
        return "https://api.twitter.com/2/oauth2/token"

    @property
    def user_info_url(self) -> str:
        """Return Twitter user info endpoint.

        Returns:
            Twitter API user endpoint URL.
        """
        return "https://api.twitter.com/2/users/me"

    def _default_scope(self) -> list[str]:
        """Return default scopes for Twitter OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["users.read", "tweet.read"]

    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge pair.

        Creates a cryptographically secure code verifier and derives the
        corresponding code challenge using SHA256.

        Returns:
            Tuple of (code_verifier, code_challenge).
        """
        # Generate code verifier (43-128 character random string)
        code_verifier = urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")

        # Generate code challenge using S256 method
        code_challenge = (
            urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest()).decode("utf-8").rstrip("=")
        )

        return code_verifier, code_challenge

    async def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        **kwargs: Any,
    ) -> str:
        """Generate authorization URL with PKCE parameters.

        Twitter requires PKCE for OAuth2 flows. This method generates the
        code_verifier and code_challenge, stores the verifier for later use
        in token exchange, and includes the challenge in the authorization URL.

        Args:
            redirect_uri: Callback URI for the OAuth flow.
            state: CSRF protection state parameter.
            **kwargs: Provider-specific parameters (e.g., scope, extra_params).

        Returns:
            Complete authorization URL with PKCE parameters.
        """
        from urllib.parse import urlencode

        # Generate PKCE pair
        code_verifier, code_challenge = self._generate_pkce_pair()
        self._code_verifier = code_verifier

        # Allow scope override via kwargs
        scope = kwargs.pop("scope", None) or " ".join(self.scope)
        extra_params = kwargs.pop("extra_params", {})

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        if extra_params:
            params.update(extra_params)

        return f"{self.authorize_url}?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        **kwargs: Any,
    ) -> OAuthToken:
        """Exchange authorization code for access token with PKCE.

        Includes the code_verifier in the token exchange request to complete
        the PKCE flow.

        Args:
            code: Authorization code from Twitter.
            redirect_uri: Redirect URI used in authorization.
            **kwargs: Provider-specific parameters. Can include 'code_verifier'
                     if managing PKCE externally.

        Returns:
            OAuth token with access token and metadata.

        Raises:
            TokenExchangeError: If exchange fails.
            ValueError: If code_verifier is not available.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for Twitter OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.exceptions import TokenExchangeError

        # Use provided code_verifier or the one generated during authorization
        code_verifier = kwargs.pop("code_verifier", None) or self._code_verifier

        if not code_verifier:
            msg = "code_verifier is required for Twitter OAuth2 PKCE flow"
            raise ValueError(msg)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                        "code_verifier": code_verifier,
                    },
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            raise TokenExchangeError(f"Failed to exchange authorization code: {e}") from e

        return OAuthToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in"),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope"),
            raw_response=data,
        )

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize Twitter user information.

        Retrieves user profile from Twitter API and normalizes it to OAuthUserInfo format.
        Twitter returns data wrapped in a "data" object.

        Args:
            access_token: Twitter OAuth access token.
            **kwargs: Additional parameters. Can include 'user_fields' for custom fields.

        Returns:
            Normalized user information.

        Raises:
            ImportError: If httpx is not installed.
            Exception: If user info fetch fails.

        Note:
            Twitter doesn't provide email addresses in the basic users.read scope.
            To access email, you need the "users.read" scope AND app-level permissions.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for Twitter OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        # Default user fields to request
        user_fields = kwargs.get(
            "user_fields",
            "id,name,username,profile_image_url",
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        params = {
            "user.fields": user_fields,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            response_data = response.json()

        # Twitter wraps user data in a "data" key
        user_data = response_data.get("data", {})

        # Parse name into first and last name
        name = user_data.get("name", "")
        first_name = ""
        last_name = ""

        if name:
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        username = user_data.get("username", "")

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(user_data.get("id", "")),
            email=None,  # Twitter doesn't provide email in basic scope
            email_verified=False,
            username=username,
            first_name=first_name,
            last_name=last_name,
            avatar_url=user_data.get("profile_image_url", ""),
            profile_url=f"https://twitter.com/{username}" if username else "",
            raw_data=response_data,
        )

    async def revoke_token(
        self,
        token: str,
        token_type_hint: str | None = None,
        **kwargs: Any,
    ) -> bool:
        """Revoke a Twitter OAuth2 token.

        Twitter supports token revocation through their OAuth2 revoke endpoint.

        Args:
            token: The access token to revoke.
            token_type_hint: Optional hint about token type (not used by Twitter).
            **kwargs: Additional provider-specific parameters.

        Returns:
            True if revocation succeeded, False otherwise.
        """
        try:
            import httpx
        except ImportError:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.twitter.com/2/oauth2/revoke",
                    data={
                        "client_id": self.client_id,
                        "token": token,
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError:
            return False
