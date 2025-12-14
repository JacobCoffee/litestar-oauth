"""LinkedIn OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class LinkedInOAuthProvider(BaseOAuthProvider):
    """LinkedIn OAuth2 provider with OpenID Connect support.

    Implements OAuth2 authentication flow for LinkedIn accounts.
    Supports OpenID Connect (OIDC) for enhanced authentication.

    Default scopes:
        - openid: Required for OIDC
        - profile: Access user profile info
        - email: Access user email

    User Info Mapping:
        - oauth_id: LinkedIn user ID (sub claim)
        - email: User email address
        - email_verified: Email verification status
        - username: Not provided by LinkedIn
        - first_name: Given name
        - last_name: Family name
        - avatar_url: Profile picture URL
        - profile_url: Not provided by LinkedIn

    Args:
        client_id: LinkedIn OAuth client ID.
        client_secret: LinkedIn OAuth client secret.
        scope: Optional custom scopes. Defaults to ["openid", "profile", "email"].
    """

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'linkedin'.
        """
        return "linkedin"

    @property
    def authorize_url(self) -> str:
        """Return LinkedIn authorization endpoint.

        Returns:
            LinkedIn OAuth authorization URL.
        """
        return "https://www.linkedin.com/oauth/v2/authorization"

    @property
    def token_url(self) -> str:
        """Return LinkedIn token exchange endpoint.

        Returns:
            LinkedIn OAuth token URL.
        """
        return "https://www.linkedin.com/oauth/v2/accessToken"

    @property
    def user_info_url(self) -> str:
        """Return LinkedIn user info endpoint.

        Returns:
            LinkedIn UserInfo endpoint URL.
        """
        return "https://api.linkedin.com/v2/userinfo"

    def _default_scope(self) -> list[str]:
        """Return default scopes for LinkedIn OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["openid", "profile", "email"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize LinkedIn user information.

        Retrieves user profile from LinkedIn UserInfo endpoint and normalizes it
        to OAuthUserInfo format. LinkedIn's OIDC implementation provides standard
        claims including sub, email, given_name, family_name, and picture.

        Args:
            access_token: LinkedIn OAuth access token.
            **kwargs: Additional parameters (unused).

        Returns:
            Normalized user information.

        Raises:
            ImportError: If httpx is not installed.
            Exception: If user info fetch fails.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for LinkedIn OAuth. Install it with: pip install httpx"
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
            username=None,  # LinkedIn doesn't provide username
            first_name=user_data.get("given_name", ""),
            last_name=user_data.get("family_name", ""),
            avatar_url=user_data.get("picture", ""),
            profile_url=None,  # LinkedIn doesn't provide profile URL via OIDC
            raw_data=user_data,
        )
