"""OAuth2 provider implementations.

This module contains OAuth2 provider implementations for various identity providers.
Each provider implements the OAuthProvider protocol and extends BaseOAuthProvider.

Available Providers:
    - GitHubOAuthProvider: GitHub OAuth2 authentication
    - GoogleOAuthProvider: Google OAuth2 with OpenID Connect support
    - DiscordOAuthProvider: Discord OAuth2 authentication
    - GenericOAuthProvider: Configurable provider for any OAuth2/OIDC-compliant IdP

Example:
    ```python
    from litestar_oauth.providers import GitHubOAuthProvider, GoogleOAuthProvider

    github = GitHubOAuthProvider(
        client_id="your-client-id",
        client_secret="your-client-secret",
    )

    google = GoogleOAuthProvider(
        client_id="your-client-id.apps.googleusercontent.com",
        client_secret="your-client-secret",
    )

    # Generate authorization URL
    auth_url = await github.get_authorization_url(
        redirect_uri="https://example.com/callback",
        state="random-state-token",
    )

    # Exchange code for token
    token = await github.exchange_code(
        code="authorization-code",
        redirect_uri="https://example.com/callback",
    )

    # Get user info
    user_info = await github.get_user_info(token.access_token)
    ```
"""

from __future__ import annotations

from litestar_oauth.providers.discord import DiscordOAuthProvider
from litestar_oauth.providers.generic import GenericOAuthProvider
from litestar_oauth.providers.github import GitHubOAuthProvider
from litestar_oauth.providers.google import GoogleOAuthProvider

__all__ = (
    "DiscordOAuthProvider",
    "GenericOAuthProvider",
    "GitHubOAuthProvider",
    "GoogleOAuthProvider",
)
