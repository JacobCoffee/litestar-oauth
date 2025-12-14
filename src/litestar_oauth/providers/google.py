"""Google OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class GoogleOAuthProvider(BaseOAuthProvider):
    """Google OAuth2 provider with OpenID Connect support.

    Implements OAuth2 authentication flow for Google accounts.
    Supports OpenID Connect (OIDC) for enhanced authentication.

    Default scopes:
        - openid: Required for OIDC
        - email: Access user email
        - profile: Access user profile info

    User Info Mapping:
        - oauth_id: Google user ID (sub claim)
        - email: User email address
        - email_verified: Email verification status
        - username: Not provided by Google (uses email)
        - first_name: Given name
        - last_name: Family name
        - avatar_url: Profile picture URL
        - profile_url: Not provided by Google

    Args:
        client_id: Google OAuth client ID.
        client_secret: Google OAuth client secret.
        scope: Optional custom scopes. Defaults to ["openid", "email", "profile"].
    """

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'google'.
        """
        return "google"

    @property
    def authorize_url(self) -> str:
        """Return Google authorization endpoint.

        Returns:
            Google OAuth authorization URL.
        """
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        """Return Google token exchange endpoint.

        Returns:
            Google OAuth token URL.
        """
        return "https://oauth2.googleapis.com/token"

    @property
    def user_info_url(self) -> str:
        """Return Google user info endpoint.

        Returns:
            Google UserInfo endpoint URL.
        """
        return "https://www.googleapis.com/oauth2/v3/userinfo"

    def _default_scope(self) -> list[str]:
        """Return default scopes for Google OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["openid", "email", "profile"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize Google user information.

        Retrieves user profile from Google UserInfo endpoint and normalizes it
        to OAuthUserInfo format. If an id_token is available from the token response,
        it can be used to verify claims.

        Args:
            access_token: Google OAuth access token.

        Returns:
            Normalized user information.

        Raises:
            ImportError: If httpx is not installed.
            Exception: If user info fetch fails.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for Google OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=user_data.get("sub", ""),
            email=user_data.get("email", ""),
            email_verified=user_data.get("email_verified", False),
            username=user_data.get("email", ""),  # Google doesn't provide username
            first_name=user_data.get("given_name", ""),
            last_name=user_data.get("family_name", ""),
            avatar_url=user_data.get("picture", ""),
            profile_url="",  # Google doesn't provide profile URL
            raw_data=user_data,
        )
