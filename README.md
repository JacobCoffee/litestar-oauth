# litestar-oauth

[![PyPI - Version](https://img.shields.io/pypi/v/litestar-oauth.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/litestar-oauth/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/litestar-oauth.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/litestar-oauth/)
[![CI](https://github.com/JacobCoffee/litestar-oauth/actions/workflows/ci.yml/badge.svg)](https://github.com/JacobCoffee/litestar-oauth/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/JacobCoffee/litestar-oauth/branch/main/graph/badge.svg)](https://codecov.io/gh/JacobCoffee/litestar-oauth)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

OAuth2 authentication plugin for [Litestar](https://litestar.dev).

## Features

- **Async-First Design**: Built on httpx for async HTTP operations
- **Pre-built Providers**: GitHub, Google, Discord, and a generic provider for any OAuth2/OIDC service
- **Type-Safe**: Full typing with Protocol-based interfaces
- **CSRF Protection**: Built-in state management to prevent cross-site request forgery
- **Automatic Routes**: Plugin registers login and callback routes automatically
- **Normalized User Data**: Consistent user info format across all providers
- **Extensible**: Easy to add custom providers for any OAuth2-compliant identity provider

## Installation

```bash
uv add litestar-oauth
```

Or with pip:

```bash
pip install litestar-oauth
```

## Quick Start

```python
from litestar import Litestar
from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

app = Litestar(
    plugins=[
        OAuthPlugin(
            config=OAuthConfig(
                redirect_base_url="https://example.com",
                github_client_id="your-client-id",
                github_client_secret="your-client-secret",
            )
        )
    ],
)

# Routes automatically registered:
# GET /auth/github/login    - Redirects to GitHub OAuth
# GET /auth/github/callback - Handles OAuth callback
```

## Standalone Usage

Use the OAuth providers without the Litestar plugin:

```python
from litestar_oauth.providers import GitHubOAuthProvider

provider = GitHubOAuthProvider(
    client_id="your-client-id",
    client_secret="your-client-secret",
)

# Generate authorization URL
auth_url = provider.get_authorization_url(
    redirect_uri="https://example.com/callback",
    state="random-state-token",
)

# After callback, exchange code for token
token = await provider.exchange_code(
    code="authorization-code",
    redirect_uri="https://example.com/callback",
)

# Get user info
user_info = await provider.get_user_info(token.access_token)
print(f"Hello, {user_info.username}!")
```

## Supported Providers

| Provider | Class | Default Scopes |
|----------|-------|----------------|
| GitHub | `GitHubOAuthProvider` | `read:user`, `user:email` |
| Google | `GoogleOAuthProvider` | `openid`, `email`, `profile` |
| Discord | `DiscordOAuthProvider` | `identify`, `email` |
| Generic | `GenericOAuthProvider` | Configurable |

Use `GenericOAuthProvider` for any OAuth2/OIDC provider like Keycloak, Auth0, Okta, or Azure AD.

## Optional Extras

```bash
# Apple Sign In (requires JWT signing)
uv add litestar-oauth[apple]

# All provider extras
uv add litestar-oauth[all]
```

## Links

- [Documentation](https://jacobcoffee.github.io/litestar-oauth)
- [PyPI](https://pypi.org/project/litestar-oauth/)
- [GitHub Repository](https://github.com/JacobCoffee/litestar-oauth)
- [Issue Tracker](https://github.com/JacobCoffee/litestar-oauth/issues)
- [Litestar Discord](https://discord.gg/litestar-919193495116337154)

## License

MIT License - see [LICENSE](LICENSE) for details.
