"""Mock implementations for testing OAuth providers and services.

This module provides configurable mock objects that can be used in tests to simulate
OAuth provider behavior without making actual HTTP requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass
class MockHTTPResponse:
    """Mock HTTP response for testing OAuth provider HTTP interactions.

    This class simulates httpx.Response objects with configurable status codes,
    headers, and response bodies.

    Args:
        status_code: HTTP status code (default: 200)
        headers: Response headers (default: empty dict)
        json_data: JSON response body (default: empty dict)
        text_data: Text response body (default: empty string)
        content: Raw bytes response body (default: empty bytes)

    Example:
        >>> response = MockHTTPResponse(status_code=200, json_data={"access_token": "mock_token"})
        >>> assert response.json() == {"access_token": "mock_token"}
    """

    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    json_data: dict[str, Any] = field(default_factory=dict)
    text_data: str = ""
    content: bytes = b""

    def json(self) -> dict[str, Any]:
        """Return JSON response data."""
        return self.json_data

    def text(self) -> str:
        """Return text response data."""
        return self.text_data

    def raise_for_status(self) -> None:
        """Raise exception if status code indicates error."""
        if self.status_code >= 400:
            msg = f"HTTP {self.status_code}"
            raise Exception(msg)


@dataclass
class MockOAuthProvider:
    """Configurable mock OAuth provider for testing.

    This mock implements the OAuthProvider protocol and can be configured to return
    specific responses for testing different OAuth flow scenarios.

    Args:
        provider_name: Provider identifier (default: "mock")
        authorize_url: Authorization endpoint URL
        token_url: Token exchange endpoint URL
        user_info_url: User info endpoint URL
        scope: OAuth scopes to request
        configured: Whether provider has valid configuration
        access_token: Mock access token to return
        refresh_token: Mock refresh token to return
        user_info: Mock user info to return
        raise_on_exchange: If True, raise exception during code exchange
        raise_on_refresh: If True, raise exception during token refresh
        raise_on_user_info: If True, raise exception when fetching user info

    Example:
        >>> from litestar_oauth.types import OAuthUserInfo
        >>> provider = MockOAuthProvider(
        ...     provider_name="github",
        ...     access_token="gho_mock_token",
        ...     user_info=OAuthUserInfo(
        ...         provider="github",
        ...         oauth_id="12345",
        ...         email="test@example.com",
        ...     ),
        ... )
        >>> url = provider.get_authorization_url("http://localhost/callback", "state123")
        >>> assert "state=state123" in url
    """

    provider_name: str = "mock"
    authorize_url: str = "https://oauth.mock/authorize"
    token_url: str = "https://oauth.mock/token"
    user_info_url: str = "https://oauth.mock/userinfo"
    scope: str = "user:email"
    configured: bool = True
    access_token: str = "mock_access_token"
    mock_refresh_token: str | None = "mock_refresh_token"
    user_info: Any = None  # Should be OAuthUserInfo but avoiding import
    raise_on_exchange: bool = False
    raise_on_refresh: bool = False
    raise_on_user_info: bool = False
    _http_client: AsyncMock | None = None

    def is_configured(self) -> bool:
        """Check if provider is configured with required credentials."""
        return self.configured

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        *,
        scope: str | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> str:
        """Generate OAuth authorization URL.

        Args:
            redirect_uri: Callback URL after authorization
            state: CSRF protection token
            scope: Optional custom scopes (defaults to provider scope)
            extra_params: Additional query parameters

        Returns:
            Full authorization URL with query parameters
        """
        params = {
            "client_id": "mock_client_id",
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": scope or self.scope,
            "response_type": "code",
        }

        if extra_params:
            params.update(extra_params)

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorize_url}?{query_string}"

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> Any:  # Should return OAuthToken
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Callback URL (must match initial request)

        Returns:
            OAuthToken with access token and optional refresh token

        Raises:
            Exception: If raise_on_exchange is True
        """
        if self.raise_on_exchange:
            msg = "Mock token exchange failure"
            raise Exception(msg)

        # Import here to avoid circular dependency
        from datetime import datetime, timezone

        # Dynamically import OAuthToken to avoid circular imports
        # In real tests, this would be imported at module level
        token_data = {
            "access_token": self.access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": self.mock_refresh_token,
            "scope": self.scope,
            "raw_response": {
                "access_token": self.access_token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "created_at": int(datetime.now(timezone.utc).timestamp()),
            },
        }

        # Create a simple object with the expected attributes
        class MockToken:
            def __init__(self, data: dict[str, Any]) -> None:
                self.access_token = data["access_token"]
                self.token_type = data["token_type"]
                self.expires_in = data["expires_in"]
                self.refresh_token = data.get("refresh_token")
                self.scope = data.get("scope")
                self.id_token = data.get("id_token")
                self.raw_response = data.get("raw_response", {})

        return MockToken(token_data)

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> Any:  # Should return OAuthToken
        """Refresh an expired access token.

        Args:
            refresh_token: Refresh token from original token exchange

        Returns:
            OAuthToken with new access token

        Raises:
            Exception: If raise_on_refresh is True
        """
        if self.raise_on_refresh:
            msg = "Mock token refresh failure"
            raise Exception(msg)

        return await self.exchange_code("refresh_code", "http://mock/callback")

    async def get_user_info(
        self,
        access_token: str,
    ) -> Any:  # Should return OAuthUserInfo
        """Fetch user profile information.

        Args:
            access_token: Valid OAuth access token

        Returns:
            OAuthUserInfo with user profile data

        Raises:
            Exception: If raise_on_user_info is True
        """
        if self.raise_on_user_info:
            msg = "Mock user info fetch failure"
            raise Exception(msg)

        if self.user_info:
            return self.user_info

        # Return default mock user info
        class MockUserInfo:
            def __init__(self) -> None:
                self.provider = "mock"
                self.oauth_id = "mock_user_123"
                self.email = "mock@example.com"
                self.email_verified = True
                self.username = "mockuser"
                self.first_name = "Mock"
                self.last_name = "User"
                self.avatar_url = "https://example.com/avatar.jpg"
                self.profile_url = "https://example.com/mockuser"
                self.raw_data = {}

        return MockUserInfo()

    async def revoke_token(
        self,
        token: str,
        *,
        token_type_hint: str = "access_token",
    ) -> None:
        """Revoke an access or refresh token.

        Args:
            token: Token to revoke
            token_type_hint: Type of token (access_token or refresh_token)
        """
        # Mock implementation does nothing


