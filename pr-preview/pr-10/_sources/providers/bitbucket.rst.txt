Bitbucket OAuth
===============

This guide covers setting up Bitbucket as an OAuth provider for your application.
Bitbucket OAuth is commonly used for developer tools and CI/CD integrations.


Creating a Bitbucket OAuth Consumer
-----------------------------------

Step 1: Navigate to Workspace Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://bitbucket.org/
2. Click on your workspace name in the sidebar
3. Go to Settings > OAuth consumers
4. Click "Add consumer"

Step 2: Configure Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fill in the required fields:

**Name**
    A descriptive name for your app (e.g., "My Awesome App")

**Callback URL**
    Where Bitbucket redirects after authorization.
    For development: ``http://localhost:8000/auth/bitbucket/callback``
    For production: ``https://myapp.com/auth/bitbucket/callback``

**URL**
    Your application's homepage URL

**Description** (optional)
    A brief description of your application

**Permissions**
    Select the permissions your application needs:
    - Account: Read (recommended minimum)
    - Email: Read (if you need email access)

Step 3: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After creating the consumer:

1. Note your **Key** (client ID)
2. Note your **Secret** (client secret)

.. warning::

   Never commit your Secret to version control. Use environment variables
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
                         bitbucket_client_id="your-consumer-key",
                         bitbucket_client_secret="your-consumer-secret",
                         bitbucket_scope="account email",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import BitbucketOAuthProvider

         provider = BitbucketOAuthProvider(
             client_id="your-consumer-key",
             client_secret="your-consumer-secret",
             scope=["account", "email"],
         )

         # Generate authorization URL
         auth_url = await provider.get_authorization_url(
             redirect_uri="https://example.com/auth/bitbucket/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/bitbucket/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


Available Scopes
----------------

Bitbucket offers various permission scopes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``account``
     - Read account information
   * - ``email``
     - Read email addresses
   * - ``repository``
     - Read repositories
   * - ``repository:write``
     - Write to repositories
   * - ``repository:admin``
     - Admin access to repositories
   * - ``pullrequest``
     - Read pull requests
   * - ``pullrequest:write``
     - Write to pull requests
   * - ``issue``
     - Read issues
   * - ``issue:write``
     - Write to issues
   * - ``wiki``
     - Read wiki
   * - ``webhook``
     - Manage webhooks

**Default scopes in litestar-oauth:** ``account``, ``email``


User Info Response
------------------

Bitbucket API returns user data. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="bitbucket",
       oauth_id="abc123-def456-...",            # Bitbucket UUID (without braces)
       email="user@example.com",                # Primary email
       email_verified=True,                     # is_confirmed field
       username="johndoe",                      # Bitbucket username
       first_name="John",                       # Parsed from display_name
       last_name="Doe",                         # Parsed from display_name
       avatar_url="https://bitbucket.org/account/johndoe/avatar/",
       profile_url="https://bitbucket.org/johndoe/",
       raw_data={...},                          # Complete API response
   )


Email Handling
--------------

Bitbucket stores emails separately from the user profile. The ``BitbucketOAuthProvider``
automatically makes an additional API call to ``/user/emails`` to fetch the user's
email addresses.

The provider selects emails in this priority:

1. Primary email (if ``is_primary`` is True)
2. First confirmed email
3. First email in the list


Troubleshooting
---------------

**"Invalid redirect URI"**
    The callback URL must exactly match what's configured in the Bitbucket
    consumer settings. Check for trailing slashes and protocol (http vs https).

**"401 Unauthorized" when fetching user info**
    Check that you've selected the "Account: Read" permission when creating
    the OAuth consumer.

**Email not returned**
    Make sure you've selected the "Email: Read" permission and that the user
    has at least one email address on their Bitbucket account.


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
