"""Exception hierarchy for OAuth2 operations.

This module defines all custom exceptions that can be raised during OAuth2
authentication flows, providing clear error handling and debugging information.
"""

from __future__ import annotations

__all__ = (
    "ExpiredStateError",
    "InvalidStateError",
    "OAuthError",
    "ProviderNotConfiguredError",
    "StateValidationError",
    "TokenExchangeError",
    "TokenRefreshError",
    "UserInfoError",
)


class OAuthError(Exception):
    """Base exception for all OAuth2-related errors.

    All custom exceptions in this library inherit from this base class,
    allowing consumers to catch all OAuth errors with a single handler.
    """


class ProviderNotConfiguredError(OAuthError):
    """Raised when attempting to use an OAuth provider that hasn't been configured.

    This typically occurs when a provider is referenced but was never registered
    with the OAuthService, or when required configuration (client ID, secret) is missing.
    """


class TokenExchangeError(OAuthError):
    """Raised when the authorization code to token exchange fails.

    This error occurs during the OAuth2 callback phase when exchanging the
    authorization code for an access token. Common causes include:
    - Invalid or expired authorization code
    - Incorrect client credentials
    - Mismatched redirect URI
    - Network or provider errors
    """


class TokenRefreshError(OAuthError):
    """Raised when token refresh fails.

    This error occurs when attempting to use a refresh token to obtain a new
    access token. Common causes include:
    - Invalid or expired refresh token
    - Revoked refresh token
    - Provider policy changes
    - Network or provider errors
    """


class UserInfoError(OAuthError):
    """Raised when fetching user information from the provider fails.

    This error occurs when the provider's user info endpoint returns an error
    or unexpected response. Common causes include:
    - Invalid or expired access token
    - Insufficient scope permissions
    - Provider API changes
    - Network or provider errors
    """


class StateValidationError(OAuthError):
    """Base exception for OAuth state validation errors.

    State validation is critical for preventing CSRF attacks. This base class
    is subclassed for specific state-related errors.
    """


class InvalidStateError(StateValidationError):
    """Raised when the OAuth state parameter is invalid or doesn't match.

    This security-critical error indicates a potential CSRF attack or
    application error. Causes include:
    - State parameter missing from callback
    - State doesn't match any stored state
    - State has been tampered with
    """


class ExpiredStateError(StateValidationError):
    """Raised when the OAuth state has exceeded its time-to-live.

    State tokens have a limited lifetime to reduce attack windows. This error
    indicates the authorization flow took too long to complete.
    """
