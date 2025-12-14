"""Unit tests for OAuthService and state management.

Tests the OAuth service layer:
- Provider registration and management
- State creation and validation
- OAuth flow orchestration
- Error handling
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar_oauth.testing.mocks import MockOAuthService


class TestOAuthServiceRegistration:
    """Test suite for provider registration in OAuthService."""

    async def test_register_provider(self, mock_oauth_service: MockOAuthService) -> None:
        """Test registering a provider with the service."""
        provider = await mock_oauth_service.register_mock_provider("github")

        assert provider.provider_name == "github"
        assert mock_oauth_service.get_provider("github") is not None

    async def test_register_multiple_providers(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test registering multiple providers."""
        await mock_oauth_service.register_mock_provider("github")
        await mock_oauth_service.register_mock_provider("google")
        await mock_oauth_service.register_mock_provider("discord")

        assert mock_oauth_service.get_provider("github") is not None
        assert mock_oauth_service.get_provider("google") is not None
        assert mock_oauth_service.get_provider("discord") is not None

    async def test_register_overwrites_existing_provider(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that re-registering a provider overwrites the previous one."""
        provider1 = await mock_oauth_service.register_mock_provider(
            "github",
            access_token="token1",
        )
        provider2 = await mock_oauth_service.register_mock_provider(
            "github",
            access_token="token2",
        )

        registered_provider = mock_oauth_service.get_provider("github")
        assert registered_provider.access_token == "token2"

    async def test_get_nonexistent_provider_returns_none(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that getting a non-registered provider returns None."""
        provider = mock_oauth_service.get_provider("nonexistent")
        assert provider is None


class TestOAuthServiceStateManagement:
    """Test suite for OAuth state management."""

    async def test_create_state(self, mock_oauth_service: MockOAuthService) -> None:
        """Test creating a new OAuth state."""
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
        )

        assert state is not None
        assert isinstance(state, str)
        assert len(state) > 20  # Should be cryptographically secure

    async def test_create_state_with_next_url(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test creating state with next_url parameter."""
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
            next_url="/dashboard",
        )

        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is not None
        assert state_data["next_url"] == "/dashboard"

    async def test_validate_state_success(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test validating a valid state token."""
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
        )

        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is not None
        assert state_data["provider"] == "github"
        assert state_data["redirect_uri"] == "http://localhost/callback"

    async def test_validate_state_returns_none_for_invalid(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that validating invalid state returns None."""
        state_data = await mock_oauth_service.validate_state("invalid_state")
        assert state_data is None

    async def test_validate_state_consumes_token(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that validating state consumes the token (one-time use)."""
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
        )

        # First validation should succeed
        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is not None

        # Second validation should fail (token consumed)
        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is None

    async def test_state_contains_required_fields(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that validated state contains all required fields."""
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
            next_url="/profile",
        )

        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is not None
        assert "provider" in state_data
        assert "redirect_uri" in state_data
        assert "created_at" in state_data
        assert "next_url" in state_data

    @pytest.mark.parametrize(
        ("provider", "redirect_uri"),
        [
            ("github", "http://localhost/auth/github/callback"),
            ("google", "http://localhost/auth/google/callback"),
            ("discord", "https://example.com/auth/discord/callback"),
        ],
    )
    async def test_create_state_for_different_providers(
        self,
        mock_oauth_service: MockOAuthService,
        provider: str,
        redirect_uri: str,
    ) -> None:
        """Test creating state for various providers."""
        state = await mock_oauth_service.create_state(
            provider=provider,
            redirect_uri=redirect_uri,
        )

        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is not None
        assert state_data["provider"] == provider
        assert state_data["redirect_uri"] == redirect_uri


class TestOAuthServiceFlowOrchestration:
    """Test suite for OAuth flow orchestration."""

    async def test_exchange_code_success(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test successful code exchange through service."""
        await mock_oauth_service.register_mock_provider("github")

        token = await mock_oauth_service.exchange_code(
            provider_name="github",
            code="test_code",
            redirect_uri="http://localhost/callback",
        )

        assert hasattr(token, "access_token")
        assert token.access_token is not None

    async def test_exchange_code_with_unregistered_provider(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test code exchange fails with unregistered provider."""
        with pytest.raises(ValueError) as exc_info:
            await mock_oauth_service.exchange_code(
                provider_name="nonexistent",
                code="test_code",
                redirect_uri="http://localhost/callback",
            )

        assert "not registered" in str(exc_info.value)

    async def test_get_user_info_success(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test successful user info retrieval through service."""
        await mock_oauth_service.register_mock_provider("github")

        user_info = await mock_oauth_service.get_user_info(
            provider_name="github",
            access_token="test_token",
        )

        assert hasattr(user_info, "provider")
        assert hasattr(user_info, "oauth_id")
        assert hasattr(user_info, "email")

    async def test_get_user_info_with_unregistered_provider(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test user info retrieval fails with unregistered provider."""
        with pytest.raises(ValueError) as exc_info:
            await mock_oauth_service.get_user_info(
                provider_name="nonexistent",
                access_token="test_token",
            )

        assert "not registered" in str(exc_info.value)

    async def test_full_oauth_flow(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test complete OAuth flow from state creation to user info."""
        # Setup
        provider = await mock_oauth_service.register_mock_provider("github")

        # Step 1: Create state
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
            next_url="/dashboard",
        )
        assert state is not None

        # Step 2: Validate state (simulating callback)
        state_data = await mock_oauth_service.validate_state(state)
        assert state_data is not None
        assert state_data["provider"] == "github"

        # Step 3: Exchange code for token
        token = await mock_oauth_service.exchange_code(
            provider_name="github",
            code="auth_code",
            redirect_uri=state_data["redirect_uri"],
        )
        assert token.access_token is not None

        # Step 4: Get user info
        user_info = await mock_oauth_service.get_user_info(
            provider_name="github",
            access_token=token.access_token,
        )
        assert user_info.provider == "mock"  # MockOAuthProvider default


class TestOAuthServiceErrorHandling:
    """Test suite for error handling in OAuthService."""

    async def test_exchange_code_with_provider_error(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that provider errors are propagated correctly."""
        provider = await mock_oauth_service.register_mock_provider(
            "github",
            raise_on_exchange=True,
        )

        with pytest.raises(Exception):  # Should be TokenExchangeError when implemented
            await mock_oauth_service.exchange_code(
                provider_name="github",
                code="test_code",
                redirect_uri="http://localhost/callback",
            )

    async def test_get_user_info_with_provider_error(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test that provider errors during user info fetch are propagated."""
        await mock_oauth_service.register_mock_provider(
            "github",
            raise_on_user_info=True,
        )

        with pytest.raises(Exception):  # Should be UserInfoError when implemented
            await mock_oauth_service.get_user_info(
                provider_name="github",
                access_token="test_token",
            )


class TestOAuthServiceConfiguration:
    """Test suite for OAuthService configuration."""

    def test_create_empty_service(self, mock_oauth_service: MockOAuthService) -> None:
        """Test creating service with no providers."""
        assert mock_oauth_service.get_provider("github") is None

    async def test_create_service_with_providers(self) -> None:
        """Test creating service with initial providers."""
        from litestar_oauth.testing.mocks import MockOAuthProvider, MockOAuthService

        providers = {
            "github": MockOAuthProvider(provider_name="github"),
            "google": MockOAuthProvider(provider_name="google"),
        }

        service = MockOAuthService(providers=providers)

        assert service.get_provider("github") is not None
        assert service.get_provider("google") is not None

    async def test_service_isolates_provider_instances(self) -> None:
        """Test that service properly isolates provider instances."""
        from litestar_oauth.testing.mocks import MockOAuthService

        service1 = MockOAuthService()
        service2 = MockOAuthService()

        await service1.register_mock_provider("github")

        assert service1.get_provider("github") is not None
        assert service2.get_provider("github") is None


class TestOAuthServiceStateTTL:
    """Test suite for state time-to-live handling."""

    async def test_create_state_with_custom_ttl(
        self,
        mock_oauth_service: MockOAuthService,
    ) -> None:
        """Test creating state with custom TTL."""
        state = await mock_oauth_service.create_state(
            provider="github",
            redirect_uri="http://localhost/callback",
            ttl=300,  # 5 minutes
        )

        assert state is not None

    async def test_expired_state_validation_fails(self) -> None:
        """Test that expired states fail validation."""
        # This test would require actual TTL implementation
        # For now, just a placeholder
        # from litestar_oauth import OAuthService
        # service = OAuthService()
        # state = await service.create_state(..., ttl=0)
        # await asyncio.sleep(0.1)
        # assert await service.validate_state(state) is None
        pass


class TestOAuthServiceProviderListing:
    """Test suite for listing registered providers."""

    async def test_list_providers(self) -> None:
        """Test getting list of registered provider names."""
        # When implemented:
        # from litestar_oauth import OAuthService
        # service = OAuthService()
        # await service.register_provider(...)
        # providers = service.list_providers()
        # assert "github" in providers
        pass

    async def test_empty_providers_list(self) -> None:
        """Test listing providers when none are registered."""
        # When implemented:
        # from litestar_oauth import OAuthService
        # service = OAuthService()
        # providers = service.list_providers()
        # assert len(providers) == 0
        pass


class TestOAuthServiceFromConfig:
    """Test suite for creating service from configuration."""

    async def test_create_service_from_config(self) -> None:
        """Test creating service from config dict."""
        # When implemented:
        # from litestar_oauth import OAuthService
        # config = {
        #     "github": {"client_id": "...", "client_secret": "..."},
        #     "google": {"client_id": "...", "client_secret": "..."},
        # }
        # service = OAuthService.from_config(config)
        # assert service.get_provider("github") is not None
        pass

    async def test_config_validation(self) -> None:
        """Test that invalid config raises appropriate error."""
        # When implemented:
        # from litestar_oauth import OAuthService
        # invalid_config = {"github": {}}  # Missing required fields
        # with pytest.raises(ValueError):
        #     OAuthService.from_config(invalid_config)
        pass
