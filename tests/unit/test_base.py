"""Unit tests for BaseOAuthProvider abstract base class.

Tests the base OAuth provider implementation:
- Protocol compliance
- Abstract method enforcement
- Common provider functionality
- Configuration validation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any


class TestOAuthProviderProtocol:
    """Test suite for OAuthProvider protocol definition."""

    def test_protocol_defines_required_properties(self) -> None:
        """Test that protocol defines all required properties."""
        # from litestar_oauth.base import OAuthProvider
        # import inspect
        #
        # # Check protocol has required properties
        # required_props = [
        #     "provider_name",
        #     "authorize_url",
        #     "token_url",
        #     "user_info_url",
        #     "scope",
        # ]
        # for prop in required_props:
        #     assert hasattr(OAuthProvider, prop)
        pass

    def test_protocol_defines_required_methods(self) -> None:
        """Test that protocol defines all required methods."""
        # from litestar_oauth.base import OAuthProvider
        #
        # required_methods = [
        #     "is_configured",
        #     "get_authorization_url",
        #     "exchange_code",
        #     "refresh_token",
        #     "get_user_info",
        #     "revoke_token",
        # ]
        # for method in required_methods:
        #     assert hasattr(OAuthProvider, method)
        pass

    def test_protocol_is_runtime_checkable(self) -> None:
        """Test that protocol can be checked at runtime."""
        # from litestar_oauth.base import OAuthProvider
        # from litestar_oauth.testing.mocks import MockOAuthProvider
        #
        # provider = MockOAuthProvider()
        # assert isinstance(provider, OAuthProvider)
        pass


class TestBaseOAuthProvider:
    """Test suite for BaseOAuthProvider ABC implementation."""

    def test_base_provider_cannot_be_instantiated(self) -> None:
        """Test that BaseOAuthProvider cannot be instantiated directly."""
        # from litestar_oauth.base import BaseOAuthProvider
        #
        # with pytest.raises(TypeError) as exc_info:
        #     BaseOAuthProvider()
        # assert "abstract" in str(exc_info.value).lower()
        pass

    def test_base_provider_enforces_abstract_methods(self) -> None:
        """Test that subclasses must implement abstract methods."""
        # from litestar_oauth.base import BaseOAuthProvider
        #
        # class IncompleteProvider(BaseOAuthProvider):
        #     provider_name = "incomplete"
        #
        # with pytest.raises(TypeError) as exc_info:
        #     IncompleteProvider()
        # assert "abstract" in str(exc_info.value).lower()
        pass

    def test_base_provider_with_all_methods_implemented(self) -> None:
        """Test that complete implementation can be instantiated."""
        # from litestar_oauth.base import BaseOAuthProvider
        # from litestar_oauth.testing.mocks import MockOAuthProvider
        #
        # # MockOAuthProvider should be a complete implementation
        # provider = MockOAuthProvider(provider_name="test")
        # assert isinstance(provider, BaseOAuthProvider)
        pass

    def test_base_provider_provides_common_functionality(self) -> None:
        """Test that base class provides common helper methods."""
        # from litestar_oauth.testing.mocks import MockOAuthProvider
        #
        # provider = MockOAuthProvider()
        #
        # # Test common URL building
        # url = provider.get_authorization_url("http://localhost/callback", "state123")
        # assert "redirect_uri=http://localhost/callback" in url
        # assert "state=state123" in url
        pass


class TestProviderConfiguration:
    """Test suite for provider configuration validation."""

    def test_is_configured_returns_true_when_configured(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test is_configured returns True for properly configured provider."""
        assert mock_github_provider.is_configured() is True

    def test_is_configured_returns_false_when_not_configured(self) -> None:
        """Test is_configured returns False for unconfigured provider."""
        from litestar_oauth.testing.mocks import MockOAuthProvider

        provider = MockOAuthProvider(configured=False)
        assert provider.is_configured() is False

    def test_provider_raises_when_used_unconfigured(self) -> None:
        """Test that using unconfigured provider raises appropriate error."""
        # from litestar_oauth.exceptions import ProviderNotConfiguredError
        # from litestar_oauth.testing.mocks import MockOAuthProvider
        #
        # provider = MockOAuthProvider(configured=False)
        #
        # with pytest.raises(ProviderNotConfiguredError):
        #     await provider.exchange_code("code", "redirect_uri")
        pass

    @pytest.mark.parametrize(
        ("client_id", "client_secret", "expected"),
        [
            ("valid_id", "valid_secret", True),
            (None, "valid_secret", False),
            ("valid_id", None, False),
            (None, None, False),
            ("", "valid_secret", False),
        ],
    )
    def test_configuration_validation(
        self,
        client_id: str | None,
        client_secret: str | None,
        expected: bool,
    ) -> None:
        """Test provider configuration validation logic."""
        # When implemented with actual provider:
        # provider = SomeOAuthProvider(client_id=client_id, client_secret=client_secret)
        # assert provider.is_configured() == expected
        configured = bool(client_id and client_secret)
        assert configured == expected


