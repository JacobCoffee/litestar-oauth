"""Shared pytest configuration and fixtures for litestar-oauth tests.

This module provides common fixtures and configuration for all test suites,
including OAuth mocks, HTTP client mocking, and test data generators.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


# Re-export all testing fixtures for convenience
pytest_plugins = ["litestar_oauth.testing.fixtures"]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio backend for async tests.

    Returns:
        Backend name ("asyncio")
    """
    return "asyncio"


@pytest.fixture
def mock_http_responses() -> dict[str, dict[str, Any]]:
    """Provide common HTTP response mocks for OAuth providers.

    Returns:
        Dict mapping provider names to response mocks

    Example:
        >>> def test_with_responses(mock_http_responses):
        ...     github_token = mock_http_responses["github"]["token"]
        ...     assert "access_token" in github_token
    """
    return {
        "github": {
            "token": {
                "access_token": "gho_1234567890abcdef",
                "token_type": "bearer",
                "scope": "user:email",
            },
            "user": {
                "id": 12345678,
                "login": "octocat",
                "email": "octocat@github.com",
                "name": "The Octocat",
                "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
            },
        },
        "google": {
            "token": {
                "access_token": "ya29.a0AfH6SMBx...",
                "token_type": "Bearer",
                "expires_in": 3599,
                "scope": "openid email profile",
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
            },
            "user": {
                "sub": "123456789012345678901",
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "picture": "https://lh3.googleusercontent.com/a/default-user",
                "email": "testuser@gmail.com",
                "email_verified": True,
            },
        },
        "discord": {
            "token": {
                "access_token": "6qrZcUqja7812RVdnEKjpzOL4CvHBFG",
                "token_type": "Bearer",
                "expires_in": 604800,
                "refresh_token": "D43f5y0ahjqew82jZ4NViEr2YafMKhue",
                "scope": "identify email",
            },
            "user": {
                "id": "987654321098765432",
                "username": "TestUser",
                "discriminator": "0",
                "global_name": "Test User",
                "avatar": "a_1234567890abcdef",
                "email": "testuser@discord.com",
                "verified": True,
            },
        },
    }


@pytest.fixture
async def async_context() -> AsyncGenerator[None, None]:
    """Provide async context for tests that need explicit async setup/teardown.

    Yields:
        None (provides async context)

    Example:
        >>> async def test_with_context(async_context):
        ...     # Async test code here
        ...     await some_async_operation()
    """
    # Setup
    return
    # Teardown


@pytest.fixture
def oauth_callback_params() -> dict[str, str]:
    """Provide sample OAuth callback query parameters.

    Returns:
        Dict with code and state parameters

    Example:
        >>> def test_callback(oauth_callback_params):
        ...     assert "code" in oauth_callback_params
        ...     assert "state" in oauth_callback_params
    """
    return {
        "code": "abc123def456",
        "state": "xyz789uvw012",
    }


@pytest.fixture
def oauth_error_params() -> dict[str, str]:
    """Provide sample OAuth error callback parameters.

    Returns:
        Dict with error and error_description parameters

    Example:
        >>> def test_error_callback(oauth_error_params):
        ...     assert oauth_error_params["error"] == "access_denied"
    """
    return {
        "error": "access_denied",
        "error_description": "The user denied authorization",
        "state": "xyz789uvw012",
    }


@pytest.fixture
def redirect_uris() -> dict[str, str]:
    """Provide common redirect URIs for testing.

    Returns:
        Dict mapping context names to redirect URIs

    Example:
        >>> def test_redirect(redirect_uris):
        ...     assert redirect_uris["local"] == "http://localhost:8000/auth/callback"
    """
    return {
        "local": "http://localhost:8000/auth/callback",
        "production": "https://example.com/auth/callback",
        "github": "http://localhost:8000/auth/github/callback",
        "google": "http://localhost:8000/auth/google/callback",
        "discord": "http://localhost:8000/auth/discord/callback",
    }


# Mark configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers.

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "provider: mark test as provider-specific")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Collection configuration
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to add automatic markers.

    Args:
        config: Pytest configuration object
        items: List of collected test items
    """
    for item in items:
        # Auto-mark tests based on path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Auto-mark provider tests
        if "providers" in str(item.fspath):
            item.add_marker(pytest.mark.provider)
