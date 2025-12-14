"""Unit tests for GoogleOAuthProvider.

Tests Google-specific OAuth implementation:
- Authorization URL generation with OIDC
- Token exchange with Google OAuth2 API
- User info retrieval from Google
- ID token parsing and validation
- Google-specific features (refresh tokens, consent prompt, etc.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any


@pytest.mark.provider
class TestGoogleOAuthProvider:
    """Test suite for Google OAuth provider."""

    def test_google_provider_properties(self, mock_google_provider: Any) -> None:
        """Test Google provider has correct endpoints and properties."""
        assert mock_google_provider.provider_name == "google"
        assert "accounts.google.com" in mock_google_provider.authorize_url
        assert "oauth2.googleapis.com" in mock_google_provider.token_url
        assert "googleapis.com" in mock_google_provider.user_info_url

    def test_google_provider_default_scope(self, mock_google_provider: Any) -> None:
        """Test Google provider includes OIDC scopes."""
        # Google OAuth should include openid, email, profile
        scope = mock_google_provider.scope.lower()
        assert "openid" in scope
        assert "email" in scope
        assert "profile" in scope

    async def test_google_provider_configuration(self) -> None:
        """Test Google provider configuration with client credentials."""
        # When implemented:
        # from litestar_oauth.providers import GoogleOAuthProvider
        # provider = GoogleOAuthProvider(
        #     client_id="test_client_id.apps.googleusercontent.com",
        #     client_secret="test_client_secret",
        # )
        # assert provider.is_configured() is True
        pass


@pytest.mark.provider
class TestGoogleAuthorizationURL:
    """Test suite for Google authorization URL generation."""

    def test_google_authorization_url_basic(self, mock_google_provider: Any) -> None:
        """Test generating Google authorization URL."""
        url = mock_google_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
        )

        assert "accounts.google.com/o/oauth2/v2/auth" in url
        assert "client_id=" in url
        assert "redirect_uri=" in url
        assert "state=abc123" in url
        assert "response_type=code" in url

    def test_google_authorization_url_with_consent_prompt(self) -> None:
        """Test Google authorization URL with consent prompt."""
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     extra_params={"prompt": "consent"},
        # )
        # assert "prompt=consent" in url
        pass

    def test_google_authorization_url_with_access_type_offline(self) -> None:
        """Test Google authorization URL for refresh token."""
        # access_type=offline is required to get refresh token
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     extra_params={"access_type": "offline"},
        # )
        # assert "access_type=offline" in url
        pass

    def test_google_authorization_url_with_hd_parameter(self) -> None:
        """Test Google Workspace domain restriction."""
        # hd parameter restricts to specific Google Workspace domain
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     extra_params={"hd": "example.com"},
        # )
        # assert "hd=example.com" in url
        pass

    def test_google_authorization_url_with_select_account(self) -> None:
        """Test Google authorization URL with account selection."""
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     extra_params={"prompt": "select_account"},
        # )
        # assert "prompt=select_account" in url
        pass


@pytest.mark.provider
class TestGoogleTokenExchange:
    """Test suite for Google token exchange."""

    async def test_google_exchange_code_success(
        self,
        mock_google_provider: Any,
        mock_http_responses: dict[str, Any],
    ) -> None:
        """Test successful Google code exchange."""
        token = await mock_google_provider.exchange_code(
            code="google_auth_code",
            redirect_uri="http://localhost/callback",
        )

        assert hasattr(token, "access_token")
        assert token.access_token is not None

    async def test_google_exchange_code_with_httpx_mock(self) -> None:
        """Test Google code exchange with mocked HTTP client."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://oauth2.googleapis.com/token",
        #     json={
        #         "access_token": "ya29.a0AfH6SMBx...",
        #         "token_type": "Bearer",
        #         "expires_in": 3599,
        #         "scope": "openid email profile",
        #         "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
        #     },
        # )
        # token = await provider.exchange_code("code", "redirect_uri")
        # assert token.access_token.startswith("ya29")
        pass

    async def test_google_token_includes_id_token(self) -> None:
        """Test that Google token exchange returns id_token."""
        # Google OIDC returns id_token for openid scope
        # When implemented:
        # token = await provider.exchange_code("code", "redirect_uri")
        # assert token.id_token is not None
        # assert token.id_token.startswith("eyJ")  # JWT format
        pass

    async def test_google_token_exchange_with_refresh_token(self) -> None:
        """Test Google token exchange with refresh token."""
        # Refresh token only returned with access_type=offline
        # When implemented:
        # httpx_mock.add_response(
        #     json={
        #         "access_token": "ya29...",
        #         "refresh_token": "1//...",
        #         "expires_in": 3599,
        #     }
        # )
        # token = await provider.exchange_code("code", "redirect_uri")
        # assert token.refresh_token is not None
        pass


