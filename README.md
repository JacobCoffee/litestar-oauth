# litestar-oauth

[![PyPI - Version](https://img.shields.io/pypi/v/litestar-oauth.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/litestar-oauth/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/litestar-oauth.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/litestar-oauth/)
[![CI](https://github.com/JacobCoffee/litestar-oauth/actions/workflows/ci.yml/badge.svg)](https://github.com/JacobCoffee/litestar-oauth/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/JacobCoffee/litestar-oauth/branch/main/graph/badge.svg)](https://codecov.io/gh/JacobCoffee/litestar-oauth)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

A modern, async OAuth2/OpenID Connect authentication library with optional Litestar integration.

## Features

- **Zero Required Dependencies**: Core OAuth2 flows work without any external dependencies
- **Async-First Design**: Built from the ground up for asyncio
- **Provider-Agnostic**: Easy to use with any OAuth2/OIDC provider
- **Type-Safe**: Comprehensive type hints throughout
- **Flexible HTTP Client Support**: Use httpx, aiohttp, or bring your own
- **Optional Framework Integration**: First-class Litestar support, with Starlette and Flask adapters
- **20+ Pre-configured Providers**: Google, GitHub, Microsoft, Discord, and more
- **Extensible**: Simple base classes for custom providers
- **Production-Ready**: Comprehensive test coverage and battle-tested in production

## Installation

### Using uv (recommended)

```bash
# Core library (no dependencies)
uv add litestar-oauth

# With httpx client
uv add "litestar-oauth[httpx]"

# With Litestar integration
uv add "litestar-oauth[litestar,httpx]"

# All features
uv add "litestar-oauth[all]"
```

### Using pip

```bash
# Core library
pip install litestar-oauth

# With httpx client
pip install "litestar-oauth[httpx]"

# With Litestar integration
pip install "litestar-oauth[litestar,httpx]"

# All features
pip install "litestar-oauth[all]"
```

## Quick Start

### Standalone Usage

```python
from litestar_oauth import OAuth2Client
from litestar_oauth.providers import GoogleProvider

# Create a client
oauth = OAuth2Client(
    provider=GoogleProvider(
        client_id="your-client-id",
        client_secret="your-client-secret",
        redirect_uri="http://localhost:8000/callback",
    )
)

# Get authorization URL
auth_url = oauth.get_authorization_url(
    scopes=["openid", "email", "profile"],
    state="random-state-value",
)

# Exchange code for token
token = await oauth.exchange_code(code="auth-code-from-callback")

# Get user info
user_info = await oauth.get_user_info(token.access_token)
```

### Litestar Integration

```python
from litestar import Litestar, get
from litestar.response import Redirect
from litestar_oauth.litestar import OAuth2Config
from litestar_oauth.providers import GitHubProvider

oauth_config = OAuth2Config(
    providers={
        "github": GitHubProvider(
            client_id="your-client-id",
            client_secret="your-client-secret",
            redirect_uri="http://localhost:8000/auth/github/callback",
        )
    }
)

@get("/login/github")
async def login(oauth: OAuth2Client) -> Redirect:
    auth_url = oauth.get_authorization_url(scopes=["user:email"])
    return Redirect(auth_url)

@get("/auth/github/callback")
async def callback(code: str, oauth: OAuth2Client) -> dict:
    token = await oauth.exchange_code(code)
    user = await oauth.get_user_info(token.access_token)
    return {"user": user}

app = Litestar(
    route_handlers=[login, callback],
    plugins=[oauth_config],
)
```

## Supported Providers

Google, GitHub, Microsoft, Discord, Twitch, LinkedIn, Facebook, Twitter/X, GitLab, Bitbucket, Slack, Spotify, Apple, Reddit, Dropbox, Auth0, Okta, Keycloak, Amazon Cognito, and more.

See the [documentation](https://jacobcoffee.github.io/litestar-oauth) for the full list and configuration examples.

## Links

- [Documentation](https://jacobcoffee.github.io/litestar-oauth)
- [PyPI](https://pypi.org/project/litestar-oauth/)
- [GitHub Repository](https://github.com/JacobCoffee/litestar-oauth)
- [Issue Tracker](https://github.com/JacobCoffee/litestar-oauth/issues)
- [Discord](https://discord.gg/litestar-919193495116337154)

## License

This project is licensed under the terms of the MIT license.
