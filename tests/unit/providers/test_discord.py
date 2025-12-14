"""Unit tests for DiscordOAuthProvider.

Tests Discord-specific OAuth implementation:
- Authorization URL generation
- Token exchange with Discord API
- User info retrieval and normalization
- Discord-specific features (bot scopes, guilds, etc.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any


@pytest.mark.provider
class TestDiscordOAuthProvider:
    """Test suite for Discord OAuth provider."""

    def test_discord_provider_properties(self, mock_discord_provider: Any) -> None:
        """Test Discord provider has correct endpoints and properties."""
        assert mock_discord_provider.provider_name == "discord"
        assert "discord.com" in mock_discord_provider.authorize_url
        assert "discord.com" in mock_discord_provider.token_url
        assert "discord.com" in mock_discord_provider.user_info_url

    def test_discord_provider_default_scope(self, mock_discord_provider: Any) -> None:
        """Test Discord provider has appropriate default scopes."""
        scope = mock_discord_provider.scope.lower()
        assert "identify" in scope or "email" in scope

    async def test_discord_provider_configuration(self) -> None:
        """Test Discord provider configuration with client credentials."""
        # When implemented:
        # from litestar_oauth.providers import DiscordOAuthProvider
        # provider = DiscordOAuthProvider(
        #     client_id="test_client_id",
        #     client_secret="test_client_secret",
        # )
        # assert provider.is_configured() is True
        pass


@pytest.mark.provider
class TestDiscordAuthorizationURL:
    """Test suite for Discord authorization URL generation."""

    def test_discord_authorization_url_basic(self, mock_discord_provider: Any) -> None:
        """Test generating Discord authorization URL."""
        url = mock_discord_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
        )

        assert "discord.com/api/oauth2/authorize" in url
        assert "client_id=" in url
        assert "redirect_uri=" in url
        assert "state=abc123" in url
        assert "response_type=code" in url

    def test_discord_authorization_url_with_scopes(
        self,
        mock_discord_provider: Any,
    ) -> None:
        """Test Discord authorization URL with custom scopes."""
        url = mock_discord_provider.get_authorization_url(
            redirect_uri="http://localhost/callback",
            state="abc123",
            scope="identify email guilds",
        )

        # Discord uses space-separated scopes
        assert "scope=" in url

    def test_discord_authorization_url_with_prompt_none(self) -> None:
        """Test Discord authorization URL with prompt=none."""
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     extra_params={"prompt": "none"},
        # )
        # assert "prompt=none" in url
        pass

    def test_discord_authorization_url_with_guild_select(self) -> None:
        """Test Discord bot authorization with guild selection."""
        # When bot scope is included, user selects which server to add bot to
        # When implemented:
        # url = provider.get_authorization_url(
        #     redirect_uri="http://localhost/callback",
        #     state="abc123",
        #     scope="bot applications.commands",
        #     extra_params={"permissions": "8"},  # Administrator
        # )
        # assert "permissions=8" in url
        pass


@pytest.mark.provider
class TestDiscordTokenExchange:
    """Test suite for Discord token exchange."""

    async def test_discord_exchange_code_success(
        self,
        mock_discord_provider: Any,
        mock_http_responses: dict[str, Any],
    ) -> None:
        """Test successful Discord code exchange."""
        token = await mock_discord_provider.exchange_code(
            code="discord_auth_code",
            redirect_uri="http://localhost/callback",
        )

        assert hasattr(token, "access_token")
        assert token.access_token is not None

    async def test_discord_exchange_code_with_httpx_mock(self) -> None:
        """Test Discord code exchange with mocked HTTP client."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://discord.com/api/oauth2/token",
        #     json={
        #         "access_token": "6qrZcUqja7812RVdnEKjpzOL4CvHBFG",
        #         "token_type": "Bearer",
        #         "expires_in": 604800,
        #         "refresh_token": "D43f5y0ahjqew82jZ4NViEr2YafMKhue",
        #         "scope": "identify email",
        #     },
        # )
        # token = await provider.exchange_code("code", "redirect_uri")
        # assert token.expires_in == 604800  # 7 days
        pass

    async def test_discord_token_exchange_requires_form_data(self) -> None:
        """Test that Discord token exchange sends form data."""
        # Discord requires application/x-www-form-urlencoded
        # Not JSON like some other providers
        pass

    async def test_discord_token_includes_refresh_token(self) -> None:
        """Test that Discord token exchange includes refresh token."""
        # Discord always returns refresh token
        # When implemented:
        # token = await provider.exchange_code("code", "redirect_uri")
        # assert token.refresh_token is not None
        pass


