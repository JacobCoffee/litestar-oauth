# litestar-oauth - Development Plan

> Async OAuth2 authentication library with pluggable providers and optional Litestar integration

## Project Overview

**Objective**: Create a standalone, provider-agnostic OAuth2 library that can work independently or integrate seamlessly with Litestar via plugin.

**Reference Projects**:
- `litestar-storages` - Provider pattern (backends → providers), ABC base class, optional dependencies
- `litestar-workflows` - Plugin architecture, contrib modules, web integration
- `pytest-routes` - Pytest plugin patterns, minimal dependencies
- `litestar-pydotorg` - Working OAuth implementation to extract (GitHub, Google, Discord)

---

## Architecture

### Core Design Principles

1. **Zero Required Dependencies** - Core library has no dependencies; providers bring their own (httpx, etc.)
2. **Provider-Agnostic** - Abstract base class defines interface; providers implement specifics
3. **Async-First** - All operations are async; sync wrappers available via contrib
4. **Framework-Agnostic** - Works standalone; Litestar integration via optional plugin
5. **Type-Safe** - Full type annotations, runtime_checkable protocols

### Directory Structure

```
litestar-oauth/
├── src/
│   └── litestar_oauth/
│       ├── __init__.py              # Public API exports
│       ├── __metadata__.py          # Version, author info
│       ├── base.py                  # OAuthProvider protocol + BaseOAuthProvider ABC
│       ├── types.py                 # OAuthUserInfo, OAuthToken, OAuthState, etc.
│       ├── exceptions.py            # OAuthError, ProviderNotConfiguredError, etc.
│       ├── service.py               # OAuthService - provider registry + state management
│       │
│       ├── providers/               # OAuth2 provider implementations
│       │   ├── __init__.py
│       │   ├── github.py            # GitHub OAuth
│       │   ├── google.py            # Google OAuth
│       │   ├── discord.py           # Discord OAuth
│       │   ├── apple.py             # Apple Sign-In
│       │   ├── microsoft.py         # Microsoft/Azure AD
│       │   ├── twitter.py           # Twitter/X OAuth2
│       │   ├── facebook.py          # Facebook/Meta OAuth
│       │   ├── linkedin.py          # LinkedIn OAuth
│       │   ├── gitlab.py            # GitLab OAuth
│       │   ├── bitbucket.py         # Bitbucket OAuth
│       │   └── generic.py           # Generic OAuth2 provider (OIDC-compliant)
│       │
│       ├── contrib/                 # Optional integrations
│       │   ├── __init__.py
│       │   ├── litestar/            # Litestar plugin
│       │   │   ├── __init__.py
│       │   │   ├── plugin.py        # OAuthPlugin (InitPluginProtocol)
│       │   │   ├── config.py        # OAuthConfig dataclass
│       │   │   ├── guards.py        # OAuthGuard, RequireOAuthSession
│       │   │   ├── middleware.py    # OAuthStateMiddleware
│       │   │   ├── dependencies.py  # Provide[OAuthService], oauth_user_info
│       │   │   ├── controllers.py   # OAuthController with /login, /callback routes
│       │   │   └── dto.py           # Litestar DTOs for API responses
│       │   ├── starlette/           # Starlette/FastAPI integration
│       │   │   ├── __init__.py
│       │   │   └── middleware.py
│       │   ├── flask/               # Flask integration
│       │   │   ├── __init__.py
│       │   │   └── blueprint.py
│       │   └── sync.py              # Sync wrapper utilities
│       │
│       └── testing/                 # Test utilities
│           ├── __init__.py
│           ├── mocks.py             # MockOAuthProvider, MockOAuthService
│           └── fixtures.py          # pytest fixtures
│
├── tests/
│   ├── unit/
│   │   ├── test_base.py
│   │   ├── test_service.py
│   │   └── providers/
│   │       ├── test_github.py
│   │       ├── test_google.py
│   │       └── test_discord.py
│   ├── integration/
│   │   ├── test_litestar_plugin.py
│   │   └── test_oauth_flows.py
│   └── conftest.py
│
├── docs/
│   ├── conf.py
│   ├── index.rst
│   ├── getting-started.rst
│   ├── providers/
│   │   ├── index.rst
│   │   ├── github.rst
│   │   └── custom.rst
│   └── api/
│       └── index.rst
│
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── Makefile
```

