Twitter/X OAuth
===============

This guide covers setting up Twitter/X as an OAuth provider for your application.
Twitter requires OAuth2 with PKCE (Proof Key for Code Exchange) for enhanced security.


Creating a Twitter Developer Application
----------------------------------------

Step 1: Set Up Developer Account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://developer.twitter.com/
2. Sign up for a developer account if you don't have one
3. Navigate to the Developer Portal

Step 2: Create a Project and App
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a new Project (if you don't have one)
2. Within the Project, create a new App
3. Choose the appropriate use case for your app

Step 3: Configure OAuth 2.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to your App settings
2. Under "User authentication settings", click "Set up"
3. Configure:

**App permissions**
    Choose based on your needs (Read, Read and Write, etc.)

**Type of App**
    Select "Web App" or "Native App"

**Callback URI / Redirect URL**
    For development: ``http://localhost:8000/auth/twitter/callback``
    For production: ``https://myapp.com/auth/twitter/callback``

**Website URL**
    Your application's homepage URL

Step 4: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Note your **Client ID**
2. Copy your **Client Secret**

.. warning::

   Never commit your Client Secret to version control. Use environment variables
   or a secrets manager.


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
                         twitter_client_id="your-client-id",
                         twitter_client_secret="your-client-secret",
                         twitter_scope="users.read tweet.read",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import TwitterOAuthProvider

         provider = TwitterOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
             scope=["users.read", "tweet.read"],
         )

         # Generate authorization URL (includes PKCE challenge)
         auth_url = await provider.get_authorization_url(
             redirect_uri="https://example.com/auth/twitter/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token (includes PKCE verifier)
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/twitter/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


PKCE Support
------------

Twitter OAuth2 requires PKCE for security. The ``TwitterOAuthProvider`` handles this
automatically:

1. When generating the authorization URL, a ``code_verifier`` and ``code_challenge``
   are created
2. The ``code_challenge`` is included in the authorization URL
3. The ``code_verifier`` is stored and used during token exchange

If you're managing PKCE externally, you can pass your own ``code_verifier``:

.. code-block:: python

   token = await provider.exchange_code(
       code="authorization-code",
       redirect_uri="https://example.com/callback",
       code_verifier="your-external-code-verifier",
   )


Available Scopes
----------------

Twitter offers various OAuth2 scopes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``tweet.read``
     - Read tweets (user's and their timeline)
   * - ``tweet.write``
     - Post, delete, and like tweets
   * - ``users.read``
     - Read user profile information
   * - ``follows.read``
     - Read follow relationships
   * - ``follows.write``
     - Follow and unfollow users
   * - ``offline.access``
     - Get refresh tokens for long-lived access
   * - ``dm.read``
     - Read direct messages
   * - ``dm.write``
     - Send direct messages
   * - ``like.read``
     - Read liked tweets
   * - ``like.write``
     - Like and unlike tweets

**Default scopes in litestar-oauth:** ``users.read``, ``tweet.read``

.. note::

   Twitter does **not** provide email addresses through OAuth2. If you need
   email verification, consider using a different provider for authentication.


User Info Response
------------------

Twitter API returns user data. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="twitter",
       oauth_id="12345678901234567890",         # Twitter user ID
       email=None,                              # Not available from Twitter
       email_verified=False,                    # N/A
       username="johndoe",                      # Twitter handle
       first_name="John",                       # Parsed from name field
       last_name="Doe",                         # Parsed from name field
       avatar_url="https://pbs.twimg.com/profile_images/...",
       profile_url="https://twitter.com/johndoe",
       raw_data={...},                          # Complete API response
   )


Token Revocation
----------------

You can revoke Twitter access tokens:

.. code-block:: python

   success = await provider.revoke_token(token.access_token)


Troubleshooting
---------------

**"invalid_request: Value passed for the authorization code was invalid"**
    The authorization code has expired or was already used. Codes are single-use
    and expire quickly.

**"code_verifier is required for Twitter OAuth2 PKCE flow"**
    You're trying to exchange a code without a code_verifier. Ensure you're using
    the same provider instance that generated the authorization URL, or pass
    ``code_verifier`` explicitly.

**"401 Unauthorized" when fetching user info**
    Check that your access token is valid and hasn't expired. Twitter access tokens
    have a limited lifetime.


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
