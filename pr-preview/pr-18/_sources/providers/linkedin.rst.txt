LinkedIn OAuth
==============

This guide covers setting up LinkedIn as an OAuth provider for your application.
LinkedIn OAuth uses OpenID Connect for authentication.


Creating a LinkedIn Application
-------------------------------

Step 1: Navigate to Developer Portal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://www.linkedin.com/developers/
2. Click "Create App"

Step 2: Configure Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fill in the required fields:

**App name**
    A descriptive name for your app

**LinkedIn Page**
    You must associate your app with a LinkedIn Company Page

**App logo**
    Upload a logo for your app

**Legal agreement**
    Accept the terms

Step 3: Configure OAuth 2.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the "Auth" tab in your app settings
2. Add your redirect URLs:

**Authorized redirect URLs for your app**
    For development: ``http://localhost:8000/auth/linkedin/callback``
    For production: ``https://myapp.com/auth/linkedin/callback``

Step 4: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Note your **Client ID**
2. Copy your **Client Secret**

.. warning::

   Never commit your Client Secret to version control. Use environment variables
   or a secrets manager.

Step 5: Request Products
~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the "Products" tab
2. Request "Sign In with LinkedIn using OpenID Connect"
3. Wait for approval (usually automatic)


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
                         linkedin_client_id="your-client-id",
                         linkedin_client_secret="your-client-secret",
                         linkedin_scope="openid email profile",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import LinkedInOAuthProvider

         provider = LinkedInOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
             scope=["openid", "email", "profile"],
         )

         # Generate authorization URL
         auth_url = await provider.get_authorization_url(
             redirect_uri="https://example.com/auth/linkedin/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/linkedin/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


Available Scopes
----------------

LinkedIn uses OpenID Connect scopes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``openid``
     - Required for OpenID Connect
   * - ``email``
     - User's email address
   * - ``profile``
     - Basic profile info (name, picture)

**Default scopes in litestar-oauth:** ``openid``, ``email``, ``profile``

.. note::

   LinkedIn has deprecated their legacy API scopes. New applications should
   use OpenID Connect scopes (``openid``, ``email``, ``profile``).


User Info Response
------------------

LinkedIn returns user data through their userinfo endpoint. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="linkedin",
       oauth_id="abc123XYZ",                    # LinkedIn member sub
       email="user@example.com",                # User email
       email_verified=True,                     # email_verified claim
       username=None,                           # LinkedIn doesn't provide usernames
       first_name="John",                       # given_name claim
       last_name="Doe",                         # family_name claim
       avatar_url="https://media.licdn-ei.com/...",
       profile_url=None,                        # Not provided via OIDC
       raw_data={...},                          # Complete API response
   )


Troubleshooting
---------------

**"unauthorized_scope_error"**
    You may be requesting scopes that your app hasn't been approved for.
    Make sure you've added the "Sign In with LinkedIn using OpenID Connect"
    product to your app.

**"Invalid redirect URI"**
    The redirect URI must exactly match one of the authorized redirect URLs
    in your LinkedIn app settings.

**"Unable to retrieve access token"**
    Check that your client secret is correct and hasn't been rotated.

**Profile picture not returned**
    The ``picture`` claim requires the ``profile`` scope and may not be
    available for all users.


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
