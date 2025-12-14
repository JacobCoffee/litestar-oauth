"""Litestar plugin implementation for OAuth integration.

This module provides the main plugin class that integrates the OAuth service
with a Litestar application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.di import Provide
from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig
    from litestar_oauth.contrib.litestar.config import OAuthConfig


class OAuthPlugin(InitPluginProtocol):
    """Litestar plugin for OAuth authentication.

    This plugin integrates the OAuth service with a Litestar application,
    automatically registering routes, dependencies, and middleware.

    The plugin follows the InitPluginProtocol pattern and configures:
    - OAuth service with configured providers
    - Authentication routes (login, callback)
    - Dependencies for accessing OAuth service and user info
    - Optional middleware for state management

    Attributes:
        config: The OAuth configuration instance

    Example:
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
    """

    def __init__(self, config: OAuthConfig) -> None:
        """Initialize the OAuth plugin.

        Args:
            config: OAuth configuration instance
        """
        self.config = config
        self._oauth_service: object | None = None

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure the application with OAuth support.

        This method is called by Litestar during application initialization.
        It registers routes, dependencies, and configures the OAuth service.

        Args:
            app_config: The Litestar application configuration

        Returns:
            The modified application configuration with OAuth support
        """
        from litestar_oauth.contrib.litestar.controllers import OAuthController
        from litestar_oauth.contrib.litestar.dependencies import (
            get_oauth_service,
            oauth_user_info_dependency,
        )

        # Register the OAuth controller
        app_config.route_handlers.append(OAuthController)

        # Register dependencies
        app_config.dependencies = app_config.dependencies or {}
        app_config.dependencies.update(
            {
                "oauth_service": Provide(get_oauth_service, sync_to_thread=False),
                "oauth_user_info": Provide(oauth_user_info_dependency, sync_to_thread=False),
            }
        )

        # Store config for dependency injection
        app_config.state = app_config.state or {}
        app_config.state["oauth_config"] = self.config

        return app_config


__all__ = ["OAuthPlugin"]
