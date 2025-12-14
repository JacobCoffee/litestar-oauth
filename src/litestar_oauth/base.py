"""Base classes and protocols for OAuth2 providers.

This module defines the provider interface and base implementation that all
OAuth2 providers must follow, ensuring consistent behavior across different providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from litestar_oauth.types import OAuthToken, OAuthUserInfo

__all__ = (
    "BaseOAuthProvider",
    "OAuthProvider",
)


@runtime_checkable
class OAuthProvider(Protocol):
    """Protocol defining the interface for OAuth2 providers.

    All OAuth providers must implement this interface to be compatible with
    the OAuthService. This protocol ensures type safety and consistent behavior.
    """

    @property
    def provider_name(self) -> str:
        """Unique identifier for this provider (e.g., 'google', 'github')."""
        ...

    @property
    def authorize_url(self) -> str:
        """URL where users are redirected to authorize the application."""
        ...

    @property
    def token_url(self) -> str:
        """URL for exchanging authorization codes for access tokens."""
        ...

    @property
    def user_info_url(self) -> str:
        """URL for retrieving user profile information."""
        ...

    @property
    def scope(self) -> list[str]:
        """List of OAuth scopes requested from the provider."""
        ...

    def is_configured(self) -> bool:
        """Check if the provider has all required configuration.

        Returns:
            True if the provider is properly configured and ready to use.
        """
        ...

    async def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        **kwargs: Any,
    ) -> str:
        """Generate the URL to redirect users for authorization.

        Args:
            redirect_uri: URI where the provider should redirect after authorization.
            state: CSRF protection state parameter.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Complete authorization URL with all required parameters.
        """
        ...

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        **kwargs: Any,
    ) -> OAuthToken:
        """Exchange an authorization code for an access token.

        Args:
            code: Authorization code received from the provider.
            redirect_uri: Redirect URI used in the authorization request.
            **kwargs: Additional provider-specific parameters.

        Returns:
            OAuth token containing access token and metadata.

        Raises:
            TokenExchangeError: If the code exchange fails.
        """
        ...

    async def refresh_token(
        self,
        refresh_token: str,
        **kwargs: Any,
    ) -> OAuthToken:
        """Use a refresh token to obtain a new access token.

        Args:
            refresh_token: The refresh token from a previous token response.
            **kwargs: Additional provider-specific parameters.

        Returns:
            New OAuth token with fresh access token.

        Raises:
            TokenRefreshError: If token refresh fails.
        """
        ...

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Retrieve user information using an access token.

        Args:
            access_token: Valid access token from the provider.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Structured user information from the provider.

        Raises:
            UserInfoError: If fetching user info fails.
        """
        ...

    async def revoke_token(
        self,
        token: str,
        token_type_hint: str | None = None,
        **kwargs: Any,
    ) -> bool:
        """Revoke an access or refresh token.

        Args:
            token: The token to revoke.
            token_type_hint: Optional hint about token type ('access_token' or 'refresh_token').
            **kwargs: Additional provider-specific parameters.

        Returns:
            True if revocation succeeded, False otherwise.
        """
        ...


class BaseOAuthProvider(ABC):
    """Abstract base class providing common OAuth2 provider functionality.

    This class implements shared logic for OAuth providers, reducing duplication
    and ensuring consistent behavior. Concrete providers should inherit from this
    class and implement the abstract methods.

    Attributes:
        client_id: OAuth2 client identifier.
        client_secret: OAuth2 client secret.
        _scope: List of OAuth scopes to request.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: list[str] | None = None,
    ) -> None:
        """Initialize the OAuth provider with credentials.

        Args:
            client_id: OAuth2 client identifier from the provider.
            client_secret: OAuth2 client secret from the provider.
            scope: List of OAuth scopes to request. Defaults to provider-specific scopes.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._scope = scope or self._default_scope()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    @abstractmethod
    def authorize_url(self) -> str:
        """Provider's authorization endpoint URL."""
        ...

    @property
    @abstractmethod
    def token_url(self) -> str:
        """Provider's token endpoint URL."""
        ...

    @property
    @abstractmethod
    def user_info_url(self) -> str:
        """Provider's user info endpoint URL."""
        ...

    @property
    def scope(self) -> list[str]:
        """List of OAuth scopes to request."""
        return self._scope

    def is_configured(self) -> bool:
        """Check if the provider has required configuration.

        Returns:
            True if client_id and client_secret are set.
        """
        return bool(self.client_id and self.client_secret)

    @abstractmethod
    def _default_scope(self) -> list[str]:
        """Get default scopes for this provider.

        Returns:
            List of default OAuth scopes for this provider.
        """
        ...

    async def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        **kwargs: Any,
    ) -> str:
        """Generate authorization URL.

        Args:
            redirect_uri: Callback URI for the OAuth flow.
            state: CSRF protection state parameter.
            **kwargs: Provider-specific parameters (e.g., scope, extra_params).

        Returns:
            Complete authorization URL.
        """
        from urllib.parse import urlencode

        # Allow scope override via kwargs
        scope = kwargs.pop("scope", None) or " ".join(self.scope)
        extra_params = kwargs.pop("extra_params", {})

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "response_type": "code",
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
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from provider.
            redirect_uri: Redirect URI used in authorization.
            **kwargs: Provider-specific parameters.

        Returns:
            OAuth token with access token and metadata.

        Raises:
            TokenExchangeError: If exchange fails.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for OAuth2 token exchange. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.exceptions import TokenExchangeError

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Accept": "application/json"},
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
            id_token=data.get("id_token"),
            raw_response=data,
        )

    async def refresh_token(
        self,
        refresh_token: str,
        **kwargs: Any,
    ) -> OAuthToken:
        """Refresh an access token.

        Args:
            refresh_token: Refresh token from previous response.
            **kwargs: Provider-specific parameters.

        Returns:
            New OAuth token.

        Raises:
            TokenRefreshError: If refresh fails.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for OAuth2 token refresh. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.exceptions import TokenRefreshError

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            raise TokenRefreshError(f"Failed to refresh token: {e}") from e

        return OAuthToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in"),
            refresh_token=data.get("refresh_token", refresh_token),
            scope=data.get("scope"),
            id_token=data.get("id_token"),
            raw_response=data,
        )

    @abstractmethod
    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch user information.

        Args:
            access_token: Valid access token.
            **kwargs: Provider-specific parameters.

        Returns:
            User information from provider.

        Raises:
            UserInfoError: If fetching fails.
        """
        ...

    async def revoke_token(
        self,
        token: str,
        token_type_hint: str | None = None,
        **kwargs: Any,
    ) -> bool:
        """Revoke a token.

        Default implementation returns False. Providers should override if they
        support token revocation.

        Args:
            token: Token to revoke.
            token_type_hint: Type of token being revoked.
            **kwargs: Provider-specific parameters.

        Returns:
            True if revocation succeeded.
        """
        return False
