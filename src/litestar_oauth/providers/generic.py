"""Generic OAuth2/OIDC provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class GenericOAuthProvider(BaseOAuthProvider):
    """Generic OAuth2/OIDC provider.

    Configurable provider that can work with any OAuth2 or OpenID Connect compliant
    identity provider. Supports OIDC discovery for automatic endpoint configuration.

    This provider is useful for integrating with custom OAuth providers or
    providers not explicitly supported by dedicated provider classes.

    Args:
        client_id: OAuth client ID.
        client_secret: OAuth client secret.
        authorize_url: Authorization endpoint URL.
        token_url: Token endpoint URL.
        user_info_url: UserInfo endpoint URL.
        provider_name: Unique identifier for this provider instance.
        scope: List of OAuth scopes. Defaults to ["openid", "email", "profile"].
        discovery_url: Optional OIDC discovery URL (.well-known/openid-configuration).
            If provided, endpoints will be discovered automatically.
        user_id_field: Field name in user info response containing the user ID.
            Defaults to "sub" (OIDC standard).
        email_field: Field name for email. Defaults to "email".
        email_verified_field: Field name for email verification. Defaults to "email_verified".
        username_field: Field name for username. Defaults to "preferred_username".
        first_name_field: Field name for first name. Defaults to "given_name".
        last_name_field: Field name for last name. Defaults to "family_name".
        avatar_url_field: Field name for avatar URL. Defaults to "picture".
        profile_url_field: Field name for profile URL. Defaults to "profile".

    Example::

        # Keycloak provider
        provider = GenericOAuthProvider(
            client_id="my-client",
            client_secret="secret",
            authorize_url="https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth",
            token_url="https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token",
            user_info_url="https://keycloak.example.com/realms/myrealm/protocol/openid-connect/userinfo",
            provider_name="keycloak",
            scope=["openid", "email", "profile"],
        )

        # Or using OIDC discovery
        provider = GenericOAuthProvider(
            client_id="my-client",
            client_secret="secret",
            provider_name="keycloak",
            discovery_url="https://keycloak.example.com/realms/myrealm/.well-known/openid-configuration",
        )
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorize_url: str = "",
        token_url: str = "",
        user_info_url: str = "",
        provider_name: str = "generic",
        scope: list[str] | None = None,
        discovery_url: str | None = None,
        user_id_field: str = "sub",
        email_field: str = "email",
        email_verified_field: str = "email_verified",
        username_field: str = "preferred_username",
        first_name_field: str = "given_name",
        last_name_field: str = "family_name",
        avatar_url_field: str = "picture",
        profile_url_field: str = "profile",
    ) -> None:
        """Initialize the generic OAuth provider.

        Args:
            client_id: OAuth client ID.
            client_secret: OAuth client secret.
            authorize_url: Authorization endpoint URL.
            token_url: Token endpoint URL.
            user_info_url: UserInfo endpoint URL.
            provider_name: Unique provider identifier.
            scope: List of OAuth scopes.
            discovery_url: Optional OIDC discovery URL.
            user_id_field: User ID field name.
            email_field: Email field name.
            email_verified_field: Email verified field name.
            username_field: Username field name.
            first_name_field: First name field name.
            last_name_field: Last name field name.
            avatar_url_field: Avatar URL field name.
            profile_url_field: Profile URL field name.
        """
        super().__init__(client_id, client_secret, scope)

        self._provider_name = provider_name
        self._authorize_url = authorize_url
        self._token_url = token_url
        self._user_info_url = user_info_url
        self._discovery_url = discovery_url

        # Field mappings for user info normalization
        self.user_id_field = user_id_field
        self.email_field = email_field
        self.email_verified_field = email_verified_field
        self.username_field = username_field
        self.first_name_field = first_name_field
        self.last_name_field = last_name_field
        self.avatar_url_field = avatar_url_field
        self.profile_url_field = profile_url_field

        # Discovery configuration cache
        self._discovery_config: dict[str, Any] | None = None

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name.
        """
        return self._provider_name

    @property
    def authorize_url(self) -> str:
        """Return authorization endpoint URL.

        Returns:
            Authorization URL (may be discovered via OIDC).
        """
        if self._discovery_config and not self._authorize_url:
            return self._discovery_config.get("authorization_endpoint", "")
        return self._authorize_url

    @property
    def token_url(self) -> str:
        """Return token endpoint URL.

        Returns:
            Token URL (may be discovered via OIDC).
        """
        if self._discovery_config and not self._token_url:
            return self._discovery_config.get("token_endpoint", "")
        return self._token_url

    @property
    def user_info_url(self) -> str:
        """Return user info endpoint URL.

        Returns:
            UserInfo URL (may be discovered via OIDC).
        """
        if self._discovery_config and not self._user_info_url:
            return self._discovery_config.get("userinfo_endpoint", "")
        return self._user_info_url

    def _default_scope(self) -> list[str]:
        """Return default scopes for generic OAuth.

        Returns:
            List of default OIDC scopes.
        """
        return ["openid", "email", "profile"]

    async def discover_configuration(self) -> None:
        """Discover OAuth/OIDC configuration from discovery URL.

        Fetches the .well-known/openid-configuration endpoint and caches
        the configuration for endpoint discovery.

        Raises:
            ImportError: If httpx is not installed.
            ValueError: If discovery_url is not set.
            Exception: If discovery fails.
        """
        if not self._discovery_url:
            msg = "discovery_url must be set to use OIDC discovery"
            raise ValueError(msg)

        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for OIDC discovery. Install it with: pip install httpx"
            raise ImportError(msg) from e

        async with httpx.AsyncClient() as client:
            response = await client.get(self._discovery_url)
            response.raise_for_status()
            self._discovery_config = response.json()

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize user information.

        Retrieves user profile from the configured user info endpoint and normalizes
        it using the configured field mappings.

        Args:
            access_token: OAuth access token.
            **kwargs: Additional parameters (unused).

        Returns:
            Normalized user information.

        Raises:
            ImportError: If httpx is not installed.
            ValueError: If user_info_url is not configured.
            Exception: If user info fetch fails.
        """
        # Attempt discovery if not already done and discovery_url is set
        if self._discovery_url and not self._discovery_config:
            await self.discover_configuration()

        user_info_url = self.user_info_url
        if not user_info_url:
            msg = "user_info_url must be configured or discoverable via OIDC"
            raise ValueError(msg)

        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for OAuth user info. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

        # Extract fields using configured field names with fallbacks
        def get_field(field_name: str, default: Any = None) -> Any:
            return user_data.get(field_name, default)

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(get_field(self.user_id_field, "")),
            email=get_field(self.email_field),
            email_verified=bool(get_field(self.email_verified_field, False)),
            username=get_field(self.username_field),
            first_name=get_field(self.first_name_field),
            last_name=get_field(self.last_name_field),
            avatar_url=get_field(self.avatar_url_field),
            profile_url=get_field(self.profile_url_field),
            raw_data=user_data,
        )
