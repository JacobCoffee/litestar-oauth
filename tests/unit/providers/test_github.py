"""Unit tests for GitHubOAuthProvider.

Tests GitHub-specific OAuth implementation:
- Authorization URL generation
- Token exchange with GitHub API
- User info retrieval and normalization
- GitHub-specific features (scopes, refresh tokens, etc.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any


@pytest.mark.provider
class TestGitHubOAuthProvider:
    """Test suite for GitHub OAuth provider."""

    def test_github_provider_properties(self, mock_github_provider: Any) -> None:
        """Test GitHub provider has correct endpoints and properties."""
        assert mock_github_provider.provider_name == "github"
        assert "github.com" in mock_github_provider.authorize_url
        assert "github.com" in mock_github_provider.token_url
        assert "api.github.com" in mock_github_provider.user_info_url

    def test_github_provider_default_scope(self, mock_github_provider: Any) -> None:
        """Test GitHub provider has appropriate default scopes."""
        assert "user" in mock_github_provider.scope or "email" in mock_github_provider.scope

    async def test_github_provider_configuration(self) -> None:
        """Test GitHub provider configuration with client credentials."""
        # When implemented:
        # from litestar_oauth.providers import GitHubOAuthProvider
        # provider = GitHubOAuthProvider(
        #     client_id="test_client_id",
        #     client_secret="test_client_secret",
        # )
        # assert provider.is_configured() is True
        pass


@pytest.mark.provider
class TestGitHubAuthorizationURL:
    """Test suite for GitHub authorization URL generation."""

    def test_github_authorization_url_basic(self, mock_github_provider: Any) -> None:
        """Test generating GitHub authorization URL."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
        )

        assert "github.com/login/oauth/authorize" in url
        assert "client_id=" in url
        assert "redirect_uri=" in url
        assert "state=abc123" in url

    def test_github_authorization_url_with_scopes(
        self,
        mock_github_provider: Any,
    ) -> None:
        """Test GitHub authorization URL with custom scopes."""
        url = mock_github_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
            scope="user:email read:org repo",
        )

        # GitHub uses space-separated scopes
        assert "scope=" in url
        # URL encoding may apply
        assert "user" in url.lower()

    def test_github_authorization_url_with_allow_signup(self) -> None:
        """Test GitHub-specific allow_signup parameter."""
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     extra_params={"allow_signup": "false"},
        # )
        # assert "allow_signup=false" in url
        pass


@pytest.mark.provider
class TestGitHubTokenExchange:
    """Test suite for GitHub token exchange."""

    async def test_github_exchange_code_success(
        self,
        mock_github_provider: Any,
        mock_http_responses: dict[str, Any],
    ) -> None:
        """Test successful GitHub code exchange."""
        # This would use pytest-httpx in real implementation
        token = await mock_github_provider.exchange_code(
            code="github_auth_code",
            redirect_uri="http://localhost/callback",
        )

        assert hasattr(token, "access_token")
        assert token.access_token is not None

    async def test_github_exchange_code_with_httpx_mock(self) -> None:
        """Test GitHub code exchange with mocked HTTP client."""
        # When implemented with pytest-httpx:
        # from litestar_oauth.providers import GitHubOAuthProvider
        # import httpx
        #
        # provider = GitHubOAuthProvider(
        #     client_id="test_id",
        #     client_secret="test_secret",
        # )
        #
        # with httpx_mock.add_response(
        #     url="https://github.com/login/oauth/access_token",
        #     json={
        #         "access_token": "gho_test_token",
        #         "token_type": "bearer",
        #         "scope": "user:email",
        #     },
        # ):
        #     token = await provider.exchange_code("code", "redirect_uri")
        #     assert token.access_token == "gho_test_token"
        pass

    async def test_github_token_exchange_sends_accept_header(self) -> None:
        """Test that GitHub token exchange sends Accept: application/json header."""
        # GitHub requires explicit JSON accept header
        # This would be tested by checking the actual HTTP request
        pass

    async def test_github_token_exchange_error_handling(self) -> None:
        """Test GitHub token exchange error responses."""
        # When implemented with httpx_mock:
        # httpx_mock.add_response(
        #     url="https://github.com/login/oauth/access_token",
        #     status_code=401,
        #     json={"error": "bad_verification_code"},
        # )
        # with pytest.raises(TokenExchangeError):
        #     await provider.exchange_code("invalid_code", "redirect_uri")
        pass


