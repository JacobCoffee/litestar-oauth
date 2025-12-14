"""Configuration for the Litestar OAuth plugin.

This module provides the configuration dataclass for the Litestar OAuth plugin,
allowing users to configure OAuth providers and plugin behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class OAuthConfig:
    """Configuration for the Litestar OAuth plugin.

    This configuration class allows you to set up OAuth providers and customize
    the behavior of the OAuth authentication flow.

    For providers not listed here (Microsoft, Apple, Twitter, etc.), use the
    ``GenericOAuthProvider`` with manual endpoint configuration.

    Attributes:
        redirect_base_url: Base URL for OAuth callbacks (e.g., "https://example.com")
        route_prefix: URL prefix for OAuth routes (default: "/auth")
        success_redirect: URL to redirect to after successful authentication (default: "/dashboard")
        failure_redirect: URL to redirect to after failed authentication (default: "/login?error=oauth")
        state_ttl: Time-to-live for OAuth state tokens in seconds (default: 600)
        enabled_providers: List of provider names to enable. If None, all configured providers are enabled.
        github_client_id: GitHub OAuth client ID
        github_client_secret: GitHub OAuth client secret
        github_scope: GitHub OAuth scopes (default: "read:user user:email")
        google_client_id: Google OAuth client ID
        google_client_secret: Google OAuth client secret
        google_scope: Google OAuth scopes (default: "openid email profile")
        discord_client_id: Discord OAuth client ID
        discord_client_secret: Discord OAuth client secret
        discord_scope: Discord OAuth scopes (default: "identify email")

    Example::

        from litestar import Litestar
        from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

        app = Litestar(
            plugins=[
                OAuthPlugin(
                    config=OAuthConfig(
                        redirect_base_url="https://example.com",
                        github_client_id="your-client-id",
                        github_client_secret="your-client-secret",
                        google_client_id="your-client-id",
                        google_client_secret="your-client-secret",
                        enabled_providers=["github", "google"],
                    )
                )
            ],
        )
    """

    # Core configuration
    redirect_base_url: str
    route_prefix: str = "/auth"
    success_redirect: str = "/dashboard"
    failure_redirect: str = "/login?error=oauth"
    state_ttl: int = 600
    enabled_providers: Sequence[str] | None = None

    # GitHub
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_scope: str = "read:user user:email"

    # Google
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_scope: str = "openid email profile"

    # Discord
    discord_client_id: str | None = None
    discord_client_secret: str | None = None
    discord_scope: str = "identify email"

    def get_configured_providers(self) -> dict[str, dict[str, str]]:
        """Get a dictionary of configured providers with their credentials.

        Returns:
            A dictionary mapping provider names to their configuration dictionaries.
            Each configuration includes client_id, client_secret, and scope.

        Example::

            config = OAuthConfig(
                redirect_base_url="https://example.com",
                github_client_id="id",
                github_client_secret="secret",
            )
            providers = config.get_configured_providers()
            # {"github": {"client_id": "id", "client_secret": "secret", "scope": "read:user user:email"}}
        """
        providers: dict[str, dict[str, str]] = {}

        # GitHub
        if self.github_client_id and self.github_client_secret:
            providers["github"] = {
                "client_id": self.github_client_id,
                "client_secret": self.github_client_secret,
                "scope": self.github_scope,
            }

        # Google
        if self.google_client_id and self.google_client_secret:
            providers["google"] = {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "scope": self.google_scope,
            }

        # Discord
        if self.discord_client_id and self.discord_client_secret:
            providers["discord"] = {
                "client_id": self.discord_client_id,
                "client_secret": self.discord_client_secret,
                "scope": self.discord_scope,
            }

        # Filter by enabled_providers if specified
        if self.enabled_providers is not None:
            providers = {name: config for name, config in providers.items() if name in self.enabled_providers}

        return providers


__all__ = ["OAuthConfig"]