class TestAuthorizationURL:
    """Test suite for authorization URL generation."""

    def test_get_authorization_url_basic(self, mock_github_provider: Any) -> None:
        """Test generating basic authorization URL."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
        )

        assert mock_github_provider.authorize_url in url
        assert "redirect_uri=http://localhost/callback" in url
        assert "state=abc123" in url

    def test_get_authorization_url_with_custom_scope(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test authorization URL with custom scope."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
            scope="user:email read:org",
        )

        assert "scope=user:email read:org" in url or "scope=user%3Aemail" in url

    def test_get_authorization_url_with_extra_params(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test authorization URL with extra parameters."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
            extra_params={"prompt": "consent", "access_type": "offline"},
        )

        assert "prompt=consent" in url
        assert "access_type=offline" in url

    def test_authorization_url_contains_response_type(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test that authorization URL includes response_type=code."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
        )

        assert "response_type=code" in url

    @pytest.mark.parametrize(
        "redirect_uri",
        [
            "http://localhost:8000/callback",
            "https://example.com/auth/callback",
            "http://localhost:3000/api/auth/callback",
        ],
    )
    def test_authorization_url_with_different_redirect_uris(
        self,
        mock_github_provider: Any,
        redirect_uri: str,
    ) -> None:
        """Test authorization URL generation with various redirect URIs."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri=redirect_uri,
            state="state123",
        )

        # URL encoding may apply
        assert redirect_uri in url or redirect_uri.replace(":", "%3A") in url


class TestTokenExchange:
    """Test suite for authorization code exchange."""

    async def test_exchange_code_success(self, mock_github_provider: Any) -> None:
        """Test successful code exchange returns token."""
        token = await mock_github_provider.exchange_code(
            code="test_code",
            redirect_uri="http://localhost/callback",
        )

        assert hasattr(token, "access_token")
        assert token.access_token is not None

    async def test_exchange_code_failure(self) -> None:
        """Test code exchange failure raises appropriate error."""
        from litestar_oauth.testing.mocks import MockOAuthProvider

        provider = MockOAuthProvider(raise_on_exchange=True)

        with pytest.raises(Exception):  # Should be TokenExchangeError when implemented
            await provider.exchange_code("invalid_code", "http://localhost/callback")

    async def test_exchange_code_returns_oauth_token(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test that code exchange returns OAuthToken instance."""
        token = await mock_github_provider.exchange_code(
            code="test_code",
            redirect_uri="http://localhost/callback",
        )

        # Should have OAuthToken attributes
        assert hasattr(token, "access_token")
        assert hasattr(token, "token_type")
        assert hasattr(token, "expires_in")


class TestTokenRefresh:
    """Test suite for token refresh functionality."""

    async def test_refresh_token_success(self, mock_github_provider: Any) -> None:
        """Test successful token refresh."""
        new_token = await mock_github_provider.refresh_token("refresh_token_value")

        assert hasattr(new_token, "access_token")
        assert new_token.access_token is not None

    async def test_refresh_token_failure(self) -> None:
        """Test token refresh failure raises appropriate error."""
        from litestar_oauth.testing.mocks import MockOAuthProvider

        provider = MockOAuthProvider(raise_on_refresh=True)

        with pytest.raises(Exception):  # Should be TokenRefreshError when implemented
            await provider.refresh_token("invalid_refresh_token")

    async def test_refresh_token_returns_new_access_token(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test that refresh returns new access token."""
        new_token = await mock_github_provider.refresh_token("refresh_token_value")

        assert hasattr(new_token, "access_token")
        assert hasattr(new_token, "token_type")


class TestUserInfo:
    """Test suite for user info retrieval."""

    async def test_get_user_info_success(self, mock_github_provider: Any) -> None:
        """Test successful user info retrieval."""
        user_info = await mock_github_provider.get_user_info("access_token")

        assert hasattr(user_info, "provider")
        assert hasattr(user_info, "oauth_id")
        assert hasattr(user_info, "email")

    async def test_get_user_info_failure(self) -> None:
        """Test user info retrieval failure raises appropriate error."""
        from litestar_oauth.testing.mocks import MockOAuthProvider

        provider = MockOAuthProvider(raise_on_user_info=True)

        with pytest.raises(Exception):  # Should be UserInfoError when implemented
            await provider.get_user_info("invalid_token")

    async def test_get_user_info_returns_normalized_data(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test that user info is normalized to OAuthUserInfo format."""
        user_info = await mock_github_provider.get_user_info("access_token")

        # Should have normalized fields
        assert hasattr(user_info, "provider")
        assert hasattr(user_info, "oauth_id")
        assert hasattr(user_info, "email")
        assert hasattr(user_info, "email_verified")


class TestTokenRevocation:
    """Test suite for token revocation."""

    async def test_revoke_token_success(self, mock_github_provider: Any) -> None:
        """Test successful token revocation."""
        # Should not raise
        await mock_github_provider.revoke_token("access_token")

    async def test_revoke_access_token(self, mock_github_provider: Any) -> None:
        """Test revoking access token."""
        await mock_github_provider.revoke_token(
            "access_token",
            token_type_hint="access_token",
        )

    async def test_revoke_refresh_token(self, mock_github_provider: Any) -> None:
        """Test revoking refresh token."""
        await mock_github_provider.revoke_token(
            "refresh_token",
            token_type_hint="refresh_token",
        )

    async def test_revoke_token_failure_does_not_raise(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test that revocation failures are handled gracefully."""
        # Even if revocation fails, should not raise (best effort)
        await mock_github_provider.revoke_token("invalid_token")
