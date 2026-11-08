Microsoft/Azure AD OAuth
========================

This guide covers setting up Microsoft/Azure AD as an OAuth provider for your application.
Microsoft OAuth supports both personal Microsoft accounts and organizational (Azure AD) accounts.


Creating an Azure AD Application
--------------------------------

Step 1: Navigate to Azure Portal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://portal.azure.com
2. Search for "App registrations" or navigate to Azure Active Directory > App registrations
3. Click "New registration"

Step 2: Configure Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fill in the required fields:

**Name**
    A descriptive name for your app (e.g., "My Awesome App")

**Supported account types**
    Choose based on your needs:
    - **Single tenant**: Only accounts in your organization
    - **Multi-tenant**: Accounts in any organizational directory
    - **Multi-tenant + personal**: Organization accounts and personal Microsoft accounts (recommended)

**Redirect URI**
    Platform: Web
    For development: ``http://localhost:8000/auth/microsoft/callback``
    For production: ``https://myapp.com/auth/microsoft/callback``

Step 3: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After creating the app:

1. Note your **Application (client) ID** from the Overview page
2. Note your **Directory (tenant) ID** (or use "common" for multi-tenant)
3. Go to "Certificates & secrets" > "Client secrets" > "New client secret"
4. Copy your **Client Secret** value (only shown once!)

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
                         microsoft_client_id="your-client-id",
                         microsoft_client_secret="your-client-secret",
                         microsoft_tenant_id="common",  # or specific tenant ID
                         microsoft_scope="openid email profile",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import MicrosoftOAuthProvider

         provider = MicrosoftOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
             tenant="common",  # "common", "organizations", "consumers", or tenant ID
             scope=["openid", "email", "profile"],
         )

         # Generate authorization URL
         auth_url = await provider.get_authorization_url(
             redirect_uri="https://example.com/auth/microsoft/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/microsoft/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


Tenant Configuration
--------------------

The ``tenant`` parameter controls which accounts can sign in:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Value
     - Description
   * - ``common``
     - Any Microsoft account (personal or organizational)
   * - ``organizations``
     - Only organizational (Azure AD) accounts
   * - ``consumers``
     - Only personal Microsoft accounts
   * - ``{tenant-id}``
     - Only accounts from a specific tenant


Available Scopes
----------------

Microsoft Graph API offers various scopes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``openid``
     - OpenID Connect authentication
   * - ``email``
     - Access user email address
   * - ``profile``
     - Access basic profile info
   * - ``offline_access``
     - Get refresh tokens
   * - ``User.Read``
     - Read user profile from Graph API
   * - ``User.ReadBasic.All``
     - Read basic profiles of all users
   * - ``Calendars.Read``
     - Read user calendars
   * - ``Mail.Read``
     - Read user mail

**Default scopes in litestar-oauth:** ``openid``, ``email``, ``profile``


User Info Response
------------------

Microsoft Graph API returns user data. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="microsoft",
       oauth_id="abc123-def456-...",            # Microsoft user ID
       email="user@example.com",                # mail or userPrincipalName
       email_verified=False,                    # Not provided by Microsoft
       username="user@example.com",             # userPrincipalName
       first_name="John",                       # givenName
       last_name="Doe",                         # surname
       avatar_url=None,                         # Requires separate photo call
       profile_url=None,                        # Not provided
       raw_data={...},                          # Complete Graph API response
   )

.. note::

   Microsoft doesn't provide avatar URLs directly. Profile photos require a separate
   call to ``/me/photo/$value`` which returns binary data.


Troubleshooting
---------------

**"AADSTS50011: The redirect URI specified in the request does not match"**
    The callback URL in your code doesn't match what's registered in Azure.
    Make sure they're identical, including trailing slashes and protocol (http vs https).

**"AADSTS700016: Application not found in the directory"**
    Check that you're using the correct tenant ID or "common" for multi-tenant apps.

**"AADSTS65001: The user or administrator has not consented"**
    The requested scopes require admin consent. Either request only user-consentable
    scopes or have an admin grant consent in the Azure portal.


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