class MockOAuthService:
    """Pre-configured mock OAuth service for testing.

    This class provides a complete mock OAuth service with state management
    and provider registration capabilities for integration testing.

    Args:
        providers: Optional mapping of provider names to MockOAuthProvider instances

    Example:
        >>> from litestar_oauth.testing.mocks import MockOAuthService
        >>> service = MockOAuthService()
        >>> await service.register_mock_provider("github")
        >>> state = await service.create_state("github", "http://localhost/callback")
        >>> assert state is not None
    """

    def __init__(
        self,
        providers: Mapping[str, MockOAuthProvider] | None = None,
    ) -> None:
        """Initialize mock OAuth service."""
        self._providers: dict[str, MockOAuthProvider] = dict(providers) if providers else {}
        self._states: dict[str, dict[str, Any]] = {}

    def register(self, provider: MockOAuthProvider) -> None:
        """Register a mock OAuth provider.

        Args:
            provider: MockOAuthProvider instance to register
        """
        self._providers[provider.provider_name] = provider

    def get_provider(self, provider_name: str) -> MockOAuthProvider | None:
        """Get a registered provider by name.

        Args:
            provider_name: Name of the provider to retrieve

        Returns:
            MockOAuthProvider instance or None if not found
        """
        return self._providers.get(provider_name)

    async def create_state(
        self,
        provider: str,
        redirect_uri: str,
        *,
        next_url: str | None = None,
        ttl: int = 600,
    ) -> str:
        """Create a new OAuth state token.

        Args:
            provider: Provider name for this state
            redirect_uri: Callback URL
            next_url: Optional URL to redirect to after OAuth flow
            ttl: Time-to-live in seconds (ignored in mock)

        Returns:
            State token string
        """
        import secrets

        state = secrets.token_urlsafe(32)
        self._states[state] = {
            "provider": provider,
            "redirect_uri": redirect_uri,
            "next_url": next_url,
            "created_at": "2024-01-01T00:00:00Z",
        }
        return state

    async def validate_state(self, state: str) -> dict[str, Any] | None:
        """Validate and consume a state token.

        Args:
            state: State token to validate

        Returns:
            State data dict or None if invalid
        """
        return self._states.pop(state, None)

    async def exchange_code(
        self,
        provider_name: str,
        code: str,
        redirect_uri: str,
    ) -> Any:  # Should return OAuthToken
        """Exchange authorization code for access token.

        Args:
            provider_name: Name of the OAuth provider
            code: Authorization code from callback
            redirect_uri: Callback URL (must match initial request)

        Returns:
            OAuthToken from provider

        Raises:
            ValueError: If provider not found
        """
        provider = self.get_provider(provider_name)
        if not provider:
            msg = f"Provider {provider_name} not registered"
            raise ValueError(msg)

        return await provider.exchange_code(code, redirect_uri)

    async def get_user_info(
        self,
        provider_name: str,
        access_token: str,
    ) -> Any:  # Should return OAuthUserInfo
        """Fetch user information from provider.

        Args:
            provider_name: Name of the OAuth provider
            access_token: Valid access token

        Returns:
            OAuthUserInfo from provider

        Raises:
            ValueError: If provider not found
        """
        provider = self.get_provider(provider_name)
        if not provider:
            msg = f"Provider {provider_name} not registered"
            raise ValueError(msg)

        return await provider.get_user_info(access_token)

    async def register_mock_provider(
        self,
        provider_name: str,
        **kwargs: Any,
    ) -> MockOAuthProvider:
        """Convenience method to create and register a mock provider.

        Args:
            provider_name: Name for the provider
            **kwargs: Additional arguments for MockOAuthProvider

        Returns:
            Created and registered MockOAuthProvider instance
        """
        provider = MockOAuthProvider(provider_name=provider_name, **kwargs)
        self.register(provider)
        return provider


__all__ = [
    "MockHTTPResponse",
    "MockOAuthProvider",
    "MockOAuthService",
]
