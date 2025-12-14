"""Testing utilities for litestar-oauth.

This module provides mock implementations and pytest fixtures for testing OAuth
providers and services. These utilities can be used both internally for testing
litestar-oauth itself, and by downstream users for testing applications that
integrate with litestar-oauth.

The testing module includes:

- **Mocks**: Configurable mock objects for OAuth providers and services
- **Fixtures**: Reusable pytest fixtures for common testing scenarios
- **HTTP Mocks**: Mock HTTP responses for testing provider interactions

Example:
    Using the mock service in tests:

    >>> from litestar_oauth.testing import MockOAuthService, mock_github_user
    >>> service = MockOAuthService()
    >>> await service.register_mock_provider("github")

    Using pytest fixtures:

    >>> from litestar_oauth.testing.fixtures import (
    ...     mock_oauth_service,
    ...     mock_github_user,
    ...     mock_oauth_token,
    ... )
    >>>
    >>> def test_oauth_flow(mock_oauth_service, mock_oauth_token):
    ...     # Test implementation
    ...     pass
"""

from __future__ import annotations

from litestar_oauth.testing.fixtures import (
    mock_discord_provider,
    mock_discord_user,
    mock_github_provider,
    mock_github_user,
    mock_google_provider,
    mock_google_user,
    mock_httpx_client,
    mock_oauth_service,
    mock_oauth_state,
    mock_oauth_token,
)
from litestar_oauth.testing.mocks import (
    MockHTTPResponse,
    MockOAuthProvider,
    MockOAuthService,
)

__all__ = [
    # Mocks
    "MockHTTPResponse",
    "MockOAuthProvider",
    "MockOAuthService",
    # Fixtures
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