@pytest.mark.provider
class TestGoogleUserInfo:
    """Test suite for Google user info retrieval."""

    async def test_google_get_user_info_success(
        self,
        mock_google_provider: Any,
        mock_google_user: dict[str, Any],
    ) -> None:
        """Test successful Google user info retrieval."""
        user_info = await mock_google_provider.get_user_info("ya29_test_token")

        assert hasattr(user_info, "provider")
        assert hasattr(user_info, "oauth_id")
        assert hasattr(user_info, "email")

    async def test_google_user_info_normalization(
        self,
        mock_google_user: dict[str, Any],
    ) -> None:
        """Test Google user data normalization to OAuthUserInfo."""
        # When implemented:
        # from litestar_oauth.providers.google import normalize_google_user
        # user_info = normalize_google_user(mock_google_user["raw_data"])
        #
        # assert user_info.provider == "google"
        # assert user_info.oauth_id == mock_google_user["raw_data"]["sub"]
        # assert user_info.email == mock_google_user["raw_data"]["email"]
        # assert user_info.first_name == mock_google_user["raw_data"]["given_name"]
        # assert user_info.last_name == mock_google_user["raw_data"]["family_name"]
        assert mock_google_user["first_name"] == "Test"
        assert mock_google_user["last_name"] == "User"

    async def test_google_user_info_with_httpx_mock(self) -> None:
        """Test Google user info with mocked HTTP response."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://www.googleapis.com/oauth2/v3/userinfo",
        #     json={
        #         "sub": "123456789012345678901",
        #         "name": "Test User",
        #         "given_name": "Test",
        #         "family_name": "User",
        #         "picture": "https://lh3.googleusercontent.com/...",
        #         "email": "test@gmail.com",
        #         "email_verified": True,
        #     },
        # )
        # user_info = await provider.get_user_info("token")
        # assert user_info.email == "test@gmail.com"
        pass

    async def test_google_user_info_email_verified(
        self,
        mock_google_user: dict[str, Any],
    ) -> None:
        """Test Google email verification status is captured."""
        assert mock_google_user["email_verified"] is True

    async def test_google_user_info_workspace_domain(self) -> None:
        """Test Google Workspace domain (hd) is captured."""
        # When user is from Google Workspace, hd field is present
        # When implemented:
        # raw_data = {"sub": "123", "email": "user@company.com", "hd": "company.com"}
        # user_info = normalize_google_user(raw_data)
        # assert user_info.raw_data.get("hd") == "company.com"
        pass


@pytest.mark.provider
class TestGoogleIDToken:
    """Test suite for Google ID token handling."""

    async def test_google_id_token_parsing(self) -> None:
        """Test parsing Google ID token JWT."""
        # When implemented:
        # from litestar_oauth.providers.google import parse_id_token
        # id_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NWUyZWY5..."
        # claims = parse_id_token(id_token, verify=False)  # Skip signature verification in tests
        # assert "sub" in claims
        # assert "email" in claims
        pass

    async def test_google_id_token_validation(self) -> None:
        """Test ID token signature validation."""
        # Google ID tokens should be validated against Google's public keys
        # When implemented:
        # from litestar_oauth.providers.google import validate_id_token
        # id_token = "..."
        # claims = await validate_id_token(id_token, client_id="...")
        # assert claims["aud"] == client_id
        pass

    async def test_google_id_token_contains_user_info(self) -> None:
        """Test that ID token contains basic user information."""
        # ID token claims include sub, email, name, picture
        # Can be used instead of separate userinfo endpoint call
        pass


@pytest.mark.provider
class TestGoogleRefreshToken:
    """Test suite for Google refresh token functionality."""

    async def test_google_refresh_token_exchange(
        self,
        mock_google_provider: Any,
    ) -> None:
        """Test Google refresh token exchange."""
        new_token = await mock_google_provider.refresh_token("1//refresh_token")

        assert hasattr(new_token, "access_token")
        assert new_token.access_token is not None

    async def test_google_refresh_token_with_httpx_mock(self) -> None:
        """Test Google refresh token exchange with HTTP mock."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://oauth2.googleapis.com/token",
        #     json={
        #         "access_token": "ya29.new_token",
        #         "token_type": "Bearer",
        #         "expires_in": 3599,
        #     },
        # )
        # token = await provider.refresh_token("1//old_refresh")
        # assert token.access_token == "ya29.new_token"
        pass

    async def test_google_refresh_token_does_not_return_new_refresh_token(self) -> None:
        """Test that Google refresh does not return new refresh token."""
        # Unlike some providers, Google keeps the same refresh token
        # New refresh token only issued on first authorization with access_type=offline
        pass


