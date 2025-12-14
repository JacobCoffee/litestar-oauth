"""OAuth route controllers for Litestar.

This module provides the route handlers for OAuth authentication flows,
including login initiation and callback handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar import Controller, Request, get
from litestar.response import Redirect

if TYPE_CHECKING:
    from litestar.datastructures import State
    from litestar_oauth.contrib.litestar.config import OAuthConfig
    from litestar_oauth.service import OAuthService


class OAuthController(Controller):
    """Controller for OAuth authentication routes.

    This controller provides two main endpoints for each configured OAuth provider:
    - /{provider}/login: Initiates the OAuth flow by redirecting to the provider
    - /{provider}/callback: Handles the callback from the provider after authentication

    The controller is automatically registered by the OAuthPlugin.

    Attributes:
        path: The base path for OAuth routes (configured via OAuthConfig.route_prefix)
    """

    path = "/auth"

    @get("/{provider:str}/login", sync_to_thread=False)
    async def login(
        self,
        provider: str,
        oauth_service: OAuthService,
        state: State,
        request: Request[Any, Any, Any],
    ) -> Redirect:
        """Initiate OAuth login flow.

        Generates an authorization URL for the specified provider and redirects
        the user to begin the OAuth authentication process.

        Args:
            provider: The OAuth provider name (e.g., "github", "google")
            oauth_service: The OAuth service instance (injected dependency)
            state: The Litestar application state
            request: The current request instance

        Returns:
            A redirect response to the OAuth provider's authorization page

        Raises:
            HTTPException: If the provider is not configured or unavailable

        Example:
            ```
            # User visits: GET /auth/github/login
            # Response: 302 redirect to GitHub OAuth page
            ```
        """
        from litestar.exceptions import NotFoundException

        # Get OAuth config from state
        config: OAuthConfig = state.get("oauth_config")

        # Check if provider is available
        if not oauth_service.has_provider(provider):
            raise NotFoundException(f"OAuth provider '{provider}' is not configured")

        # Build redirect URI for callback
        redirect_uri = f"{config.redirect_base_url}{config.route_prefix}/{provider}/callback"

        # Get next URL from query parameters (for post-login redirect)
        next_url = request.query_params.get("next")

        # Generate state token and authorization URL
        oauth_state = await oauth_service.create_state(
            provider=provider,
            redirect_uri=redirect_uri,
            next_url=next_url,
        )

        auth_url = oauth_service.get_authorization_url(
            provider=provider,
            redirect_uri=redirect_uri,
            state=oauth_state,
        )

        return Redirect(path=auth_url)

    @get("/{provider:str}/callback", sync_to_thread=False)
    async def callback(
        self,
        provider: str,
        oauth_service: OAuthService,
        state: State,
        request: Request[Any, Any, Any],
    ) -> Redirect:
        """Handle OAuth callback from provider.

        Processes the OAuth callback, exchanges the authorization code for tokens,
        retrieves user information, and stores it in the session.

        Args:
            provider: The OAuth provider name (e.g., "github", "google")
            oauth_service: The OAuth service instance (injected dependency)
            state: The Litestar application state
            request: The current request instance

        Returns:
            A redirect response to either the success or failure URL

        Example:
            ```
            # Provider redirects to: GET /auth/github/callback?code=abc123&state=xyz
            # If successful: 302 redirect to success_redirect
            # If failed: 302 redirect to failure_redirect
            ```
        """
        from litestar.exceptions import NotFoundException

        # Get OAuth config from state
        config: OAuthConfig = state.get("oauth_config")

        # Get code and state from query parameters
        code = request.query_params.get("code")
        oauth_state = request.query_params.get("state")
        error = request.query_params.get("error")

        # Handle OAuth errors (user denied, etc.)
        if error:
            return Redirect(path=f"{config.failure_redirect}&reason={error}")

        # Validate required parameters
        if not code or not oauth_state:
            return Redirect(path=f"{config.failure_redirect}&reason=missing_params")

        try:
            # Validate state token (CSRF protection)
            state_data = await oauth_service.validate_state(oauth_state)

            # Verify provider matches
            if state_data.provider != provider:
                return Redirect(path=f"{config.failure_redirect}&reason=provider_mismatch")

            # Build redirect URI (must match the one used in login)
            redirect_uri = f"{config.redirect_base_url}{config.route_prefix}/{provider}/callback"

            # Exchange authorization code for access token
            token = await oauth_service.exchange_code(
                provider=provider,
                code=code,
                redirect_uri=redirect_uri,
            )

            # Get user information using access token
            user_info = await oauth_service.get_user_info(
                provider=provider,
                access_token=token.access_token,
            )

            # Store user info in session
            request.session["oauth_user"] = {
                "provider": user_info.provider,
                "oauth_id": user_info.oauth_id,
                "email": user_info.email,
                "email_verified": user_info.email_verified,
                "username": user_info.username,
                "first_name": user_info.first_name,
                "last_name": user_info.last_name,
                "avatar_url": user_info.avatar_url,
                "profile_url": user_info.profile_url,
                "raw_data": user_info.raw_data,
            }

            # Store tokens in session (optional, for refresh token support)
            request.session["oauth_token"] = {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "refresh_token": token.refresh_token,
                "scope": token.scope,
            }

            # Redirect to next URL or default success page
            redirect_url = state_data.next_url or config.success_redirect
            return Redirect(path=redirect_url)

        except NotFoundException:
            return Redirect(path=f"{config.failure_redirect}&reason=provider_not_found")
        except ValueError as exc:
            # State validation failed or other validation error
            return Redirect(path=f"{config.failure_redirect}&reason=invalid_state&detail={exc!s}")
        except Exception as exc:  # noqa: BLE001
            # Catch-all for any other errors (token exchange, user info retrieval, etc.)
            # In production, you'd want to log these errors
            return Redirect(path=f"{config.failure_redirect}&reason=unknown&detail={type(exc).__name__}")


__all__ = ["OAuthController"]
