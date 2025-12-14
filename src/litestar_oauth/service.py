"""OAuth2 service for managing providers and state.

This module provides the central OAuthService class that coordinates OAuth
providers, manages state for security, and provides a high-level API for
OAuth operations.
"""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from litestar_oauth.exceptions import ExpiredStateError, InvalidStateError, ProviderNotConfiguredError
from litestar_oauth.types import OAuthState

if TYPE_CHECKING:
    from litestar_oauth.base import OAuthProvider

__all__ = (
    "OAuthService",
    "OAuthStateManager",
)


class OAuthStateManager:
    """In-memory state manager for OAuth2 CSRF protection.

    This manager generates, stores, and validates state tokens used in OAuth
    flows to prevent CSRF attacks. States are stored in memory with a TTL.

    Attributes:
        default_ttl: Default time-to-live for state tokens in seconds.
    """

    def __init__(self, default_ttl: int = 600) -> None:
        """Initialize the state manager.

        Args:
            default_ttl: Default lifetime for state tokens in seconds. Defaults to 600 (10 minutes).
        """
        self.default_ttl = default_ttl
        self._states: dict[str, OAuthState] = {}

    def generate_state(
        self,
        provider: str,
        redirect_uri: str,
        next_url: str | None = None,
        extra_data: dict[str, Any] | None = None,
        ttl: int | None = None,
    ) -> OAuthState:
        """Generate a new OAuth state token.

        Args:
            provider: Name of the OAuth provider.
            redirect_uri: URI for OAuth callback.
            next_url: Optional URL to redirect to after authentication.
            extra_data: Optional additional data to store with state.
            ttl: Optional custom TTL for this state in seconds.

        Returns:
            Generated OAuth state object.
        """
        state_string = secrets.token_urlsafe(32)
        oauth_state = OAuthState(
            state=state_string,
            provider=provider,
            redirect_uri=redirect_uri,
            next_url=next_url,
            extra_data=extra_data or {},
        )
        self._states[state_string] = oauth_state

        # Schedule cleanup for expired states
        if ttl is None:
            ttl = self.default_ttl
        # Note: In production, consider using a background task or cache with TTL
        # This is a simple in-memory implementation

        return oauth_state

    def validate_state(self, state: str, provider: str | None = None) -> OAuthState:
        """Validate and retrieve an OAuth state.

        Args:
            state: State string to validate.
            provider: Optional provider name to verify against.

        Returns:
            The validated OAuth state object.

        Raises:
            InvalidStateError: If state is not found or provider doesn't match.
            ExpiredStateError: If state has exceeded its TTL.
        """
        oauth_state = self._states.get(state)
        if oauth_state is None:
            raise InvalidStateError(f"State not found: {state}")

        # Check expiration
        age = datetime.now(timezone.utc) - oauth_state.created_at
        if age.total_seconds() > self.default_ttl:
            self._states.pop(state, None)
            raise ExpiredStateError(f"State has expired: {state}")

        # Verify provider if specified
        if provider is not None and oauth_state.provider != provider:
            raise InvalidStateError(f"Provider mismatch: expected {provider}, got {oauth_state.provider}")

        return oauth_state

    def consume_state(self, state: str, provider: str | None = None) -> OAuthState:
        """Validate and remove an OAuth state (one-time use).

        Args:
            state: State string to consume.
            provider: Optional provider name to verify against.

        Returns:
            The validated OAuth state object.

        Raises:
            InvalidStateError: If state is not found or provider doesn't match.
            ExpiredStateError: If state has exceeded its TTL.
        """
        oauth_state = self.validate_state(state, provider)
        self._states.pop(state, None)
        return oauth_state

    def cleanup_expired(self) -> int:
        """Remove all expired states from storage.

        Returns:
            Number of expired states removed.
        """
        now = datetime.now(timezone.utc)
        expired_states = [
            state_str
            for state_str, oauth_state in self._states.items()
            if (now - oauth_state.created_at).total_seconds() > self.default_ttl
        ]

        for state_str in expired_states:
            self._states.pop(state_str, None)

        return len(expired_states)

    def clear(self) -> None:
        """Remove all states from storage.

        This is primarily useful for testing or application shutdown.
        """
        self._states.clear()