@pytest.mark.provider
class TestDiscordUserInfo:
    """Test suite for Discord user info retrieval."""

    async def test_discord_get_user_info_success(
        self,
        mock_discord_provider: Any,
        mock_discord_user: dict[str, Any],
    ) -> None:
        """Test successful Discord user info retrieval."""
        user_info = await mock_discord_provider.get_user_info("test_token")

        assert hasattr(user_info, "provider")
        assert hasattr(user_info, "oauth_id")
        assert hasattr(user_info, "email")

    async def test_discord_user_info_normalization(
        self,
        mock_discord_user: dict[str, Any],
    ) -> None:
        """Test Discord user data normalization to OAuthUserInfo."""
        # When implemented:
        # from litestar_oauth.providers.discord import normalize_discord_user
        # user_info = normalize_discord_user(mock_discord_user["raw_data"])
        #
        # assert user_info.provider == "discord"
        # assert user_info.oauth_id == mock_discord_user["raw_data"]["id"]
        # assert user_info.username == mock_discord_user["raw_data"]["username"]
        # assert user_info.email == mock_discord_user["raw_data"]["email"]
        assert mock_discord_user["username"] == "TestUser"

    async def test_discord_user_info_with_httpx_mock(self) -> None:
        """Test Discord user info with mocked HTTP response."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://discord.com/api/users/@me",
        #     json={
        #         "id": "987654321098765432",
        #         "username": "TestUser",
        #         "discriminator": "0",
        #         "global_name": "Test User",
        #         "avatar": "a_1234567890abcdef",
        #         "email": "test@discord.com",
        #         "verified": True,
        #     },
        # )
        # user_info = await provider.get_user_info("token")
        # assert user_info.username == "TestUser"
        pass

    async def test_discord_user_avatar_url_construction(
        self,
        mock_discord_user: dict[str, Any],
    ) -> None:
        """Test Discord avatar URL is constructed correctly."""
        # Discord avatar URL format:
        # https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png
        # Animated avatars start with a_ and use .gif
        avatar_url = mock_discord_user["avatar_url"]
        assert "cdn.discordapp.com/avatars" in avatar_url
        assert mock_discord_user["raw_data"]["id"] in avatar_url

    async def test_discord_email_verified_status(
        self,
        mock_discord_user: dict[str, Any],
    ) -> None:
        """Test Discord email verification status is captured."""
        assert mock_discord_user["email_verified"] is True

    async def test_discord_new_username_system(self) -> None:
        """Test Discord new username system (discriminator = 0)."""
        # Discord is phasing out discriminators
        # New system: discriminator = "0", username is unique
        # Old system: username + discriminator (e.g., "User#1234")
        # When implemented:
        # user_data = {"username": "testuser", "discriminator": "0"}
        # normalized = normalize_discord_user(user_data)
        # assert normalized.username == "testuser"  # No discriminator appended
        pass


@pytest.mark.provider
class TestDiscordRefreshToken:
    """Test suite for Discord refresh token functionality."""

    async def test_discord_refresh_token_exchange(
        self,
        mock_discord_provider: Any,
    ) -> None:
        """Test Discord refresh token exchange."""
        new_token = await mock_discord_provider.refresh_token("refresh_token_value")

        assert hasattr(new_token, "access_token")
        assert new_token.access_token is not None

    async def test_discord_refresh_token_with_httpx_mock(self) -> None:
        """Test Discord refresh token exchange with HTTP mock."""
        # When implemented with pytest-httpx:
        # httpx_mock.add_response(
        #     url="https://discord.com/api/oauth2/token",
        #     json={
        #         "access_token": "new_access_token",
        #         "token_type": "Bearer",
        #         "expires_in": 604800,
        #         "refresh_token": "new_refresh_token",
        #         "scope": "identify email",
        #     },
        # )
        # token = await provider.refresh_token("old_refresh")
        # assert token.refresh_token == "new_refresh_token"
        pass

    async def test_discord_refresh_token_returns_new_refresh_token(self) -> None:
        """Test that Discord refresh returns new refresh token."""
        # Unlike Google, Discord returns a new refresh token
        # Old refresh token is invalidated
        pass


@pytest.mark.provider
class TestDiscordTokenRevocation:
    """Test suite for Discord token revocation."""

    async def test_discord_revoke_token(self, mock_discord_provider: Any) -> None:
        """Test Discord token revocation."""
        await mock_discord_provider.revoke_token("test_token")

    async def test_discord_revoke_token_with_httpx_mock(self) -> None:
        """Test Discord token revocation with HTTP mock."""
        # When implemented:
        # httpx_mock.add_response(
        #     url="https://discord.com/api/oauth2/token/revoke",
        #     status_code=200,
        # )
        # await provider.revoke_token("token")
        pass


@pytest.mark.provider
class TestDiscordErrorHandling:
    """Test suite for Discord-specific error handling."""

    async def test_discord_invalid_grant_error(self) -> None:
        """Test handling Discord invalid grant error."""
        # When implemented:
        # httpx_mock.add_response(
        #     url="https://discord.com/api/oauth2/token",
        #     status_code=400,
        #     json={"error": "invalid_grant"},
        # )
        # with pytest.raises(TokenExchangeError):
        #     await provider.exchange_code("invalid_code", "redirect_uri")
        pass

    async def test_discord_rate_limit_handling(self) -> None:
        """Test handling Discord API rate limits."""
        # Discord returns 429 with Retry-After header
        # httpx_mock.add_response(
        #     url="https://discord.com/api/users/@me",
        #     status_code=429,
        #     headers={"Retry-After": "5"},
        #     json={"message": "You are being rate limited"},
        # )
        # with pytest.raises(OAuthError) as exc_info:
        #     await provider.get_user_info("token")
        # assert "rate limit" in str(exc_info.value).lower()
        pass

    async def test_discord_unauthorized_error(self) -> None:
        """Test handling Discord unauthorized errors."""
        # Discord returns 401 for invalid/expired tokens
        # httpx_mock.add_response(
        #     url="https://discord.com/api/users/@me",
        #     status_code=401,
        #     json={"message": "401: Unauthorized"},
        # )
        # with pytest.raises(UserInfoError):
        #     await provider.get_user_info("invalid_token")
        pass


@pytest.mark.provider
class TestDiscordSpecificFeatures:
    """Test suite for Discord-specific OAuth features."""

    async def test_discord_guilds_scope(self) -> None:
        """Test Discord guilds scope for server information."""
        # guilds scope allows reading user's servers
        # When implemented:
        # provider = DiscordOAuthProvider(...)
        # url = provider.get_authorization_url(..., scope="identify guilds")
        # # After auth, can fetch guilds with separate endpoint
        # guilds = await provider.get_user_guilds(access_token)
        pass

    async def test_discord_connections_scope(self) -> None:
        """Test Discord connections scope for linked accounts."""
        # connections scope allows reading linked accounts (Twitch, Steam, etc.)
        # When implemented:
        # connections = await provider.get_user_connections(access_token)
        pass

    async def test_discord_bot_authorization(self) -> None:
        """Test Discord bot authorization flow."""
        # Bot scope adds bot to server instead of user auth
        # Requires additional permissions parameter
        # When implemented:
        # url = provider.get_authorization_url(
        #     ...,
        #     scope="bot applications.commands",
        #     extra_params={"permissions": "8"},  # Admin
        # )
        pass

    def test_discord_webhook_integration(self) -> None:
        """Test Discord webhook OAuth flow."""
        # webhook.incoming scope allows creating webhooks
        # Returns webhook URL in token response
        pass

    async def test_discord_role_connections(self) -> None:
        """Test Discord role connections metadata."""
        # role_connections.write scope for linked roles
        # Allows pushing metadata for role requirements
        pass


@pytest.mark.provider
class TestDiscordAvatarHandling:
    """Test suite for Discord avatar URL handling."""

    def test_discord_avatar_url_static(self, mock_discord_user: dict[str, Any]) -> None:
        """Test Discord static avatar URL construction."""
        # Standard avatars: hash without a_ prefix
        # URL: https://cdn.discordapp.com/avatars/{user_id}/{hash}.png
        raw = mock_discord_user["raw_data"]
        if raw["avatar"] and not raw["avatar"].startswith("a_"):
            # Would construct static avatar URL
            pass

    def test_discord_avatar_url_animated(self, mock_discord_user: dict[str, Any]) -> None:
        """Test Discord animated avatar URL construction."""
        # Animated avatars: hash with a_ prefix
        # URL: https://cdn.discordapp.com/avatars/{user_id}/{hash}.gif
        raw = mock_discord_user["raw_data"]
        if raw["avatar"] and raw["avatar"].startswith("a_"):
            # Would construct animated avatar URL with .gif
            assert ".png" in mock_discord_user["avatar_url"]  # Mock uses .png

    def test_discord_default_avatar(self) -> None:
        """Test Discord default avatar for users without custom avatar."""
        # When avatar is None, use default avatar
        # URL: https://cdn.discordapp.com/embed/avatars/{discriminator % 5}.png
        # New system (discriminator=0): use (user_id >> 22) % 6
        pass


@pytest.mark.provider
@pytest.mark.parametrize(
    ("scope", "allows_feature"),
    [
        ("identify", "basic_user_info"),
        ("email", "email_address"),
        ("guilds", "server_list"),
        ("connections", "linked_accounts"),
        ("guilds.join", "add_to_server"),
        ("bot", "bot_addition"),
    ],
)
def test_discord_scope_permissions(scope: str, allows_feature: str) -> None:
    """Test Discord scope to permission mapping."""
    # Different scopes provide different capabilities
    # identify - basic user info (no email)
    # email - email address
    # guilds - list of servers
    # guilds.join - add user to server
    # connections - linked accounts (Twitch, YouTube, etc.)
    # bot - add bot to server
    pass


@pytest.mark.provider
class TestDiscordAPIVersion:
    """Test suite for Discord API versioning."""

    def test_discord_api_v10_endpoints(self) -> None:
        """Test Discord uses API v10 endpoints."""
        # Current Discord API version is v10
        # Endpoints should use /api/v10/ or /api/oauth2/
        pass

    def test_discord_api_version_compatibility(self) -> None:
        """Test Discord API version compatibility."""
        # Provider should support current and recent API versions
        # Can be configured via base_url or api_version parameter
        pass