---

## Core Abstractions

### Protocol Definition (`base.py`)

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthToken, OAuthUserInfo


@runtime_checkable
class OAuthProvider(Protocol):
    """Async OAuth2 provider protocol.

    All provider implementations must implement this protocol to ensure
    consistent behavior across different OAuth2 providers.
    """

    @property
    def provider_name(self) -> str:
        """Unique identifier for this provider (e.g., 'github', 'google')."""
        ...

    @property
    def authorize_url(self) -> str:
        """OAuth2 authorization endpoint URL."""
        ...

    @property
    def token_url(self) -> str:
        """OAuth2 token exchange endpoint URL."""
        ...

    @property
    def user_info_url(self) -> str:
        """User info endpoint URL (for fetching profile after auth)."""
        ...

    @property
    def scope(self) -> str:
        """Default OAuth2 scopes to request."""
        ...

    def is_configured(self) -> bool:
        """Check if provider has required credentials configured."""
        ...

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        *,
        scope: str | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> str:
        """Generate authorization URL for OAuth2 flow initiation."""
        ...

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthToken:
        """Exchange authorization code for access token."""
        ...

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> OAuthToken:
        """Refresh an expired access token."""
        ...

    async def get_user_info(
        self,
        access_token: str,
    ) -> OAuthUserInfo:
        """Fetch user profile information using access token."""
        ...

    async def revoke_token(
        self,
        token: str,
        *,
        token_type_hint: str = "access_token",
    ) -> None:
        """Revoke an access or refresh token."""
        ...
```

### Type Definitions (`types.py`)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class OAuthUserInfo:
    """Normalized user information from OAuth provider."""

    provider: str
    oauth_id: str
    email: str
    email_verified: bool = False
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    avatar_url: str = ""
    profile_url: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass(frozen=True, slots=True)
class OAuthToken:
    """OAuth2 token response."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None
    id_token: str | None = None  # For OIDC
    raw_response: dict[str, Any] = field(default_factory=dict)

    @property
    def expires_at(self) -> datetime | None:
        if self.expires_in:
            return datetime.now() + timedelta(seconds=self.expires_in)
        return None


@dataclass
class OAuthState:
    """CSRF state for OAuth flow."""

    state: str
    provider: str
    redirect_uri: str
    created_at: datetime = field(default_factory=datetime.now)
    next_url: str | None = None
    extra_data: dict[str, Any] = field(default_factory=dict)
```

---

## pyproject.toml Structure

