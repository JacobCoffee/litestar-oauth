"""Litestar OAuth - OAuth2 authentication library for Litestar.

This library provides a flexible, provider-agnostic OAuth2 authentication system
for Litestar applications, with built-in support for popular providers and an
extensible architecture for custom providers.
"""

from __future__ import annotations

from litestar_oauth.__metadata__ import __project__, __version__
from litestar_oauth.base import BaseOAuthProvider, OAuthProvider
from litestar_oauth.exceptions import (
    ExpiredStateError,
    InvalidStateError,
    OAuthError,
    ProviderNotConfiguredError,
    StateValidationError,
    TokenExchangeError,
    TokenRefreshError,
    UserInfoError,
)
from litestar_oauth.service import OAuthService, OAuthStateManager
from litestar_oauth.types import OAuthState, OAuthToken, OAuthUserInfo

__all__ = (
    # Base classes and protocols
    "BaseOAuthProvider",
    # Exceptions
    "ExpiredStateError",
    "InvalidStateError",
    "OAuthError",
    "OAuthProvider",
    # Core service and state management
    "OAuthService",
    # Data types
    "OAuthState",
    "OAuthStateManager",
    "OAuthToken",
    "OAuthUserInfo",
    "ProviderNotConfiguredError",
    "StateValidationError",
    "TokenExchangeError",
    "TokenRefreshError",
    "UserInfoError",
    # Metadata
    "__project__",
    "__version__",
)
