"""Facebook OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class FacebookOAuthProvider(BaseOAuthProvider):
    """Facebook OAuth2 provider.

    Implements OAuth2 authentication flow for Facebook.

    Default scopes:
        - email: Access user email address
        - public_profile: Access basic profile information

    User Info Mapping:
        - oauth_id: Facebook user ID
        - email: User email address
        - email_verified: Not provided by Facebook (defaults to False)
        - username: Not provided by Facebook
        - first_name: User's first name
        - last_name: User's last name
        - avatar_url: Profile picture URL from picture.data.url
        - profile_url: Facebook profile URL

    Args:
        client_id: Facebook App ID.
        client_secret: Facebook App Secret.
        scope: Optional custom scopes. Defaults to ["email", "public_profile"].
    """

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'facebook'.
        """
        return "facebook"

    @property
    def authorize_url(self) -> str:
        """Return Facebook authorization endpoint.

        Returns:
            Facebook OAuth authorization URL.
        """
        return "https://www.facebook.com/v18.0/dialog/oauth"

    @property
    def token_url(self) -> str:
        """Return Facebook token exchange endpoint.

        Returns:
            Facebook OAuth token URL.
        """
        return "https://graph.facebook.com/v18.0/oauth/access_token"

    @property
    def user_info_url(self) -> str:
        """Return Facebook user info endpoint.

        Returns:
            Facebook Graph API user endpoint URL with requested fields.
        """
        return "https://graph.facebook.com/v18.0/me?fields=id,name,email,first_name,last_name,picture"

    def _default_scope(self) -> list[str]:
        """Return default scopes for Facebook OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["email", "public_profile"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize Facebook user information.

        Retrieves user profile from Facebook Graph API and normalizes it to OAuthUserInfo format.
        Handles Facebook's nested picture object structure.

        Args:
            access_token: Facebook OAuth access token.
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
            msg = "httpx is required for Facebook OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

        # Extract avatar URL from nested picture object
        # Facebook returns: {"picture": {"data": {"url": "...", "is_silhouette": false}}}
        avatar_url = ""
        if user_data.get("picture"):
            picture_data = user_data.get("picture", {}).get("data", {})
            avatar_url = picture_data.get("url", "")

        # Build Facebook profile URL from user ID
        user_id = user_data.get("id", "")
        profile_url = f"https://facebook.com/{user_id}" if user_id else ""

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(user_data.get("id", "")),
            email=user_data.get("email"),
            email_verified=False,  # Facebook doesn't provide email verification status
            username=None,  # Facebook doesn't provide username in API response
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            avatar_url=avatar_url,
            profile_url=profile_url,
            raw_data=user_data,
        )