```toml
[build-system]
build-backend = "uv_build"
requires = ["uv_build>=0.9.11,<0.10.0"]

[dependency-groups]
docs = [
    "litestar>=2.0.0",
    "myst-parser>=4.0.0",
    "shibuya>=2024.0.0",
    "sphinx>=7.0.0",
    "sphinx-autodoc-typehints>=2.0.0",
    "sphinx-copybutton>=0.5.0",
]
lint = [
    "codespell>=2.2.6",
    "prek>=0.2.18",
    "ruff>=0.9.0",
    "ty>=0.0.1a7",
]
test = [
    "httpx>=0.27.0",
    "litestar[testing]>=2.0.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "pytest-httpx>=0.30.0",
    "respx>=0.21.0",
]
dev = [
    {include-group = "docs"},
    {include-group = "lint"},
    {include-group = "test"},
]

[project]
name = "litestar-oauth"
version = "0.1.0"
description = "Async OAuth2 authentication library with optional Litestar integration"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10,<3.14"
authors = [{name = "Jacob Coffee", email = "jacob@z7x.org"}]
keywords = ["oauth", "oauth2", "authentication", "litestar", "async"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Internet :: WWW/HTTP :: Session",
    "Topic :: Security",
    "Typing :: Typed",
]
dependencies = []  # No required dependencies!

[project.optional-dependencies]
# Core HTTP client (pick one)
httpx = ["httpx>=0.27.0"]
aiohttp = ["aiohttp>=3.9.0"]

# Provider-specific extras (for providers with special requirements)
apple = ["pyjwt>=2.8.0", "cryptography>=41.0.0"]  # Apple requires JWT signing
microsoft = ["msal>=1.26.0"]  # Optional: use Microsoft's official library

# Framework integrations
litestar = ["litestar>=2.0.0"]
starlette = ["starlette>=0.27.0"]
flask = ["flask>=2.0.0", "asgiref>=3.7.0"]

# All providers with recommended HTTP client
all = [
    "httpx>=0.27.0",
    "pyjwt>=2.8.0",
    "cryptography>=41.0.0",
    "litestar>=2.0.0",
]

[project.urls]
Homepage = "https://github.com/JacobCoffee/litestar-oauth"
Documentation = "https://jacobcoffee.github.io/litestar-oauth"
Repository = "https://github.com/JacobCoffee/litestar-oauth"
Changelog = "https://github.com/JacobCoffee/litestar-oauth/releases/"
Discord = "https://discord.gg/litestar-919193495116337154"

[tool.uv]
default-groups = ["dev"]

[tool.ruff]
fix = true
line-length = 120
src = ["src/litestar_oauth", "tests"]
target-version = "py310"

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "COM812", "ISC001", "EM", "TRY003", "TD"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Development Phases

### Phase 1: Core Foundation (Week 1-2)

| Task | Priority | Description |
|------|----------|-------------|
| Project scaffold | HIGH | Create directory structure, pyproject.toml, Makefile |
| Base abstractions | HIGH | `OAuthProvider` protocol, `BaseOAuthProvider` ABC |
| Type definitions | HIGH | `OAuthUserInfo`, `OAuthToken`, `OAuthState` dataclasses |
| Exceptions | HIGH | `OAuthError`, `ProviderNotConfiguredError`, `TokenExchangeError` |
| OAuthService | HIGH | Provider registry, state management, validation |

**Deliverable**: Core library importable with no dependencies

### Phase 2: Provider Implementations (Week 2-3)

| Provider | Priority | Notes |
|----------|----------|-------|
| GitHub | HIGH | Extract from litestar-pydotorg, add refresh token support |
| Google | HIGH | Extract from litestar-pydotorg, add OIDC id_token parsing |
| Discord | HIGH | Extract from litestar-pydotorg |
| Generic OIDC | MEDIUM | Configurable provider for any OIDC-compliant IdP |
| Microsoft/Azure | MEDIUM | Azure AD + Microsoft personal accounts |
| Apple | MEDIUM | Requires JWT client secret generation |
| GitLab | LOW | Similar to GitHub |
| Twitter/X | LOW | OAuth 2.0 with PKCE |
| Facebook | LOW | Meta OAuth |
| LinkedIn | LOW | Professional network OAuth |

**Deliverable**: Working providers with 80%+ test coverage

### Phase 3: Litestar Plugin (Week 3-4)

| Task | Priority | Description |
|------|----------|-------------|
| OAuthConfig | HIGH | Plugin configuration dataclass |
| OAuthPlugin | HIGH | `InitPluginProtocol` implementation |
| Dependencies | HIGH | `Provide[OAuthService]`, `oauth_user_info` |
| Controllers | HIGH | `/auth/{provider}/login`, `/auth/{provider}/callback` |
| Middleware | MEDIUM | State validation, CSRF protection |
| Guards | MEDIUM | `OAuthGuard`, `RequireOAuthSession` |
| DTOs | LOW | API response schemas |

**Deliverable**: Drop-in Litestar plugin with auto-configured routes

### Phase 4: Testing & Documentation (Week 4-5)

| Task | Priority | Description |
|------|----------|-------------|
| Unit tests | HIGH | Provider logic, service, state management |
| Integration tests | HIGH | Full OAuth flows with mocked responses |
| Test fixtures | HIGH | pytest fixtures in `litestar_oauth.testing` |
| MockOAuthProvider | HIGH | For downstream testing |
| Sphinx docs | MEDIUM | API reference, getting started guide |
| Provider guides | MEDIUM | Setup instructions for each provider |

**Deliverable**: 90%+ test coverage, published docs

### Phase 5: Additional Integrations (Future)

| Task | Priority | Description |
|------|----------|-------------|
| Starlette/FastAPI | LOW | Middleware + route helpers |
| Flask | LOW | Blueprint with routes |
| CLI tool | LOW | `litestar-oauth init` for quick setup |
| Token storage | LOW | Redis/database token persistence |

---

## Key Implementation Details

### State Management Strategy

```python
class OAuthStateManager:
    """Manages CSRF state for OAuth flows.

    Default: In-memory with TTL
    Optional: Redis backend for distributed deployments
    """

    async def create_state(
        self,
        provider: str,
        redirect_uri: str,
        *,
        next_url: str | None = None,
        ttl: int = 600,  # 10 minutes
    ) -> str:
        """Generate cryptographically secure state token."""
        ...

    async def validate_state(self, state: str) -> OAuthState:
        """Validate and consume state (one-time use)."""
        ...