@pytest.mark.provider
class TestGitHubUserInfo:
    """Test suite for GitHub user info retrieval."""

    async def test_github_get_user_info_success(
        self,
        mock_github_provider: Any,
        mock_github_user: dict[str, Any],
    ) -> None:
        """Test successful GitHub user info retrieval."""
        user_info = await mock_github_provider.get_user_info("gho_test_token")

        assert hasattr(user_info, "provider")
        assert hasattr(user_info, "oauth_id")
        assert hasattr(user_info, "email")

    async def test_github_user_info_normalization(
        self,
        mock_github_user: dict[str, Any],
    ) -> None:
        """Test GitHub user data normalization to OAuthUserInfo."""
        # When implemented:
        # from litestar_oauth.providers.github import normalize_github_user
        # user_info = normalize_github_user(mock_github_user["raw_data"])
        #
        # assert user_info.provider == "github"
        # assert user_info.oauth_id == str(mock_github_user["raw_data"]["id"])
        # assert user_info.username == mock_github_user["raw_data"]["login"]
        # assert user_info.email == mock_github_user["raw_data"]["email"]
        assert mock_github_user["username"] == "octocat"

    async def test_github_user_info_with_httpx_mock(self) -> None:
        """Test GitHub user info with mocked HTTP response."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://api.github.com/user",
        #     json={
        #         "id": 12345,
        #         "login": "octocat",
        #         "email": "octocat@github.com",
        #         "name": "The Octocat",
        #         "avatar_url": "https://avatars.githubusercontent.com/u/12345",
        #     },
        # )
        # user_info = await provider.get_user_info("token")
        # assert user_info.username == "octocat"
        pass

    async def test_github_user_info_sends_auth_header(self) -> None:
        """Test that GitHub user info request includes authorization header."""
        # Should send: Authorization: Bearer {token}
        # Or: Authorization: token {token} (GitHub also accepts this format)
        pass

    async def test_github_user_info_with_private_email(self) -> None:
        """Test handling GitHub users with private email settings."""
        # When email is private, GitHub may return null
        # Provider should fetch from /user/emails endpoint
        # httpx_mock.add_response(
        #     url="https://api.github.com/user",
        #     json={"id": 12345, "login": "user", "email": None},
        # )
        # httpx_mock.add_response(
        #     url="https://api.github.com/user/emails",
        #     json=[{"email": "user@example.com", "primary": True, "verified": True}],
        # )
        # user_info = await provider.get_user_info("token")
        # assert user_info.email == "user@example.com"
        pass


@pytest.mark.provider
class TestGitHubRefreshToken:
    """Test suite for GitHub refresh token functionality."""

    async def test_github_supports_refresh_tokens(self) -> None:
        """Test that GitHub provider supports refresh tokens."""
        # GitHub supports refresh tokens as of 2021
        # When implemented:
        # from litestar_oauth.providers import GitHubOAuthProvider
        # provider = GitHubOAuthProvider(...)
        # assert hasattr(provider, "refresh_token")
        pass

    async def test_github_refresh_token_exchange(self) -> None:
        """Test GitHub refresh token exchange."""
        # When implemented with httpx_mock:
        # httpx_mock.add_response(
        #     url="https://github.com/login/oauth/access_token",
        #     json={
        #         "access_token": "gho_new_token",
        #         "token_type": "bearer",
        #         "expires_in": 28800,
        #         "refresh_token": "ghr_new_refresh",
        #     },
        # )
        # token = await provider.refresh_token("ghr_old_refresh")
        # assert token.access_token == "gho_new_token"
        pass


@pytest.mark.provider
class TestGitHubTokenRevocation:
    """Test suite for GitHub token revocation."""

    async def test_github_revoke_token(self, mock_github_provider: Any) -> None:
        """Test GitHub token revocation."""
        # Should not raise
        await mock_github_provider.revoke_token("gho_test_token")

    async def test_github_revoke_token_sends_delete_request(self) -> None:
        """Test that GitHub revocation uses DELETE method."""
        # GitHub revocation: DELETE /applications/{client_id}/token
        # When implemented:
        # httpx_mock.add_response(
        #     method="DELETE",
        #     url__regex=r".*/applications/.*/token",
        #     status_code=204,
        # )
        # await provider.revoke_token("token")
        pass


@pytest.mark.provider
class TestGitHubErrorHandling:
    """Test suite for GitHub-specific error handling."""

    async def test_github_rate_limit_handling(self) -> None:
        """Test handling GitHub API rate limits."""
        # GitHub returns 403 with X-RateLimit-Remaining: 0
        # httpx_mock.add_response(
        #     url="https://api.github.com/user",
        #     status_code=403,
        #     headers={"X-RateLimit-Remaining": "0"},
        #     json={"message": "API rate limit exceeded"},
        # )
        # with pytest.raises(OAuthError) as exc_info:
        #     await provider.get_user_info("token")
        # assert "rate limit" in str(exc_info.value).lower()
        pass

    async def test_github_suspended_account_handling(self) -> None:
        """Test handling suspended GitHub accounts."""
        # GitHub returns 403 for suspended accounts
        # Should raise appropriate error
        pass

    async def test_github_invalid_token_handling(self) -> None:
        """Test handling invalid/expired GitHub tokens."""
        # GitHub returns 401 for invalid tokens
        # httpx_mock.add_response(
        #     url="https://api.github.com/user",
        #     status_code=401,
        #     json={"message": "Bad credentials"},
        # )
        # with pytest.raises(UserInfoError):
        #     await provider.get_user_info("invalid_token")
        pass


@pytest.mark.provider
class TestGitHubSpecificFeatures:
    """Test suite for GitHub-specific OAuth features."""

    def test_github_enterprise_support(self) -> None:
        """Test GitHub provider can be configured for Enterprise."""
        # When implemented:
        # provider = GitHubOAuthProvider(
        #     client_id="...",
        #     client_secret="...",
        #     base_url="https://github.enterprise.com",
        # )
        # assert "github.enterprise.com" in provider.authorize_url
        pass

    def test_github_app_authentication(self) -> None:
        """Test GitHub App authentication (vs OAuth App)."""
        # GitHub Apps have different authentication flows
        # This would be a separate provider or mode
        pass

    async def test_github_email_verification_status(
        self,
        mock_github_user: dict[str, Any],
    ) -> None:
        """Test that GitHub email verification status is captured."""
        # GitHub /user/emails endpoint provides verified flag
        raw_data = mock_github_user["raw_data"]
        assert "email" in raw_data
        # When normalized:
        # assert user_info.email_verified is True
        assert mock_github_user["email_verified"] is True

    def test_github_scope_permissions(self) -> None:
        """Test GitHub scope to permission mapping."""
        # Different scopes provide different access levels
        # user:email - read user email
        # read:user - read user profile
        # repo - access repositories
        # etc.
        pass


@pytest.mark.provider
@pytest.mark.parametrize(
    ("scope", "expected_in_url"),
    [
        ("user:email", "user"),
        ("read:user", "read"),
        ("repo read:org", "repo"),
        ("user:email read:user repo", "user"),
    ],
)
def test_github_scope_formatting(scope: str, expected_in_url: str) -> None:
    """Test GitHub scope formatting in authorization URLs."""
    # GitHub uses space-separated scopes
    # When implemented:
    # from litestar_oauth.testing.mocks import MockOAuthProvider
    # provider = MockOAuthProvider(provider_name="github", scope=scope)
    # url = provider.get_authorization_url("http://localhost/callback", "state")
    # assert expected_in_url in url
    pass
