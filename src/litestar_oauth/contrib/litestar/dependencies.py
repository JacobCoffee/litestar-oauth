"""Dependency injection providers for OAuth functionality.

This module provides dependency injection functions for accessing the OAuth
service and user information within Litestar route handlers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.exceptions import NotAuthorizedException

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.datastructures.state import State
    from litestar_oauth.contrib.litestar.config import OAuthConfig
    from litestar_oauth.types import OAuthUserInfo


async def get_oauth_service(state: State) -> Any:
    """Dependency provider for the OAuth service.

    This dependency creates and caches an OAuth service instance based on
    the configuration stored in the application state.

    Args:
        state: The Litestar application state

    Returns:
        The OAuth service instance configured with all enabled providers

    Raises:
        RuntimeError: If OAuth config is not found in application state

    Example:
        ```python
        from litestar import get
        from litestar_oauth import OAuthService


        @get("/oauth-info")
        async def get_oauth_info(oauth_service: OAuthService) -> dict:
            providers = oauth_service.get_provider_names()
            return {"available_providers": providers}
        ```
    """
    from litestar_oauth.service import OAuthService

    # Check if service is already cached
    if "oauth_service" in state:
        return state["oauth_service"]

    # Get config from state
    config: OAuthConfig | None = state.get("oauth_config")
    if config is None:
        msg = "OAuth config not found in application state"
        raise RuntimeError(msg)

    # Create service instance
    service = OAuthService(state_ttl=config.state_ttl)

    # Register configured providers
    configured_providers = config.get_configured_providers()

    # Import and register providers dynamically
    for provider_name, provider_config in configured_providers.items():
        provider_class = _get_provider_class(provider_name)
        if provider_class:
            provider_instance = provider_class(**provider_config)
            service.register_provider(provider_instance)

    # Cache service in state
    state["oauth_service"] = service

    return service


async def oauth_user_info_dependency(connection: ASGIConnection[Any, Any, Any, Any]) -> OAuthUserInfo | None:
    """Dependency provider for OAuth user information.

    Retrieves the current authenticated user's OAuth information from the session.
    Returns None if no user is authenticated.

    Args:
        connection: The ASGI connection instance

    Returns:
        The OAuth user information if authenticated, None otherwise

    Example:
        ```python
        from litestar import get
        from litestar_oauth.types import OAuthUserInfo


        @get("/profile")
        async def get_profile(oauth_user_info: OAuthUserInfo | None) -> dict:
            if oauth_user_info is None:
                return {"authenticated": False}
            return {
                "authenticated": True,
                "email": oauth_user_info.email,
                "username": oauth_user_info.username,
            }
        ```
    """
    from litestar_oauth.types import OAuthUserInfo

    # Get user info from session
    user_data = connection.session.get("oauth_user")
    if user_data is None:
        return None

    # Reconstruct OAuthUserInfo from session data
    return OAuthUserInfo(
        provider=user_data.get("provider", ""),
        oauth_id=user_data.get("oauth_id", ""),
        email=user_data.get("email", ""),
        email_verified=user_data.get("email_verified", False),
        username=user_data.get("username", ""),
        first_name=user_data.get("first_name", ""),
        last_name=user_data.get("last_name", ""),
        avatar_url=user_data.get("avatar_url", ""),
        profile_url=user_data.get("profile_url", ""),
        raw_data=user_data.get("raw_data", {}),
    )


async def require_oauth_user_info(connection: ASGIConnection[Any, Any, Any, Any]) -> OAuthUserInfo:
    """Dependency provider that requires OAuth authentication.

    Similar to oauth_user_info_dependency but raises an exception if no user
    is authenticated. Use this for routes that require authentication.

    Args:
        connection: The ASGI connection instance

    Returns:
        The OAuth user information

    Raises:
        NotAuthorizedException: If no user is authenticated

    Example:
        ```python
        from litestar import get
        from litestar_oauth.types import OAuthUserInfo


        @get("/dashboard")
        async def dashboard(user: OAuthUserInfo = Dependency(require_oauth_user_info)) -> dict:
            return {"welcome": user.username}
        ```
    """
    user_info = await oauth_user_info_dependency(connection)
    if user_info is None:
        raise NotAuthorizedException("OAuth authentication required")
    return user_info


def _get_provider_class(provider_name: str) -> type | None:
    """Get the provider class for a given provider name.

    Args:
        provider_name: Name of the OAuth provider (e.g., "github", "google")

    Returns:
        The provider class if available, None otherwise
    """
    try:
        if provider_name == "github":
            from litestar_oauth.providers.github import GitHubOAuthProvider

            return GitHubOAuthProvider
        if provider_name == "google":
            from litestar_oauth.providers.google import GoogleOAuthProvider

            return GoogleOAuthProvider
        if provider_name == "discord":
            from litestar_oauth.providers.discord import DiscordOAuthProvider

            return DiscordOAuthProvider
        if provider_name == "microsoft":
            from litestar_oauth.providers.microsoft import MicrosoftOAuthProvider

            return MicrosoftOAuthProvider
        if provider_name == "apple":
            from litestar_oauth.providers.apple import AppleOAuthProvider

            return AppleOAuthProvider
        if provider_name == "gitlab":
            from litestar_oauth.providers.gitlab import GitLabOAuthProvider

            return GitLabOAuthProvider
        if provider_name == "twitter":
            from litestar_oauth.providers.twitter import TwitterOAuthProvider

            return TwitterOAuthProvider
        if provider_name == "facebook":
            from litestar_oauth.providers.facebook import FacebookOAuthProvider

            return FacebookOAuthProvider
        if provider_name == "linkedin":
            from litestar_oauth.providers.linkedin import LinkedInOAuthProvider

            return LinkedInOAuthProvider
        if provider_name == "bitbucket":
            from litestar_oauth.providers.bitbucket import BitbucketOAuthProvider

            return BitbucketOAuthProvider
    except ImportError:
        # Provider not available (missing dependencies, etc.)
        return None

    return None


__all__ = ["get_oauth_service", "oauth_user_info_dependency", "require_oauth_user_info"]