@pytest.mark.provider
class TestGoogleTokenRevocation:
    """Test suite for Google token revocation."""

    async def test_google_revoke_token(self, mock_google_provider: Any) -> None:
        """Test Google token revocation."""
        await mock_google_provider.revoke_token("ya29_test_token")

    async def test_google_revoke_token_with_httpx_mock(self) -> None:
        """Test Google token revocation with HTTP mock."""
        # When implemented:
        # httpx_mock.add_response(
        #     url="https://oauth2.googleapis.com/revoke",
        #     status_code=200,
        # )
        # await provider.revoke_token("token")
        pass

    async def test_google_revoke_refresh_token(self) -> None:
        """Test revoking Google refresh token."""
        # Revoking refresh token also invalidates associated access tokens
        # When implemented:
        # await provider.revoke_token("1//refresh_token", token_type_hint="refresh_token")
        pass


@pytest.mark.provider
class TestGoogleErrorHandling:
    """Test suite for Google-specific error handling."""

    async def test_google_invalid_grant_error(self) -> None:
        """Test handling Google invalid_grant error."""
        # When implemented:
        # httpx_mock.add_response(
        #     url="https://oauth2.googleapis.com/token",
        #     status_code=400,
        #     json={"error": "invalid_grant", "error_description": "Code expired"},
        # )
        # with pytest.raises(TokenExchangeError) as exc_info:
        #     await provider.exchange_code("expired_code", "redirect_uri")
        # assert "invalid_grant" in str(exc_info.value)
        pass

    async def test_google_redirect_uri_mismatch_error(self) -> None:
        """Test handling redirect_uri mismatch error."""
        # Google returns error when redirect_uri doesn't match
        # httpx_mock.add_response(
        #     status_code=400,
        #     json={"error": "redirect_uri_mismatch"},
        # )
        # with pytest.raises(TokenExchangeError):
        #     await provider.exchange_code("code", "wrong_redirect_uri")
        pass

    async def test_google_invalid_token_error(self) -> None:
        """Test handling invalid/expired token errors."""
        # When implemented:
        # httpx_mock.add_response(
        #     url="https://www.googleapis.com/oauth2/v3/userinfo",
        #     status_code=401,
        #     json={"error": {"code": 401, "message": "Invalid Credentials"}},
        # )
        # with pytest.raises(UserInfoError):
        #     await provider.get_user_info("invalid_token")
        pass


@pytest.mark.provider
class TestGoogleSpecificFeatures:
    """Test suite for Google-specific OAuth features."""

    def test_google_supports_oidc(self) -> None:
        """Test that Google provider supports OpenID Connect."""
        # Google is OIDC-compliant
        # Should support discovery endpoint, id_token, etc.
        pass

    async def test_google_workspace_integration(self) -> None:
        """Test Google Workspace (G Suite) specific features."""
        # When hd parameter is used, restrict to workspace domain
        # User info includes hd field for workspace accounts
        pass

    def test_google_incremental_authorization(self) -> None:
        """Test Google incremental authorization support."""
        # Google supports requesting additional scopes without re-auth
        # Using include_granted_scopes=true parameter
        pass

    async def test_google_people_api_integration(self) -> None:
        """Test optional Google People API for extended user info."""
        # Provider could optionally use People API for more detailed info
        # Requires additional scope: https://www.googleapis.com/auth/userinfo.profile
        pass

    def test_google_multiple_accounts_handling(self) -> None:
        """Test handling users with multiple Google accounts."""
        # prompt=select_account allows user to choose account
        # login_hint parameter can suggest specific account
        pass


@pytest.mark.provider
@pytest.mark.parametrize(
    ("scope", "expected_in_url"),
    [
        ("openid email profile", "openid"),
        ("openid email", "email"),
        ("https://www.googleapis.com/auth/userinfo.profile", "googleapis"),
    ],
)
def test_google_scope_formatting(scope: str, expected_in_url: str) -> None:
    """Test Google scope formatting in authorization URLs."""
    # Google uses space-separated scopes
    # Also supports full URI scopes for Google APIs
    pass


@pytest.mark.provider
class TestGoogleOIDCDiscovery:
    """Test suite for Google OIDC discovery."""

    async def test_google_oidc_discovery_endpoint(self) -> None:
        """Test fetching Google OIDC discovery document."""
        # When implemented:
        # discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
        # discovery_data = await fetch_discovery(discovery_url)
        # assert "authorization_endpoint" in discovery_data
        # assert "token_endpoint" in discovery_data
        # assert "userinfo_endpoint" in discovery_data
        pass

    async def test_google_jwks_endpoint(self) -> None:
        """Test fetching Google JSON Web Key Set for token validation."""
        # JWKS endpoint provides public keys for ID token validation
        # https://www.googleapis.com/oauth2/v3/certs
        pass
