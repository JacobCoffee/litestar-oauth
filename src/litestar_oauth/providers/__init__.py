"""OAuth2 provider implementations.

This module contains OAuth2 provider implementations for various identity providers.
Each provider implements the OAuthProvider protocol and extends BaseOAuthProvider.

Available Providers:
    - BitbucketOAuthProvider: Bitbucket OAuth2 authentication
    - GitHubOAuthProvider: GitHub OAuth2 authentication
    - GoogleOAuthProvider: Google OAuth2 with OpenID Connect support
    - DiscordOAuthProvider: Discord OAuth2 authentication
    - FacebookOAuthProvider: Facebook OAuth2 authentication
    - MicrosoftOAuthProvider: Microsoft/Azure AD OAuth2 with OpenID Connect support
    - LinkedInOAuthProvider: LinkedIn OAuth2 with OpenID Connect support
    - TwitterOAuthProvider: Twitter/X OAuth2 authentication with PKCE support
    - GitLabOAuthProvider: GitLab OAuth2 (supports self-hosted instances)
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

from litestar_oauth.providers.bitbucket import BitbucketOAuthProvider
from litestar_oauth.providers.discord import DiscordOAuthProvider
from litestar_oauth.providers.facebook import FacebookOAuthProvider
from litestar_oauth.providers.generic import GenericOAuthProvider
from litestar_oauth.providers.github import GitHubOAuthProvider
from litestar_oauth.providers.gitlab import GitLabOAuthProvider
from litestar_oauth.providers.google import GoogleOAuthProvider
from litestar_oauth.providers.linkedin import LinkedInOAuthProvider
from litestar_oauth.providers.microsoft import MicrosoftOAuthProvider
from litestar_oauth.providers.twitter import TwitterOAuthProvider

__all__ = (
    "BitbucketOAuthProvider",
    "DiscordOAuthProvider",
    "FacebookOAuthProvider",
    "GenericOAuthProvider",
    "GitHubOAuthProvider",
    "GitLabOAuthProvider",
    "GoogleOAuthProvider",
    "LinkedInOAuthProvider",
    "MicrosoftOAuthProvider",
    "TwitterOAuthProvider",
)
