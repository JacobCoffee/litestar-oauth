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

    Attributes:
        redirect_base_url: Base URL for OAuth callbacks (e.g., "https://example.com")
        route_prefix: URL prefix for OAuth routes (default: "/auth")
        success_redirect: URL to redirect to after successful authentication (default: "/dashboard")
        failure_redirect: URL to redirect to after failed authentication (default: "/login?error=oauth")
        state_ttl: Time-to-live for OAuth state tokens in seconds (default: 600)
        enabled_providers: List of provider names to enable. If None, all configured providers are enabled.
        github_client_id: GitHub OAuth client ID
        github_client_secret: GitHub OAuth client secret
        github_scope: GitHub OAuth scopes (default: "user:email")
        google_client_id: Google OAuth client ID
        google_client_secret: Google OAuth client secret
        google_scope: Google OAuth scopes (default: "openid email profile")
        discord_client_id: Discord OAuth client ID
        discord_client_secret: Discord OAuth client secret
        discord_scope: Discord OAuth scopes (default: "identify email")
        microsoft_client_id: Microsoft OAuth client ID
        microsoft_client_secret: Microsoft OAuth client secret
        microsoft_tenant_id: Microsoft tenant ID (default: "common")
        microsoft_scope: Microsoft OAuth scopes (default: "openid email profile")
        apple_client_id: Apple Sign In client ID
        apple_team_id: Apple team ID
        apple_key_id: Apple key ID
        apple_private_key: Apple private key for JWT signing
        apple_scope: Apple OAuth scopes (default: "name email")
        gitlab_client_id: GitLab OAuth client ID
        gitlab_client_secret: GitLab OAuth client secret
        gitlab_url: GitLab instance URL (default: "https://gitlab.com")
        gitlab_scope: GitLab OAuth scopes (default: "read_user")
        twitter_client_id: Twitter/X OAuth client ID
        twitter_client_secret: Twitter/X OAuth client secret
        twitter_scope: Twitter OAuth scopes (default: "users.read tweet.read")
        facebook_client_id: Facebook OAuth client ID
        facebook_client_secret: Facebook OAuth client secret
        facebook_scope: Facebook OAuth scopes (default: "email public_profile")
        linkedin_client_id: LinkedIn OAuth client ID
        linkedin_client_secret: LinkedIn OAuth client secret
        linkedin_scope: LinkedIn OAuth scopes (default: "openid email profile")
        bitbucket_client_id: Bitbucket OAuth client ID
        bitbucket_client_secret: Bitbucket OAuth client secret
        bitbucket_scope: Bitbucket OAuth scopes (default: "account email")

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
    github_scope: str = "user:email"

    # Google
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_scope: str = "openid email profile"

    # Discord
    discord_client_id: str | None = None
    discord_client_secret: str | None = None
    discord_scope: str = "identify email"

    # Microsoft/Azure AD
    microsoft_client_id: str | None = None
    microsoft_client_secret: str | None = None
    microsoft_tenant_id: str = "common"
    microsoft_scope: str = "openid email profile"

    # Apple Sign In
    apple_client_id: str | None = None
    apple_team_id: str | None = None
    apple_key_id: str | None = None
    apple_private_key: str | None = None
    apple_scope: str = "name email"

    # GitLab
    gitlab_client_id: str | None = None
    gitlab_client_secret: str | None = None
    gitlab_url: str = "https://gitlab.com"
    gitlab_scope: str = "read_user"

    # Twitter/X
    twitter_client_id: str | None = None
    twitter_client_secret: str | None = None
    twitter_scope: str = "users.read tweet.read"

    # Facebook/Meta
    facebook_client_id: str | None = None
    facebook_client_secret: str | None = None
    facebook_scope: str = "email public_profile"

    # LinkedIn
    linkedin_client_id: str | None = None
    linkedin_client_secret: str | None = None
    linkedin_scope: str = "openid email profile"

    # Bitbucket
    bitbucket_client_id: str | None = None
    bitbucket_client_secret: str | None = None
    bitbucket_scope: str = "account email"

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
            # {"github": {"client_id": "id", "client_secret": "secret", "scope": "user:email"}}
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

        # Microsoft
        if self.microsoft_client_id and self.microsoft_client_secret:
            providers["microsoft"] = {
                "client_id": self.microsoft_client_id,
                "client_secret": self.microsoft_client_secret,
                "tenant_id": self.microsoft_tenant_id,
                "scope": self.microsoft_scope,
            }

        # Apple
        if all([self.apple_client_id, self.apple_team_id, self.apple_key_id, self.apple_private_key]):
            providers["apple"] = {
                "client_id": self.apple_client_id,
                "team_id": self.apple_team_id,  # type: ignore[typeddict-item]
                "key_id": self.apple_key_id,  # type: ignore[typeddict-item]
                "private_key": self.apple_private_key,  # type: ignore[typeddict-item]
                "scope": self.apple_scope,
            }

        # GitLab
        if self.gitlab_client_id and self.gitlab_client_secret:
            providers["gitlab"] = {
                "client_id": self.gitlab_client_id,
                "client_secret": self.gitlab_client_secret,
                "url": self.gitlab_url,  # type: ignore[typeddict-item]
                "scope": self.gitlab_scope,
            }

        # Twitter
        if self.twitter_client_id and self.twitter_client_secret:
            providers["twitter"] = {
                "client_id": self.twitter_client_id,
                "client_secret": self.twitter_client_secret,
                "scope": self.twitter_scope,
            }

        # Facebook
        if self.facebook_client_id and self.facebook_client_secret:
            providers["facebook"] = {
                "client_id": self.facebook_client_id,
                "client_secret": self.facebook_client_secret,
                "scope": self.facebook_scope,
            }

        # LinkedIn
        if self.linkedin_client_id and self.linkedin_client_secret:
            providers["linkedin"] = {
                "client_id": self.linkedin_client_id,
                "client_secret": self.linkedin_client_secret,
                "scope": self.linkedin_scope,
            }

        # Bitbucket
        if self.bitbucket_client_id and self.bitbucket_client_secret:
            providers["bitbucket"] = {
                "client_id": self.bitbucket_client_id,
                "client_secret": self.bitbucket_client_secret,
                "scope": self.bitbucket_scope,
            }

        # Filter by enabled_providers if specified
        if self.enabled_providers is not None:
            providers = {name: config for name, config in providers.items() if name in self.enabled_providers}

        return providers


__all__ = ["OAuthConfig"]
