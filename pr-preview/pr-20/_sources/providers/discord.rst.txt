Discord OAuth
=============

This guide covers setting up Discord OAuth2 authentication.


Creating a Discord Application
------------------------------

1. Go to the `Discord Developer Portal <https://discord.com/developers/applications>`_

2. Click **New Application** and give it a name

3. Navigate to **OAuth2** → **General**

4. Add your redirect URI:

   - For development: ``http://localhost:8000/auth/discord/callback``
   - For production: ``https://yourdomain.com/auth/discord/callback``

5. Copy your **Client ID** and **Client Secret**

.. note::

   Discord's Client Secret can only be viewed once when generated. If you lose it,
   you'll need to regenerate it.


Available Scopes
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Scope
     - Description
   * - ``identify``
     - Access to user's ID, username, avatar, and discriminator
   * - ``email``
     - Access to user's email address
   * - ``guilds``
     - List of guilds (servers) the user is a member of
   * - ``guilds.join``
     - Allows joining users to a guild
   * - ``connections``
     - List of third-party connections (Steam, Spotify, etc.)
   * - ``bot``
     - For OAuth2 bot authorization


Usage Example
-------------

.. tabs::

   .. group-tab:: Litestar Plugin

      .. code-block:: python

         from litestar import Litestar
         from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

         app = Litestar(
             plugins=[
                 OAuthPlugin(
                     config=OAuthConfig(
                         redirect_base_url="https://example.com",
                         discord_client_id="your-client-id",
                         discord_client_secret="your-client-secret",
                         discord_scope="identify email",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import DiscordOAuthProvider

         provider = DiscordOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
             scope=["identify", "email"],
         )

         # Generate authorization URL
         auth_url = provider.get_authorization_url(
             redirect_uri="https://example.com/auth/discord/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/discord/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


User Info Response
------------------

The ``OAuthUserInfo`` object returned by Discord contains:

.. code-block:: python

   OAuthUserInfo(
       provider="discord",
       oauth_id="123456789012345678",  # Discord user ID (snowflake)
       email="user@example.com",
       email_verified=True,
       username="username",  # New username format
       first_name=None,  # Discord doesn't provide name components
       last_name=None,
       avatar_url="https://cdn.discordapp.com/avatars/123.../abc123.png",
       profile_url=None,
       raw_data={...},  # Complete response from Discord
   )


Avatar URLs
-----------

Discord provides avatar hashes instead of direct URLs. The provider automatically
constructs the correct CDN URL::

   # For regular avatars
   https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png

   # For animated avatars (GIF)
   https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.gif

If the user has no custom avatar, Discord provides a default avatar based on
their discriminator.


Bot Authorization
-----------------

For Discord bots, you can combine user OAuth with bot authorization::

   auth_url = provider.get_authorization_url(
       redirect_uri="https://example.com/auth/discord/callback",
       state="random-state-token",
       scope="identify email bot",
       extra_params={
           "permissions": "8",  # Administrator permission
           "guild_id": "123456789",  # Pre-select a guild
       },
   )


Troubleshooting
---------------

**Error: invalid_client**
   The client ID or secret is incorrect. Double-check your credentials.

**Error: invalid_scope**
   One or more requested scopes are invalid. Make sure you're using
   valid Discord OAuth2 scopes.

**Error: access_denied**
   The user cancelled the authorization or your app was denied.
