"""GitLab OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class GitLabOAuthProvider(BaseOAuthProvider):
    """GitLab OAuth2 provider.

    Implements OAuth2 authentication flow for GitLab (both gitlab.com and self-hosted instances).

    Default scopes:
        - read_user: Read user profile data
        - email: Access user email address

    User Info Mapping:
        - oauth_id: GitLab user ID
        - email: User email address
        - username: GitLab username
        - first_name: Extracted from name field (first word)
        - last_name: Extracted from name field (remaining words)
        - avatar_url: GitLab avatar URL
        - profile_url: GitLab profile URL (web_url)

    Args:
        client_id: GitLab OAuth application client ID.
        client_secret: GitLab OAuth application client secret.
        scope: Optional custom scopes. Defaults to ["read_user", "email"].
        base_url: Base URL for GitLab instance. Defaults to "https://gitlab.com" for GitLab.com.
            Use "https://gitlab.example.com" for self-hosted instances.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: list[str] | None = None,
        base_url: str = "https://gitlab.com",
    ) -> None:
        """Initialize the GitLab OAuth provider.

        Args:
            client_id: GitLab OAuth application client ID.
            client_secret: GitLab OAuth application client secret.
            scope: Optional custom scopes. Defaults to ["read_user", "email"].
            base_url: Base URL for GitLab instance. Defaults to "https://gitlab.com".
        """
        super().__init__(client_id, client_secret, scope)
        self.base_url = base_url.rstrip("/")

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'gitlab'.
        """
        return "gitlab"

    @property
    def authorize_url(self) -> str:
        """Return GitLab authorization endpoint.

        Returns:
            GitLab OAuth authorization URL.
        """
        return f"{self.base_url}/oauth/authorize"

    @property
    def token_url(self) -> str:
        """Return GitLab token exchange endpoint.

        Returns:
            GitLab OAuth token URL.
        """
        return f"{self.base_url}/oauth/token"

    @property
    def user_info_url(self) -> str:
        """Return GitLab user info endpoint.

        Returns:
            GitLab API user endpoint URL.
        """
        return f"{self.base_url}/api/v4/user"

    def _default_scope(self) -> list[str]:
        """Return default scopes for GitLab OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["read_user", "email"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize GitLab user information.

        Retrieves user profile from GitLab API and normalizes it to OAuthUserInfo format.

        Args:
            access_token: GitLab OAuth access token.
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
            msg = "httpx is required for GitLab OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

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
            email=user_data.get("email", ""),
            email_verified=user_data.get("confirmed_at") is not None,
            username=user_data.get("username", ""),
            first_name=first_name,
            last_name=last_name,
            avatar_url=user_data.get("avatar_url", ""),
            profile_url=user_data.get("web_url", ""),
            raw_data=user_data,
        )
