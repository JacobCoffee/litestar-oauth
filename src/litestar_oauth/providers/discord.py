"""Discord OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class DiscordOAuthProvider(BaseOAuthProvider):
    """Discord OAuth2 provider.

    Implements OAuth2 authentication flow for Discord.

    Default scopes:
        - identify: Access basic user information
        - email: Access user email address

    User Info Mapping:
        - oauth_id: Discord user ID (snowflake)
        - email: User email address
        - email_verified: Email verification status
        - username: Discord username (with discriminator if applicable)
        - first_name: Discord username (no first/last name separation)
        - last_name: Empty (Discord doesn't separate names)
        - avatar_url: Discord CDN avatar URL
        - profile_url: Not provided by Discord

    Args:
        client_id: Discord OAuth application client ID.
        client_secret: Discord OAuth application client secret.
        scope: Optional custom scopes. Defaults to ["identify", "email"].
    """

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'discord'.
        """
        return "discord"

    @property
    def authorize_url(self) -> str:
        """Return Discord authorization endpoint.

        Returns:
            Discord OAuth authorization URL.
        """
        return "https://discord.com/api/oauth2/authorize"

    @property
    def token_url(self) -> str:
        """Return Discord token exchange endpoint.

        Returns:
            Discord OAuth token URL.
        """
        return "https://discord.com/api/oauth2/token"

    @property
    def user_info_url(self) -> str:
        """Return Discord user info endpoint.

        Returns:
            Discord API user endpoint URL.
        """
        return "https://discord.com/api/users/@me"

    def _default_scope(self) -> list[str]:
        """Return default scopes for Discord OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["identify", "email"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize Discord user information.

        Retrieves user profile from Discord API and normalizes it to OAuthUserInfo format.
        Handles Discord's avatar hash and CDN URL construction.

        Args:
            access_token: Discord OAuth access token.
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
            msg = "httpx is required for Discord OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

        # Build Discord avatar URL from hash
        # Format: https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png
        avatar_url = ""
        if user_data.get("avatar"):
            user_id = user_data.get("id")
            avatar_hash = user_data.get("avatar")
            # Check if avatar is animated (hash starts with 'a_')
            extension = "gif" if avatar_hash.startswith("a_") else "png"
            avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{extension}"

        # Discord username format changed - discriminator is now optional
        username = user_data.get("username", "")
        discriminator = user_data.get("discriminator")
        if discriminator and discriminator != "0":
            username = f"{username}#{discriminator}"

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(user_data.get("id", "")),
            email=user_data.get("email"),
            email_verified=user_data.get("verified", False),
            username=username,
            first_name=user_data.get("username", ""),  # Discord only has username
            last_name="",  # Discord doesn't have separate first/last names
            avatar_url=avatar_url,
            profile_url="",  # Discord doesn't provide profile URLs via API
            raw_data=user_data,
        )
