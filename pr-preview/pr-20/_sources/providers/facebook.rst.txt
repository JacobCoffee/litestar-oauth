Facebook OAuth
==============

This guide covers setting up Facebook as an OAuth provider for your application.
Facebook OAuth is commonly used for social login and accessing Facebook's Graph API.


Creating a Facebook App
-----------------------

Step 1: Navigate to Developer Console
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://developers.facebook.com/
2. Click "My Apps" in the top right
3. Click "Create App"

Step 2: Choose App Type
~~~~~~~~~~~~~~~~~~~~~~~

Select the app type that matches your use case:

- **Consumer**: For apps that require standard Facebook Login
- **Business**: For apps that need Facebook business tools

Step 3: Configure Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add "Facebook Login" product to your app
2. In Facebook Login > Settings, configure:

**Valid OAuth Redirect URIs**
    For development: ``http://localhost:8000/auth/facebook/callback``
    For production: ``https://myapp.com/auth/facebook/callback``

Step 4: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to Settings > Basic
2. Note your **App ID** (client ID)
3. Note your **App Secret** (client secret)

.. warning::

   Never commit your App Secret to version control. Use environment variables
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
                         facebook_client_id="your-app-id",
                         facebook_client_secret="your-app-secret",
                         facebook_scope="email public_profile",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import FacebookOAuthProvider

         provider = FacebookOAuthProvider(
             client_id="your-app-id",
             client_secret="your-app-secret",
             scope=["email", "public_profile"],
         )

         # Generate authorization URL
         auth_url = await provider.get_authorization_url(
             redirect_uri="https://example.com/auth/facebook/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/facebook/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


Available Scopes
----------------

Facebook offers various permission scopes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``public_profile``
     - Basic profile info (name, picture, etc.)
   * - ``email``
     - User's primary email address
   * - ``user_birthday``
     - User's birthday
   * - ``user_friends``
     - List of friends using the app
   * - ``user_location``
     - User's current city
   * - ``user_photos``
     - Access user photos
   * - ``user_posts``
     - Access user posts

**Default scopes in litestar-oauth:** ``email``, ``public_profile``

.. note::

   Many Facebook scopes require App Review before they can be used with
   users outside your app's team.


User Info Response
------------------

Facebook Graph API returns user data. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="facebook",
       oauth_id="12345678901234567",            # Facebook user ID
       email="user@example.com",                # User email
       email_verified=True,                     # Facebook verifies emails
       username=None,                           # Facebook removed usernames
       first_name="John",                       # first_name field
       last_name="Doe",                         # last_name field
       avatar_url="https://graph.facebook.com/12345678901234567/picture",
       profile_url="https://www.facebook.com/12345678901234567",
       raw_data={...},                          # Complete API response
   )


App Modes
---------

Facebook apps have two modes:

**Development Mode**
    - Only users with roles in your app can log in
    - No app review required
    - Good for testing

**Live Mode**
    - Any Facebook user can log in
    - May require app review for certain permissions
    - Required for production

To switch modes, go to your app's dashboard and toggle the mode switch.


Troubleshooting
---------------

**"Error validating access token"**
    Your access token has expired or is invalid. Request a new authorization.

**"Invalid redirect_uri"**
    Make sure your redirect URI exactly matches what's configured in the Facebook
    app settings, including the protocol and any trailing slashes.

**"User hasn't authorized the application"**
    The user may have revoked access or never completed the authorization flow.

**Email not returned**
    Make sure you've requested the ``email`` scope and that the user has a
    verified email on their Facebook account.


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
