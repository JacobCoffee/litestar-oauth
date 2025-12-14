# litestar-oauth

OAuth2 authentication plugin for Litestar with support for GitHub, Google, Discord, and custom OAuth2/OIDC providers.

## Project Rules & Conventions

### Git & Commits

- **Atomic commits** - each commit is a logical unit of work
- **Conventional commits** - `feat:`, `fix:`, `docs:`, `chore:`, `test:`
- **Run `make lint` before committing** - lint, format, type-check must pass
- **All PR checks must pass** - use `gh pr checks` to verify
  When Pull requests are made, run `gh pr view $PR_NUMBER --web` so that i can see it.
  Address all PR comments, comment on those review comments saying you fixed it with the commit
  hash

### Python & Tooling

- **Always use `uv run`** - never call `python`/`python3` directly
- **Use Makefile targets** - `make help` shows all commands
- **Ruff for linting/formatting** - `make lint`
- **ty for type checking** - included in `make lint`
- **PEP 649 annotations** - use `from __future__ import annotations` in all modules

### Agent Workflow

- **Dispatch subagents in parallel** - don't serialize when tasks are independent
- **Use specialized agents** - docs expert for docs, python engineer for code
- **Dispatch doc agent after code is done** - for documenting new features
- **Run `make lint` and tests before signing off**

### CI/CD

- **Pin actions to SHA hashes** - not tags (for security)
- **Add `persist-credentials: false`** to checkout steps
- **Explicit permissions** on all workflow jobs

### Testing

- **pytest-asyncio** - for async test support
- **pytest-httpx** - for mocking HTTP requests
- **Litestar TestClient** - for integration tests

### Code Standards

- **Async-first** - all provider methods must be async
- **Full type hints** - strict ty compatible
- **Google-style docstrings** - on all public APIs

---

## Project Overview

- **Package**: `litestar-oauth`
- **Python**: 3.10+
- **Framework**: Litestar 2.x
- **HTTP Client**: httpx

## Architecture

```
src/litestar_oauth/
├── base.py           # BaseOAuthProvider, OAuthProvider protocol
├── service.py        # OAuthService, OAuthStateManager
├── types.py          # OAuthToken, OAuthUserInfo, OAuthState
├── exceptions.py     # OAuth exception hierarchy
├── providers/        # Pre-built OAuth providers
│   ├── github.py     # GitHub OAuth
│   ├── google.py     # Google OAuth with OIDC
│   ├── discord.py    # Discord OAuth
│   └── generic.py    # Generic OAuth2/OIDC provider
├── contrib/
│   └── litestar/     # Litestar plugin integration
│       ├── config.py       # OAuthConfig
│       ├── plugin.py       # OAuthPlugin
│       └── controllers.py  # OAuth route handlers
└── testing/          # Test utilities
    ├── mocks.py      # MockOAuthProvider
    └── fixtures.py   # pytest fixtures
```

---

## Critical Rules

1. **ALWAYS use `uv run`** - Never call `python`/`python3` directly
2. **ALWAYS run `make lint`** before committing
3. **Keep code async-first** - All provider methods must be async
4. **Full type hints** - Strict ty compatible
5. **Google-style docstrings** - On all public APIs

---

## Development Commands

### Package Management (uv)

```bash
uv sync                    # Install dependencies
uv sync --all-groups       # Install with all dev dependencies
uv add <package>           # Add dependency
uv remove <package>        # Remove dependency
uv lock                    # Update lock file
```

### Development Workflow

```bash
make lint                  # Run all linters (ruff, ty, codespell, sphinx-lint)
make test                  # Run tests
make test-cov              # Run tests with coverage
```

### Documentation

```bash
make docs                  # Build documentation
make docs-serve            # Serve with live reload
```

### Building

```bash
uv build                   # Build package
```

---

## Code Standards

### Imports

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthToken
```

### Provider Implementation

```python
from litestar_oauth.base import BaseOAuthProvider
from litestar_oauth.types import OAuthToken, OAuthUserInfo

class MyProvider(BaseOAuthProvider):
    provider_name = "my_provider"
    authorize_url = "https://provider.com/oauth/authorize"
    token_url = "https://provider.com/oauth/token"
    user_info_url = "https://provider.com/api/user"
    default_scopes = ["read:user"]

    def _parse_user_info(self, data: dict) -> OAuthUserInfo:
        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=str(data["id"]),
            email=data.get("email"),
            username=data.get("username"),
        )
```

### Plugin Usage

```python
from litestar import Litestar
from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

app = Litestar(
    plugins=[
        OAuthPlugin(
            config=OAuthConfig(
                redirect_base_url="https://example.com",
                github_client_id="...",
                github_client_secret="...",
            )
        )
    ],
)
```

---

## Testing

```bash
make test                           # Run all tests
uv run pytest tests/test_types.py   # Run specific file
uv run pytest -k "test_github"      # Run by pattern
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_types.py         # Type tests
├── test_service.py       # OAuthService tests
├── test_providers.py     # Provider tests
└── test_integration.py   # E2E tests with Litestar
```

---

## Git Workflow

1. **Atomic commits** - One logical change per commit
2. **Conventional commits** - `feat:`, `fix:`, `docs:`, `chore:`
3. **PR checks must pass** - Use `gh pr checks` to verify

```bash
git add -p                          # Stage selectively
git commit -m "feat: add Apple OAuth provider"
make lint                           # Test locally first
gh pr create --fill
gh pr checks                        # Wait for CI
```

---

## Key Files

| File                             | Purpose                           |
| -------------------------------- | --------------------------------- |
| `pyproject.toml`                 | Package config, dependencies      |
| `Makefile`                       | Development commands              |
| `src/litestar_oauth/base.py`     | Base provider classes             |
| `src/litestar_oauth/service.py`  | OAuth service and state manager   |
| `src/litestar_oauth/providers/`  | Pre-built OAuth providers         |
| `tests/`                         | Test suite                        |