class OAuthService:
    """Central service for OAuth2 provider management and operations.

    This service manages multiple OAuth providers, handles state management for
    security, and provides a unified API for OAuth operations.

    Attributes:
        providers: Registry of configured OAuth providers.
        state_manager: Manager for OAuth state tokens.
    """

    def __init__(
        self,
        providers: Mapping[str, OAuthProvider] | None = None,
        state_manager: OAuthStateManager | None = None,
    ) -> None:
        """Initialize the OAuth service.

        Args:
            providers: Optional mapping of provider names to provider instances.
            state_manager: Optional custom state manager. If not provided, uses default.
        """
        self.providers: dict[str, OAuthProvider] = dict(providers) if providers else {}
        self.state_manager = state_manager or OAuthStateManager()

    def register(self, provider: OAuthProvider) -> None:
        """Register an OAuth provider with the service.

        Args:
            provider: Provider instance to register.

        Raises:
            ValueError: If a provider with the same name is already registered.
        """
        if provider.provider_name in self.providers:
            raise ValueError(f"Provider '{provider.provider_name}' is already registered")

        self.providers[provider.provider_name] = provider

    def get_provider(self, provider_name: str) -> OAuthProvider:
        """Retrieve a registered OAuth provider.

        Args:
            provider_name: Name of the provider to retrieve.

        Returns:
            The requested OAuth provider instance.

        Raises:
            ProviderNotConfiguredError: If the provider is not registered.
        """
        provider = self.providers.get(provider_name)
        if provider is None:
            raise ProviderNotConfiguredError(
                f"Provider '{provider_name}' is not configured. Available providers: {', '.join(self.list_providers())}"
            )

        if not provider.is_configured():
            raise ProviderNotConfiguredError(f"Provider '{provider_name}' is registered but not properly configured")

        return provider

    def list_providers(self) -> list[str]:
        """Get names of all registered providers.

        Returns:
            List of provider names currently registered.
        """
        return list(self.providers.keys())

    async def get_authorization_url(
        self,
        provider_name: str,
        redirect_uri: str,
        next_url: str | None = None,
        extra_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate an authorization URL for a provider.

        This is the first step in the OAuth flow. The generated URL includes a
        secure state parameter for CSRF protection.

        Args:
            provider_name: Name of the OAuth provider to use.
            redirect_uri: URI where the provider should redirect after authorization.
            next_url: Optional URL to redirect to after successful authentication.
            extra_data: Optional additional data to preserve across the OAuth flow.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Complete authorization URL to redirect the user to.

        Raises:
            ProviderNotConfiguredError: If the provider is not available.
        """
        provider = self.get_provider(provider_name)

        # Generate and store state
        oauth_state = self.state_manager.generate_state(
            provider=provider_name,
            redirect_uri=redirect_uri,
            next_url=next_url,
            extra_data=extra_data,
        )

        # Get authorization URL from provider
        return await provider.get_authorization_url(
            redirect_uri=redirect_uri,
            state=oauth_state.state,
            **kwargs,
        )

    @classmethod
    def from_config(
        cls,
        providers_config: Mapping[str, Mapping[str, Any]],
        provider_classes: Mapping[str, type[OAuthProvider]],
        state_ttl: int = 600,
    ) -> OAuthService:
        """Create an OAuthService from configuration dictionaries.

        This factory method simplifies service setup when configuration comes
        from files, environment variables, or other sources.

        Args:
            providers_config: Mapping of provider names to their configuration.
                Each config should include 'client_id', 'client_secret', and optional 'scope'.
            provider_classes: Mapping of provider names to their implementation classes.
            state_ttl: Time-to-live for state tokens in seconds.

        Returns:
            Configured OAuthService instance.

        Example::

            from litestar_oauth.providers import GoogleProvider, GitHubProvider

            config = {
                "google": {
                    "client_id": "your-client-id",
                    "client_secret": "your-secret",
                    "scope": ["openid", "email", "profile"],
                },
                "github": {
                    "client_id": "your-client-id",
                    "client_secret": "your-secret",
                },
            }

            classes = {
                "google": GoogleProvider,
                "github": GitHubProvider,
            }

            service = OAuthService.from_config(config, classes)
        """
        providers: dict[str, OAuthProvider] = {}

        for provider_name, provider_config in providers_config.items():
            if provider_name not in provider_classes:
                continue

            provider_class = provider_classes[provider_name]
            providers[provider_name] = provider_class(**provider_config)

        state_manager = OAuthStateManager(default_ttl=state_ttl)
        return cls(providers=providers, state_manager=state_manager)
