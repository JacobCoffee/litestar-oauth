"""Guards for OAuth authentication in Litestar.

This module provides route guards that enforce OAuth authentication requirements
on specific routes or controllers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.exceptions import NotAuthorizedException

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.handlers.base import BaseRouteHandler


async def require_oauth_session(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
    """Guard that requires an active OAuth session.

    This guard checks if the user has an active OAuth session by verifying
    that OAuth user data exists in the session. If no session is found,
    it raises a NotAuthorizedException.

    Args:
        connection: The ASGI connection instance
        _: The route handler (unused but required by guard signature)

    Raises:
        NotAuthorizedException: If no OAuth session exists

    Example:
        ```python
        from litestar import get
        from litestar_oauth.contrib.litestar.guards import require_oauth_session


        @get("/dashboard", guards=[require_oauth_session])
        async def dashboard() -> dict:
            return {"message": "Welcome to your dashboard"}
        ```

    Example with controller:
        ```python
        from litestar import Controller, get
        from litestar_oauth.contrib.litestar.guards import require_oauth_session


        class DashboardController(Controller):
            path = "/dashboard"
            guards = [require_oauth_session]

            @get("/")
            async def index(self) -> dict:
                return {"message": "Dashboard index"}

            @get("/profile")
            async def profile(self) -> dict:
                return {"message": "User profile"}
        ```
    """
    oauth_user = connection.session.get("oauth_user")
    if oauth_user is None:
        raise NotAuthorizedException("OAuth authentication required. Please log in.")


async def require_oauth_provider(
    connection: ASGIConnection[Any, Any, Any, Any],
    _: BaseRouteHandler,
    *,
    provider: str,
) -> None:
    """Guard that requires authentication from a specific OAuth provider.

    This guard checks if the user is authenticated AND authenticated through
    a specific OAuth provider (e.g., only allow GitHub users).

    Args:
        connection: The ASGI connection instance
        _: The route handler (unused but required by guard signature)
        provider: The required OAuth provider name

    Raises:
        NotAuthorizedException: If no OAuth session exists or wrong provider

    Example:
        ```python
        from functools import partial
        from litestar import get
        from litestar_oauth.contrib.litestar.guards import require_oauth_provider

        # Only allow GitHub authenticated users
        require_github = partial(require_oauth_provider, provider="github")


        @get("/github-only", guards=[require_github])
        async def github_only_route() -> dict:
            return {"message": "GitHub users only"}
        ```
    """
    oauth_user = connection.session.get("oauth_user")
    if oauth_user is None:
        raise NotAuthorizedException("OAuth authentication required. Please log in.")

    user_provider = oauth_user.get("provider")
    if user_provider != provider:
        raise NotAuthorizedException(
            f"Authentication from {provider} required. You are authenticated with {user_provider}."
        )


async def require_verified_email(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
    """Guard that requires the OAuth user to have a verified email address.

    This guard checks if the user has an active OAuth session AND has a verified
    email address from the OAuth provider.

    Args:
        connection: The ASGI connection instance
        _: The route handler (unused but required by guard signature)

    Raises:
        NotAuthorizedException: If no OAuth session exists or email not verified

    Example:
        ```python
        from litestar import get
        from litestar_oauth.contrib.litestar.guards import require_verified_email


        @get("/sensitive-data", guards=[require_verified_email])
        async def sensitive_data() -> dict:
            return {"message": "Only users with verified emails can see this"}
        ```
    """
    oauth_user = connection.session.get("oauth_user")
    if oauth_user is None:
        raise NotAuthorizedException("OAuth authentication required. Please log in.")

    email_verified = oauth_user.get("email_verified", False)
    if not email_verified:
        raise NotAuthorizedException("Verified email address required. Please verify your email.")


class RequireOAuthSession:
    """Class-based guard that requires an active OAuth session.

    This is an alternative to the function-based guard, providing the same
    functionality in a class format for use cases where that's preferred.

    Example:
        ```python
        from litestar import get
        from litestar_oauth.contrib.litestar.guards import RequireOAuthSession


        @get("/dashboard", guards=[RequireOAuthSession()])
        async def dashboard() -> dict:
            return {"message": "Welcome to your dashboard"}
        ```
    """

    def __call__(self, connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if user has an active OAuth session.

        Args:
            connection: The ASGI connection instance
            _: The route handler (unused but required by guard signature)

        Raises:
            NotAuthorizedException: If no OAuth session exists
        """
        oauth_user = connection.session.get("oauth_user")
        if oauth_user is None:
            raise NotAuthorizedException("OAuth authentication required. Please log in.")


class RequireOAuthProvider:
    """Class-based guard that requires authentication from a specific provider.

    Example:
        ```python
        from litestar import get
        from litestar_oauth.contrib.litestar.guards import RequireOAuthProvider


        @get("/github-only", guards=[RequireOAuthProvider(provider="github")])
        async def github_only_route() -> dict:
            return {"message": "GitHub users only"}
        ```
    """

    def __init__(self, provider: str) -> None:
        """Initialize the guard with a specific provider requirement.

        Args:
            provider: The required OAuth provider name
        """
        self.provider = provider

    def __call__(self, connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if user is authenticated with the required provider.

        Args:
            connection: The ASGI connection instance
            _: The route handler (unused but required by guard signature)

        Raises:
            NotAuthorizedException: If no OAuth session exists or wrong provider
        """
        oauth_user = connection.session.get("oauth_user")
        if oauth_user is None:
            raise NotAuthorizedException("OAuth authentication required. Please log in.")

        user_provider = oauth_user.get("provider")
        if user_provider != self.provider:
            raise NotAuthorizedException(
                f"Authentication from {self.provider} required. You are authenticated with {user_provider}."
            )


class RequireVerifiedEmail:
    """Class-based guard that requires a verified email address.

    Example:
        ```python
        from litestar import get
        from litestar_oauth.contrib.litestar.guards import RequireVerifiedEmail


        @get("/sensitive-data", guards=[RequireVerifiedEmail()])
        async def sensitive_data() -> dict:
            return {"message": "Only users with verified emails can see this"}
        ```
    """

    def __call__(self, connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if user has a verified email address.

        Args:
            connection: The ASGI connection instance
            _: The route handler (unused but required by guard signature)

        Raises:
            NotAuthorizedException: If no OAuth session exists or email not verified
        """
        oauth_user = connection.session.get("oauth_user")
        if oauth_user is None:
            raise NotAuthorizedException("OAuth authentication required. Please log in.")

        email_verified = oauth_user.get("email_verified", False)
        if not email_verified:
            raise NotAuthorizedException("Verified email address required. Please verify your email.")


__all__ = [
    "RequireOAuthProvider",
    "RequireOAuthSession",
    "RequireVerifiedEmail",
    "require_oauth_provider",
    "require_oauth_session",
    "require_verified_email",
]
