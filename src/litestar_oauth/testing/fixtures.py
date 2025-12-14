"""Pytest fixtures for testing OAuth providers and services.

This module provides reusable pytest fixtures that can be imported into test suites
to simplify testing of OAuth flows, providers, and integrations.

Usage:
    Import fixtures in your conftest.py or test files:

    >>> from litestar_oauth.testing.fixtures import (
    ...     mock_oauth_service,
    ...     mock_github_user,
    ...     mock_google_user,
    ...     mock_oauth_token,
    ... )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from litestar_oauth.testing.mocks import MockOAuthService


@pytest.fixture
def mock_oauth_service() -> MockOAuthService:
    """Provide a pre-configured MockOAuthService for testing.

    Returns:
        MockOAuthService instance with no providers registered

    Example:
        >>> def test_oauth_service(mock_oauth_service):
        ...     provider = await mock_oauth_service.register_mock_provider("github")
        ...     assert provider.provider_name == "github"
    """
    from litestar_oauth.testing.mocks import MockOAuthService

    return MockOAuthService()


@pytest.fixture
def mock_github_user() -> dict[str, Any]:
    """Provide sample GitHub user data for testing.

    Returns:
        Dict with OAuthUserInfo-compatible data for GitHub

    Example:
        >>> def test_github_user(mock_github_user):
        ...     assert mock_github_user["provider"] == "github"
        ...     assert mock_github_user["email_verified"] is True
    """
    return {
        "provider": "github",
        "oauth_id": "12345678",
        "email": "octocat@github.com",
        "email_verified": True,
        "username": "octocat",
        "first_name": "The",
        "last_name": "Octocat",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
        "profile_url": "https://github.com/octocat",
        "raw_data": {
            "id": 12345678,
            "login": "octocat",
            "name": "The Octocat",
            "email": "octocat@github.com",
            "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
            "html_url": "https://github.com/octocat",
            "bio": "GitHub mascot and developer",
            "location": "San Francisco",
            "company": "GitHub",
            "blog": "https://github.blog",
            "public_repos": 8,
            "followers": 1000,
            "following": 100,
        },
    }


@pytest.fixture
def mock_google_user() -> dict[str, Any]:
    """Provide sample Google user data for testing.

    Returns:
        Dict with OAuthUserInfo-compatible data for Google

    Example:
        >>> def test_google_user(mock_google_user):
        ...     assert mock_google_user["provider"] == "google"
        ...     assert mock_google_user["email_verified"] is True
    """
    return {
        "provider": "google",
        "oauth_id": "123456789012345678901",
        "email": "testuser@gmail.com",
        "email_verified": True,
        "username": "",  # Google doesn't provide username
        "first_name": "Test",
        "last_name": "User",
        "avatar_url": "https://lh3.googleusercontent.com/a/default-user",
        "profile_url": "",  # Google doesn't provide public profile URL
        "raw_data": {
            "sub": "123456789012345678901",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://lh3.googleusercontent.com/a/default-user",
            "email": "testuser@gmail.com",
            "email_verified": True,
            "locale": "en",
            "hd": "gmail.com",  # Hosted domain for workspace accounts
        },
    }


@pytest.fixture
def mock_discord_user() -> dict[str, Any]:
    """Provide sample Discord user data for testing.

    Returns:
        Dict with OAuthUserInfo-compatible data for Discord

    Example:
        >>> def test_discord_user(mock_discord_user):
        ...     assert mock_discord_user["provider"] == "discord"
        ...     assert mock_discord_user["username"] == "TestUser"
    """
    return {
        "provider": "discord",
        "oauth_id": "987654321098765432",
        "email": "testuser@discord.com",
        "email_verified": True,
        "username": "TestUser",
        "first_name": "",  # Discord doesn't provide name split
        "last_name": "",
        "avatar_url": "https://cdn.discordapp.com/avatars/987654321098765432/a_1234567890abcdef.png",
        "profile_url": "",  # Discord doesn't provide public profile URL
        "raw_data": {
            "id": "987654321098765432",
            "username": "TestUser",
            "discriminator": "0",  # New username system (no discriminator)
            "global_name": "Test User",
            "avatar": "a_1234567890abcdef",
            "email": "testuser@discord.com",
            "verified": True,
            "flags": 0,
            "premium_type": 2,
            "public_flags": 0,
            "locale": "en-US",
            "mfa_enabled": True,
        },
    }


@pytest.fixture
def mock_oauth_token() -> dict[str, Any]:
    """Provide sample OAuth token data for testing.

    Returns:
        Dict with OAuthToken-compatible data

    Example:
        >>> def test_oauth_token(mock_oauth_token):
        ...     assert mock_oauth_token["access_token"] == "gho_1234567890abcdef"
        ...     assert mock_oauth_token["token_type"] == "Bearer"
    """
    return {
        "access_token": "gho_1234567890abcdef",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "ghr_0987654321fedcba",
        "scope": "user:email read:user",
        "id_token": None,
        "raw_response": {
            "access_token": "gho_1234567890abcdef",
            "token_type": "bearer",
            "scope": "user:email read:user",
            "refresh_token": "ghr_0987654321fedcba",
            "expires_in": 3600,
            "created_at": 1704067200,
        },
    }


@pytest.fixture
def mock_oauth_state() -> dict[str, Any]:
    """Provide sample OAuth state data for testing.

    Returns:
        Dict with OAuthState-compatible data

    Example:
        >>> def test_oauth_state(mock_oauth_state):
        ...     assert mock_oauth_state["provider"] == "github"
        ...     assert "state" in mock_oauth_state
    """
    return {
        "state": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
        "provider": "github",
        "redirect_uri": "http://localhost:8000/auth/github/callback",
        "created_at": "2024-01-01T00:00:00Z",
        "next_url": "/dashboard",
        "extra_data": {"user_agent": "Mozilla/5.0"},
    }


@pytest.fixture
def mock_github_provider() -> Any:
    """Provide a configured MockOAuthProvider for GitHub testing.

    Returns:
        MockOAuthProvider instance configured for GitHub

    Example:
        >>> async def test_github_provider(mock_github_provider):
        ...     url = mock_github_provider.get_authorization_url(
        ...         "http://localhost/callback", "state123"
        ...     )
        ...     assert "github.com" in url
    """
    from litestar_oauth.testing.mocks import MockOAuthProvider

    return MockOAuthProvider(
        provider_name="github",
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        user_info_url="https://api.github.com/user",
        scope="user:email",
        access_token="gho_mock_github_token",
    )


@pytest.fixture
def mock_google_provider() -> Any:
    """Provide a configured MockOAuthProvider for Google testing.

    Returns:
        MockOAuthProvider instance configured for Google

    Example:
        >>> async def test_google_provider(mock_google_provider):
        ...     url = mock_google_provider.get_authorization_url(
        ...         "http://localhost/callback", "state456"
        ...     )
        ...     assert "accounts.google.com" in url
    """
    from litestar_oauth.testing.mocks import MockOAuthProvider

    return MockOAuthProvider(
        provider_name="google",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v3/userinfo",
        scope="openid email profile",
        access_token="ya29.mock_google_token",
    )


@pytest.fixture
def mock_discord_provider() -> Any:
    """Provide a configured MockOAuthProvider for Discord testing.

    Returns:
        MockOAuthProvider instance configured for Discord

    Example:
        >>> async def test_discord_provider(mock_discord_provider):
        ...     url = mock_discord_provider.get_authorization_url(
        ...         "http://localhost/callback", "state789"
        ...     )
        ...     assert "discord.com" in url
    """
    from litestar_oauth.testing.mocks import MockOAuthProvider

    return MockOAuthProvider(
        provider_name="discord",
        authorize_url="https://discord.com/api/oauth2/authorize",
        token_url="https://discord.com/api/oauth2/token",
        user_info_url="https://discord.com/api/users/@me",
        scope="identify email",
        access_token="mock_discord_token",
    )


@pytest.fixture
async def mock_httpx_client() -> Any:
    """Provide a mock httpx.AsyncClient for testing HTTP interactions.

    Returns:
        Mock httpx.AsyncClient that can be configured with pytest-httpx

    Example:
        >>> async def test_http_client(mock_httpx_client, httpx_mock):
        ...     httpx_mock.add_response(json={"status": "ok"})
        ...     response = await mock_httpx_client.get("https://api.example.com")
        ...     assert response.json() == {"status": "ok"}

    Note:
        This fixture requires pytest-httpx to be installed for proper mocking.
    """
    from unittest.mock import AsyncMock

    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.aclose = AsyncMock()
    return client


__all__ = [
    "mock_discord_provider",
    "mock_discord_user",
    "mock_github_provider",
    "mock_github_user",
    "mock_google_provider",
    "mock_google_user",
    "mock_httpx_client",
    "mock_oauth_service",
    "mock_oauth_state",
    "mock_oauth_token",
]
