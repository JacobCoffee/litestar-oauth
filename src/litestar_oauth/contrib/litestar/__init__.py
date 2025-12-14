"""Litestar integration for litestar-oauth.

This module provides a complete Litestar plugin for OAuth authentication,
including configuration, route controllers, guards, and dependencies.

The plugin follows the InitPluginProtocol pattern and automatically configures:
- OAuth service with configured providers
- Authentication routes (/{provider}/login, /{provider}/callback)
- Dependencies for accessing OAuth service and user info
- Guards for protecting routes with OAuth authentication

Example:
    Basic usage with GitHub OAuth:

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
    ```

Example:
    Using guards to protect routes:

    ```python
    from litestar import get
    from litestar_oauth.contrib.litestar import require_oauth_session
    from litestar_oauth.types import OAuthUserInfo


    @get("/dashboard", guards=[require_oauth_session])
    async def dashboard(oauth_user_info: OAuthUserInfo) -> dict:
        return {
            "message": f"Welcome {oauth_user_info.username}",
            "email": oauth_user_info.email,
        }
    ```

Example:
    Multiple providers configuration:

    ```python
    from litestar import Litestar
    from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

    app = Litestar(
        plugins=[
            OAuthPlugin(
                config=OAuthConfig(
                    redirect_base_url="https://example.com",
                    route_prefix="/auth",
                    success_redirect="/dashboard",
                    failure_redirect="/login?error=oauth",
                    # GitHub
                    github_client_id="github-client-id",
                    github_client_secret="github-client-secret",
                    # Google
                    google_client_id="google-client-id",
                    google_client_secret="google-client-secret",
                    # Discord
                    discord_client_id="discord-client-id",
                    discord_client_secret="discord-client-secret",
                    # Only enable specific providers
                    enabled_providers=["github", "google"],
                )
            )
        ],
    )
    ```
"""

from litestar_oauth.contrib.litestar.config import OAuthConfig
from litestar_oauth.contrib.litestar.controllers import OAuthController
from litestar_oauth.contrib.litestar.dependencies import (
    get_oauth_service,
    oauth_user_info_dependency,
    require_oauth_user_info,
)
from litestar_oauth.contrib.litestar.guards import (
    RequireOAuthProvider,
    RequireOAuthSession,
    RequireVerifiedEmail,
    require_oauth_provider,
    require_oauth_session,
    require_verified_email,
)
from litestar_oauth.contrib.litestar.plugin import OAuthPlugin

__all__ = [
    "OAuthConfig",
    "OAuthController",
    "OAuthPlugin",
    "RequireOAuthProvider",
    "RequireOAuthSession",
    "RequireVerifiedEmail",
    "get_oauth_service",
    "oauth_user_info_dependency",
    "require_oauth_provider",
    "require_oauth_session",
    "require_oauth_user_info",
    "require_verified_email",
]
