"""GitHub OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class GitHubOAuthProvider(BaseOAuthProvider):
    """GitHub OAuth2 provider.

    Implements OAuth2 authentication flow for GitHub.

    Default scopes:
        - read:user: Read user profile data
        - user:email: Access user email addresses

    User Info Mapping:
        - oauth_id: GitHub user ID
        - email: Primary email (requires separate API call if not public)
        - username: GitHub login
        - first_name: Extracted from name field
        - last_name: Extracted from name field
        - avatar_url: GitHub avatar URL
        - profile_url: GitHub profile URL

    Args:
        client_id: GitHub OAuth App client ID.
        client_secret: GitHub OAuth App client secret.
        scope: Optional custom scopes. Defaults to ["read:user", "user:email"].
    """

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'github'.
        """
        return "github"

    @property
    def authorize_url(self) -> str:
        """Return GitHub authorization endpoint.

        Returns:
            GitHub OAuth authorization URL.
        """
        return "https://github.com/login/oauth/authorize"

    @property
    def token_url(self) -> str:
        """Return GitHub token exchange endpoint.

        Returns:
            GitHub OAuth token URL.
        """
        return "https://github.com/login/oauth/access_token"

    @property
    def user_info_url(self) -> str:
        """Return GitHub user info endpoint.

        Returns:
            GitHub API user endpoint URL.
        """
        return "https://api.github.com/user"

    def _default_scope(self) -> list[str]:
        """Return default scopes for GitHub OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["read:user", "user:email"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize GitHub user information.

        Retrieves user profile from GitHub API and normalizes it to OAuthUserInfo format.
        If the primary email is not public, makes an additional API call to fetch it.

        Args:
            access_token: GitHub OAuth access token.

        Returns:
            Normalized user information.

        Raises:
            ImportError: If httpx is not installed.
            Exception: If user info fetch fails.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for GitHub OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient() as client:
            # Fetch user profile
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

            # Fetch email if not public in profile
            email = user_data.get("email")
            email_verified = False

            if not email:
                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers=headers,
                )
                email_response.raise_for_status()
                emails = email_response.json()

                # Find primary verified email
                for email_data in emails:
                    if email_data.get("primary"):
                        email = email_data.get("email")
                        email_verified = email_data.get("verified", False)
                        break

                # Fallback to first verified email
                if not email:
                    for email_data in emails:
                        if email_data.get("verified"):
                            email = email_data.get("email")
                            email_verified = True
                            break

                # Last resort: first email
                if not email and emails:
                    email = emails[0].get("email")
                    email_verified = emails[0].get("verified", False)

        # Parse name into first and last name
        name = user_data.get("name", "")
        first_name = ""
        last_name = ""

        if name:
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(user_data["id"]),
            email=email or "",
            email_verified=email_verified,
            username=user_data.get("login", ""),
            first_name=first_name,
            last_name=last_name,
            avatar_url=user_data.get("avatar_url", ""),
            profile_url=user_data.get("html_url", ""),
            raw_data=user_data,
        )