```

### Provider Registration

```python
# Automatic registration via entry points (future)
# Manual registration for explicit control

from litestar_oauth import OAuthService
from litestar_oauth.providers import GitHubOAuthProvider, GoogleOAuthProvider

service = OAuthService()
service.register(GitHubOAuthProvider(client_id="...", client_secret="..."))
service.register(GoogleOAuthProvider(client_id="...", client_secret="..."))

# Or via config
service = OAuthService.from_config({
    "github": {"client_id": "...", "client_secret": "..."},
    "google": {"client_id": "...", "client_secret": "..."},
})
```

### Litestar Plugin Usage

```python
from litestar import Litestar
from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

app = Litestar(
    plugins=[
        OAuthPlugin(
            config=OAuthConfig(
                github_client_id="...",
                github_client_secret="...",
                google_client_id="...",
                google_client_secret="...",
                redirect_base_url="https://example.com",
                route_prefix="/auth",  # /auth/github/login, /auth/github/callback
                success_redirect="/dashboard",
                failure_redirect="/login?error=oauth",
            )
        )
    ],
)
```

---

## Testing Strategy

### Mocking External Calls

```python
# Use pytest-httpx or respx for mocking HTTP calls
import pytest
from litestar_oauth.providers import GitHubOAuthProvider

@pytest.fixture
def github_provider():
    return GitHubOAuthProvider(
        client_id="test-client-id",
        client_secret="test-client-secret",
    )

async def test_github_exchange_code(github_provider, httpx_mock):
    httpx_mock.add_response(
        url="https://github.com/login/oauth/access_token",
        json={"access_token": "gho_xxxx", "token_type": "bearer"},
    )

    token = await github_provider.exchange_code("test-code", "http://localhost/callback")

    assert token.access_token == "gho_xxxx"
```

### Test Fixtures Export

```python
# In litestar_oauth.testing.fixtures
import pytest
from litestar_oauth.testing.mocks import MockOAuthProvider, MockOAuthService

@pytest.fixture
def mock_oauth_service() -> MockOAuthService:
    """Pre-configured mock OAuth service for testing."""
    return MockOAuthService()

@pytest.fixture
def mock_github_user() -> OAuthUserInfo:
    """Sample GitHub user for testing."""
    return OAuthUserInfo(
        provider="github",
        oauth_id="12345",
        email="test@example.com",
        username="testuser",
        email_verified=True,
    )
```

---

## Migration Path from litestar-pydotorg

1. Extract `src/pydotorg/core/auth/oauth.py` → `src/litestar_oauth/`
2. Split into `base.py`, `types.py`, `providers/github.py`, etc.
3. Add generic configuration instead of `Settings` dependency
4. Add missing features: refresh tokens, token revocation, PKCE
5. Write comprehensive tests
6. Create Litestar plugin wrapping the extracted code

---

## Success Criteria

- [ ] Zero required dependencies in core
- [ ] 90%+ test coverage
- [ ] Working providers: GitHub, Google, Discord, Generic OIDC
- [ ] Litestar plugin with auto-configured routes
- [ ] Published to PyPI
- [ ] Sphinx documentation hosted on GitHub Pages
- [ ] Used in litestar-pydotorg (dogfooding)

---

*Last updated: 2025-12-14*
