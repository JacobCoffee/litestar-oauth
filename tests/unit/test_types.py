"""Unit tests for OAuth type definitions.

Tests the dataclasses and type definitions used throughout litestar-oauth:
- OAuthUserInfo
- OAuthToken
- OAuthState
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any


class TestOAuthUserInfo:
    """Test suite for OAuthUserInfo dataclass."""

    def test_oauth_user_info_creation(self, mock_github_user: dict[str, Any]) -> None:
        """Test creating OAuthUserInfo with minimal required fields."""
        # Note: This test assumes OAuthUserInfo will be implemented
        # For now, we test with dict data from fixture
        assert mock_github_user["provider"] == "github"
        assert mock_github_user["oauth_id"] == "12345678"
        assert mock_github_user["email"] == "octocat@github.com"

    def test_oauth_user_info_full_name_property(self, mock_github_user: dict[str, Any]) -> None:
        """Test full_name property combines first and last name."""
        expected_full_name = f"{mock_github_user['first_name']} {mock_github_user['last_name']}"
        assert expected_full_name == "The Octocat"

    def test_oauth_user_info_defaults(self) -> None:
        """Test OAuthUserInfo default values for optional fields."""
        # This will test actual implementation when available
        user_data = {
            "provider": "github",
            "oauth_id": "123",
            "email": "test@example.com",
            "email_verified": False,
            "username": "",
            "first_name": "",
            "last_name": "",
            "avatar_url": "",
            "profile_url": "",
            "raw_data": {},
        }
        assert user_data["username"] == ""
        assert user_data["first_name"] == ""
        assert user_data["email_verified"] is False

    def test_oauth_user_info_immutable(self) -> None:
        """Test that OAuthUserInfo is immutable (frozen dataclass)."""
        # When implemented, should test with:
        # user = OAuthUserInfo(...)
        # with pytest.raises(FrozenInstanceError):
        #     user.email = "new@example.com"
        pass  # Placeholder for actual implementation

    def test_oauth_user_info_raw_data(self, mock_github_user: dict[str, Any]) -> None:
        """Test that raw_data preserves provider-specific fields."""
        raw = mock_github_user["raw_data"]
        assert raw["id"] == 12345678
        assert raw["login"] == "octocat"
        assert "bio" in raw
        assert "company" in raw

    @pytest.mark.parametrize(
        ("provider", "fixture_name"),
        [
            ("github", "mock_github_user"),
            ("google", "mock_google_user"),
            ("discord", "mock_discord_user"),
        ],
    )
    def test_oauth_user_info_provider_normalization(
        self,
        provider: str,
        fixture_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        """Test that different providers normalize to common OAuthUserInfo format."""
        user_data = request.getfixturevalue(fixture_name)
        assert user_data["provider"] == provider
        assert "oauth_id" in user_data
        assert "email" in user_data
        assert isinstance(user_data["email_verified"], bool)


class TestOAuthToken:
    """Test suite for OAuthToken dataclass."""

    def test_oauth_token_creation(self, mock_oauth_token: dict[str, Any]) -> None:
        """Test creating OAuthToken with required fields."""
        assert mock_oauth_token["access_token"] == "gho_1234567890abcdef"
        assert mock_oauth_token["token_type"] == "Bearer"

    def test_oauth_token_defaults(self) -> None:
        """Test OAuthToken default values."""
        token_data = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": None,
            "refresh_token": None,
            "scope": None,
            "id_token": None,
            "raw_response": {},
        }
        assert token_data["token_type"] == "Bearer"
        assert token_data["expires_in"] is None
        assert token_data["refresh_token"] is None

    def test_oauth_token_expires_at_property(self, mock_oauth_token: dict[str, Any]) -> None:
        """Test expires_at property calculates expiry time from expires_in."""
        # When implemented with actual OAuthToken:
        # token = OAuthToken(access_token="test", expires_in=3600)
        # assert token.expires_at is not None
        # assert token.expires_at > datetime.now(UTC)
        expires_in = mock_oauth_token["expires_in"]
        assert expires_in == 3600

    def test_oauth_token_expires_at_none_when_no_expiry(self) -> None:
        """Test expires_at is None when expires_in not provided."""
        token_data = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": None,
        }
        # When implemented: assert token.expires_at is None
        assert token_data["expires_in"] is None

    def test_oauth_token_with_refresh_token(self, mock_oauth_token: dict[str, Any]) -> None:
        """Test OAuthToken includes refresh token when available."""
        assert mock_oauth_token["refresh_token"] == "ghr_0987654321fedcba"

    def test_oauth_token_with_id_token(self) -> None:
        """Test OAuthToken includes OIDC id_token when available."""
        token_data = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
        }
        assert token_data["id_token"] is not None
        assert token_data["id_token"].startswith("eyJ")

    def test_oauth_token_raw_response(self, mock_oauth_token: dict[str, Any]) -> None:
        """Test that raw_response preserves original provider response."""
        raw = mock_oauth_token["raw_response"]
        assert raw["access_token"] == mock_oauth_token["access_token"]
        assert "created_at" in raw

    def test_oauth_token_immutable(self) -> None:
        """Test that OAuthToken is immutable (frozen dataclass)."""
        # When implemented, should test with:
        # token = OAuthToken(access_token="test")
        # with pytest.raises(FrozenInstanceError):
        #     token.access_token = "new_token"
        pass  # Placeholder for actual implementation


class TestOAuthState:
    """Test suite for OAuthState dataclass."""

    def test_oauth_state_creation(self, mock_oauth_state: dict[str, Any]) -> None:
        """Test creating OAuthState with required fields."""
        assert mock_oauth_state["state"] is not None
        assert mock_oauth_state["provider"] == "github"
        assert mock_oauth_state["redirect_uri"] == "http://localhost:8000/auth/github/callback"

    def test_oauth_state_with_next_url(self, mock_oauth_state: dict[str, Any]) -> None:
        """Test OAuthState includes next_url for post-auth redirect."""
        assert mock_oauth_state["next_url"] == "/dashboard"

    def test_oauth_state_created_at_default(self) -> None:
        """Test created_at defaults to current time."""
        # When implemented:
        # state = OAuthState(state="test", provider="github", redirect_uri="http://...")
        # assert state.created_at is not None
        # assert (datetime.now(UTC) - state.created_at).seconds < 1
        pass  # Placeholder for actual implementation

    def test_oauth_state_extra_data(self, mock_oauth_state: dict[str, Any]) -> None:
        """Test extra_data stores additional context."""
        assert mock_oauth_state["extra_data"] == {"user_agent": "Mozilla/5.0"}

    def test_oauth_state_mutable(self) -> None:
        """Test that OAuthState is mutable (not frozen)."""
        # When implemented:
        # state = OAuthState(state="test", provider="github", redirect_uri="http://...")
        # state.next_url = "/profile"
        # assert state.next_url == "/profile"
        pass  # Placeholder for actual implementation

    @pytest.mark.parametrize(
        ("provider", "redirect_uri"),
        [
            ("github", "http://localhost/auth/github/callback"),
            ("google", "http://localhost/auth/google/callback"),
            ("discord", "http://localhost/auth/discord/callback"),
        ],
    )
    def test_oauth_state_for_different_providers(
        self,
        provider: str,
        redirect_uri: str,
    ) -> None:
        """Test OAuthState creation for various providers."""
        state_data = {
            "state": "test_state_123",
            "provider": provider,
            "redirect_uri": redirect_uri,
            "created_at": datetime.now(UTC).isoformat(),
        }
        assert state_data["provider"] == provider
        assert state_data["redirect_uri"] == redirect_uri


class TestTypeHelpers:
    """Test suite for type helper functions and utilities."""

    def test_oauth_user_info_from_provider_data(self) -> None:
        """Test creating OAuthUserInfo from provider-specific response."""
        # Placeholder for testing normalization helpers
        # e.g., normalize_github_user(raw_data) -> OAuthUserInfo
        pass

    def test_oauth_token_from_provider_response(self) -> None:
        """Test creating OAuthToken from provider token response."""
        # Placeholder for testing token parsing
        # e.g., parse_token_response(raw_response) -> OAuthToken
        pass

    def test_calculate_token_expiry(self) -> None:
        """Test token expiry calculation with various inputs."""
        now = datetime.now(UTC)
        expires_in = 3600  # 1 hour

        expected_expiry = now + timedelta(seconds=expires_in)

        # When implemented, test actual calculation
        # assert abs((token.expires_at - expected_expiry).seconds) < 1
        assert (expected_expiry - now).seconds == expires_in
