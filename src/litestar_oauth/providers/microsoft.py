"""Microsoft/Azure AD OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class MicrosoftOAuthProvider(BaseOAuthProvider):
    """Microsoft/Azure AD OAuth2 provider with OpenID Connect support.

    Implements OAuth2 authentication flow for Microsoft accounts and Azure AD.
    Supports both personal Microsoft accounts and organizational accounts.

    Default scopes:
        - openid: Required for OIDC
        - email: Access user email
        - profile: Access user profile info

    User Info Mapping:
        - oauth_id: Microsoft user ID (id field)
        - email: User email address (mail or userPrincipalName)
        - email_verified: Not provided by Microsoft (defaults to False)
        - username: User principal name
        - first_name: Given name
        - last_name: Surname
        - avatar_url: Not available (requires separate Microsoft Graph photo call)
        - profile_url: Not provided by Microsoft

    Args:
        client_id: Azure AD OAuth application client ID.
        client_secret: Azure AD OAuth application client secret.
        tenant: Azure AD tenant ID. Defaults to "common" for multi-tenant.
            Use "organizations" for any org account, "consumers" for personal accounts,
            or a specific tenant ID/domain for single-tenant.
        scope: Optional custom scopes. Defaults to ["openid", "email", "profile"].
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant: str = "common",
        scope: list[str] | None = None,
    ) -> None:
        """Initialize Microsoft OAuth provider.

        Args:
            client_id: Azure AD OAuth application client ID.
            client_secret: Azure AD OAuth application client secret.
            tenant: Azure AD tenant ID or identifier. Defaults to "common".
            scope: Optional custom scopes.
        """
        super().__init__(client_id, client_secret, scope)
        self.tenant = tenant

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'microsoft'.
        """
        return "microsoft"

    @property
    def authorize_url(self) -> str:
        """Return Microsoft authorization endpoint.

        Returns:
            Microsoft OAuth authorization URL with tenant.
        """
        return f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/authorize"

    @property
    def token_url(self) -> str:
        """Return Microsoft token exchange endpoint.

        Returns:
            Microsoft OAuth token URL with tenant.
        """
        return f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token"

    @property
    def user_info_url(self) -> str:
        """Return Microsoft Graph user info endpoint.

        Returns:
            Microsoft Graph API user endpoint URL.
        """
        return "https://graph.microsoft.com/v1.0/me"

    def _default_scope(self) -> list[str]:
        """Return default scopes for Microsoft OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["openid", "email", "profile"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize Microsoft user information.

        Retrieves user profile from Microsoft Graph API and normalizes it
        to OAuthUserInfo format. Microsoft Graph provides user data through
        the /me endpoint.

        Note: Avatar URLs are not included as they require a separate API call
        to /me/photo/$value which returns binary data rather than a URL.

        Args:
            access_token: Microsoft OAuth access token.
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
            msg = "httpx is required for Microsoft OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

        # Microsoft Graph uses 'mail' for mailbox email or 'userPrincipalName' as fallback
        # userPrincipalName is in email format for most users
        email = user_data.get("mail") or user_data.get("userPrincipalName")

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(user_data.get("id", "")),
            email=email,
            email_verified=False,  # Microsoft Graph doesn't provide email verification status
            username=user_data.get("userPrincipalName"),
            first_name=user_data.get("givenName"),
            last_name=user_data.get("surname"),
            avatar_url=None,  # Requires separate /me/photo/$value call
            profile_url=None,  # Microsoft doesn't provide profile URLs
            raw_data=user_data,
        )
