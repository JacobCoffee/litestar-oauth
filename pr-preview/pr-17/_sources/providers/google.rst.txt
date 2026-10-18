Google OAuth
============

This guide covers setting up Google OAuth2 authentication with OpenID Connect support.


Creating a Google OAuth Application
-----------------------------------

1. Go to the `Google Cloud Console <https://console.cloud.google.com/>`_

2. Create a new project or select an existing one

3. Navigate to **APIs & Services** → **OAuth consent screen**

4. Configure the consent screen:

   - Choose **External** for public apps or **Internal** for Google Workspace
   - Fill in the required fields (App name, User support email, Developer contact)
   - Add scopes: ``openid``, ``email``, ``profile``

5. Navigate to **APIs & Services** → **Credentials**

6. Click **Create Credentials** → **OAuth client ID**

7. Select **Web application** as the application type

8. Add your redirect URI:

   - For development: ``http://localhost:8000/auth/google/callback``
   - For production: ``https://yourdomain.com/auth/google/callback``

9. Copy your **Client ID** and **Client Secret**


Available Scopes
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Scope
     - Description
   * - ``openid``
     - Required for OpenID Connect authentication
   * - ``email``
     - Access to user's email address
   * - ``profile``
     - Access to basic profile information (name, picture)
   * - ``https://www.googleapis.com/auth/calendar.readonly``
     - Read-only access to Google Calendar
   * - ``https://www.googleapis.com/auth/drive.readonly``
     - Read-only access to Google Drive


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
                         google_client_id="your-client-id.apps.googleusercontent.com",
                         google_client_secret="your-client-secret",
                         google_scope="openid email profile",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import GoogleOAuthProvider

         provider = GoogleOAuthProvider(
             client_id="your-client-id.apps.googleusercontent.com",
             client_secret="your-client-secret",
             scope=["openid", "email", "profile"],
         )

         # Generate authorization URL
         auth_url = provider.get_authorization_url(
             redirect_uri="https://example.com/auth/google/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/google/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


User Info Response
------------------

The ``OAuthUserInfo`` object returned by Google contains:

.. code-block:: python

   OAuthUserInfo(
       provider="google",
       oauth_id="123456789012345678901",  # Google's unique user ID
       email="user@gmail.com",
       email_verified=True,
       username=None,  # Google doesn't provide username
       first_name="John",
       last_name="Doe",
       avatar_url="https://lh3.googleusercontent.com/a/...",
       profile_url=None,
       raw_data={...},  # Complete response from Google
   )


OpenID Connect (OIDC)
---------------------

Google fully supports OpenID Connect. When using the ``openid`` scope, the token
response includes an ``id_token`` containing verified claims::

   token = await provider.exchange_code(code, redirect_uri)
   print(token.id_token)  # JWT containing user claims


Google Workspace Integration
----------------------------

For Google Workspace (formerly G Suite) users, you can restrict authentication
to your organization's domain::

   auth_url = provider.get_authorization_url(
       redirect_uri="https://example.com/auth/google/callback",
       state="random-state-token",
       extra_params={"hd": "yourdomain.com"},
   )


Troubleshooting
---------------

**Error: redirect_uri_mismatch**
   The redirect URI in your request doesn't match one of the authorized URIs
   in the Google Cloud Console. Make sure the URI matches exactly, including
   the protocol (http vs https) and trailing slashes.

**Error: access_denied**
   The user denied the authorization request, or the app is not verified.
   For testing, add yourself as a test user in the OAuth consent screen.

**Error: invalid_grant**
   The authorization code has expired or has already been used. Codes are
   single-use and expire after a few minutes.
