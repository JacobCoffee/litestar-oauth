# litestar-oauth Testing Suite

Comprehensive test suite for litestar-oauth with 251 test cases across 68 test classes, targeting 80%+ code coverage.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and pytest configuration
├── unit/                                # Unit tests (112 tests)
│   ├── test_types.py                    # OAuthUserInfo, OAuthToken, OAuthState tests
│   ├── test_exceptions.py               # Exception hierarchy tests
│   ├── test_base.py                     # BaseOAuthProvider tests
│   ├── test_service.py                  # OAuthService and state management tests
│   └── providers/                       # Provider-specific tests
│       ├── test_github.py               # GitHub OAuth provider tests
│       ├── test_google.py               # Google OAuth provider tests
│       └── test_discord.py              # Discord OAuth provider tests
└── integration/                         # Integration tests (89 tests)
    └── test_litestar_plugin.py          # Full Litestar plugin integration tests
```

## Testing Utilities

The `litestar_oauth.testing` module provides reusable mocks and fixtures:

### Mocks (`litestar_oauth.testing.mocks`)

- **MockHTTPResponse**: Mock HTTP responses for testing provider HTTP interactions
- **MockOAuthProvider**: Configurable mock OAuth provider
- **MockOAuthService**: Pre-configured mock OAuth service

### Fixtures (`litestar_oauth.testing.fixtures`)

- `mock_oauth_service`: MockOAuthService instance
- `mock_github_user`: Sample GitHub user data
- `mock_google_user`: Sample Google user data
- `mock_discord_user`: Sample Discord user data
- `mock_oauth_token`: Sample OAuth token data
- `mock_oauth_state`: Sample OAuth state data
- `mock_github_provider`: Configured GitHub mock provider
- `mock_google_provider`: Configured Google mock provider
- `mock_discord_provider`: Configured Discord mock provider
- `mock_httpx_client`: Mock httpx.AsyncClient

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Provider-specific tests
pytest -m provider

# Specific provider tests
pytest tests/unit/providers/test_github.py
pytest tests/unit/providers/test_google.py
pytest tests/unit/providers/test_discord.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=litestar_oauth --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Run Async Tests

All async tests use pytest-asyncio with automatic async mode:

```bash
pytest -v  # Automatically handles async tests
```

## Test Categories

### Unit Tests (tests/unit/)

#### test_types.py
- OAuthUserInfo creation and validation
- OAuthToken expiry calculation
- OAuthState management
- Type immutability and defaults
- Provider-specific normalization

#### test_exceptions.py
- Exception hierarchy validation
- Error context preservation
- Provider-specific error handling
- CSRF and security-related errors

#### test_base.py
- Protocol compliance
- Abstract method enforcement
- Authorization URL generation
- Token exchange
- User info retrieval
- Token refresh and revocation

#### test_service.py
- Provider registration
- State creation and validation
- OAuth flow orchestration
- Error handling
- Configuration management

#### test_github.py (Provider Tests)
- GitHub-specific endpoints
- Authorization URL with GitHub params
- Token exchange with GitHub API
- User info normalization
- Private email handling
- Rate limit handling
- GitHub Enterprise support

#### test_google.py (Provider Tests)
- Google OAuth/OIDC endpoints
- ID token parsing and validation
- Consent and access_type parameters
- Google Workspace integration
- Refresh token handling
- OIDC discovery

#### test_discord.py (Provider Tests)
- Discord OAuth endpoints
- Bot authorization flow
- Guild and connection scopes
- Avatar URL handling (static/animated)
- New username system
- Webhook integration

### Integration Tests (tests/integration/)

#### test_litestar_plugin.py
- Plugin initialization
- Route registration
- Full OAuth flow
- Dependency injection
- Guards and middleware
- Session management
- Error handling
- Multi-provider support

## Using Testing Utilities

### Example: Testing with Mock Provider

```python
from litestar_oauth.testing import MockOAuthProvider

async def test_my_oauth_flow():
    provider = MockOAuthProvider(
        provider_name="github",
        access_token="test_token",
        user_info=custom_user_info,
    )

    # Test authorization URL
    url = provider.get_authorization_url("http://localhost/callback", "state123")
    assert "state=state123" in url

    # Test token exchange
    token = await provider.exchange_code("code", "http://localhost/callback")
    assert token.access_token == "test_token"
```

### Example: Testing with Fixtures

```python
from litestar_oauth.testing.fixtures import mock_oauth_service

async def test_service_integration(mock_oauth_service):
    await mock_oauth_service.register_mock_provider("github")

    state = await mock_oauth_service.create_state(
        provider="github",
        redirect_uri="http://localhost/callback"
    )

    assert state is not None
```

### Example: Testing with pytest-httpx

```python
import pytest
from pytest_httpx import HTTPXMock

async def test_github_token_exchange(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://github.com/login/oauth/access_token",
        json={"access_token": "gho_test", "token_type": "bearer"}
    )

    # Your provider code that makes HTTP request
    # Will receive mocked response
```

## Coverage Goals

- **Overall Target**: 80%+ code coverage
- **Critical Paths**: 100% coverage
  - Token exchange flows
  - State validation
  - Error handling
- **Provider Implementations**: 85%+ coverage
- **Plugin Integration**: 75%+ coverage

## Test Markers

Tests are automatically marked based on location:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.provider`: Provider-specific tests
- `@pytest.mark.slow`: Slow-running tests

## Test Configuration

Pytest configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-v", "--strict-markers", "--tb=short"]
markers = [
    "unit: mark test as unit test",
    "integration: mark test as integration test",
]
```

## Dependencies

Required test dependencies (in `pyproject.toml`):

```toml
[dependency-groups]
test = [
    "httpx>=0.27.0",
    "litestar[testing]>=2.0.0",
    "pytest>=8.1.1",
    "pytest-asyncio>=0.23.6",
    "pytest-cov>=4.1.0",
    "pytest-httpx>=0.30.0",
    "pytest-sugar>=1.1.1",
    "respx>=0.21.0",
]
```

## Writing New Tests

### Test Template

```python
"""Tests for [feature].

Description of what this test module covers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any


class TestFeatureName:
    """Test suite for [feature]."""

    def test_basic_functionality(self) -> None:
        """Test basic feature functionality."""
        # Arrange

        # Act

        # Assert
        pass

    async def test_async_functionality(self) -> None:
        """Test async feature functionality."""
        # Arrange

        # Act

        # Assert
        pass
```

### Best Practices

1. **Use descriptive test names**: Test name should describe what is being tested
2. **One assertion per test**: Focus on single behavior
3. **Use fixtures**: Reuse common setup via fixtures
4. **Mock external calls**: Use pytest-httpx for HTTP mocking
5. **Test error cases**: Don't just test happy paths
6. **Use parametrize**: Test multiple inputs with `@pytest.mark.parametrize`
7. **Add docstrings**: Explain what each test validates
8. **Keep tests isolated**: Tests should not depend on each other

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Release tags

GitHub Actions workflow ensures:
- All tests pass
- Coverage meets threshold
- No test warnings or failures

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure dependencies installed
uv sync --group test
```

**Async Test Failures**
```bash
# Check pytest-asyncio is installed and configured
pytest --asyncio-mode=auto
```

**Coverage Not Showing**
```bash
# Ensure pytest-cov is installed
pytest --cov=litestar_oauth --cov-report=term-missing
```

## Contributing Tests

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain 80%+ coverage
4. Update this README if adding new test categories
5. Add fixtures for reusable test data

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-httpx documentation](https://colin-b.github.io/pytest_httpx/)
- [Litestar testing guide](https://docs.litestar.dev/latest/usage/testing.html)
