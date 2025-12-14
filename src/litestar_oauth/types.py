"""Core data types for OAuth2 authentication.

This module defines the primary data structures used throughout the OAuth2 flow,
including user information, tokens, and state management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

__all__ = (
    "OAuthState",
    "OAuthToken",
    "OAuthUserInfo",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class OAuthUserInfo:
    """User information retrieved from an OAuth provider.

    Attributes:
        provider: Name of the OAuth provider (e.g., 'google', 'github').
        oauth_id: Unique identifier from the OAuth provider.
        email: User's email address, if available.
        email_verified: Whether the email has been verified by the provider.
        username: User's username, if available.
        first_name: User's first name, if available.
        last_name: User's last name, if available.
        avatar_url: URL to the user's avatar image, if available.
        profile_url: URL to the user's profile page, if available.
        raw_data: Complete raw response data from the provider.
    """

    provider: str
    oauth_id: str
    email: str | None = None
    email_verified: bool = False
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str | None:
        """Construct full name from first and last name components.

        Returns:
            Combined full name if either component exists, None otherwise.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name


@dataclass(frozen=True, slots=True, kw_only=True)
class OAuthToken:
    """OAuth2 access token and associated metadata.

    Attributes:
        access_token: The OAuth2 access token.
        token_type: Type of token (typically 'Bearer').
        expires_in: Token lifetime in seconds, if provided.
        refresh_token: Refresh token for obtaining new access tokens, if available.
        scope: Space-separated list of granted scopes, if provided.
        id_token: OpenID Connect ID token, if provided.
        raw_response: Complete raw token response from the provider.
    """

    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None
    id_token: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)

    @property
    def expires_at(self) -> datetime | None:
        """Calculate absolute expiration timestamp.

        Returns:
            UTC timestamp when the token expires, or None if expires_in not set.
        """
        if self.expires_in is None:
            return None
        return datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)


@dataclass(frozen=True, slots=True, kw_only=True)
class OAuthState:
    """State parameter for OAuth2 authorization flow security.

    The state parameter prevents CSRF attacks by verifying that authorization
    callbacks originate from requests initiated by this application.

    Attributes:
        state: Random state string for CSRF protection.
        provider: Name of the OAuth provider.
        redirect_uri: URI where the provider should redirect after authorization.
        created_at: UTC timestamp when the state was created.
        next_url: Optional URL to redirect to after successful authentication.
        extra_data: Additional application-specific data to preserve across the flow.
    """

    state: str
    provider: str
    redirect_uri: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    next_url: str | None = None
    extra_data: dict[str, Any] = field(default_factory=dict)
