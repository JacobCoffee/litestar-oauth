GitLab OAuth
============

This guide covers setting up GitLab as an OAuth provider for your application.
GitLab OAuth works with both GitLab.com and self-hosted GitLab instances.


Creating a GitLab OAuth Application
-----------------------------------

Step 1: Navigate to Application Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For GitLab.com:**

1. Go to https://gitlab.com/-/user_settings/applications
2. Or: User Settings > Applications

**For Self-Hosted GitLab:**

1. Go to ``https://your-gitlab.com/-/user_settings/applications``
2. For group-level apps: Group Settings > Applications
3. For instance-wide apps (admin): Admin Area > Applications

Step 2: Configure Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fill in the required fields:

**Name**
    A descriptive name for your app (e.g., "My Awesome App")

**Redirect URI**
    Where GitLab redirects after authorization.
    For development: ``http://localhost:8000/auth/gitlab/callback``
    For production: ``https://myapp.com/auth/gitlab/callback``

**Scopes**
    Select the scopes your application needs:
    - ``read_user`` (recommended)
    - ``email`` (if you need email access)

Step 3: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After creating the app:

1. Note your **Application ID** (client ID)
2. Copy your **Secret** (client secret)

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
                         gitlab_client_id="your-application-id",
                         gitlab_client_secret="your-secret",
                         gitlab_url="https://gitlab.com",  # or your self-hosted URL
                         gitlab_scope="read_user email",
                     )
                 )
             ],
         )

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth.providers import GitLabOAuthProvider

         # For GitLab.com
         provider = GitLabOAuthProvider(
             client_id="your-application-id",
             client_secret="your-secret",
             scope=["read_user", "email"],
         )

         # For self-hosted GitLab
         provider = GitLabOAuthProvider(
             client_id="your-application-id",
             client_secret="your-secret",
             base_url="https://gitlab.mycompany.com",
             scope=["read_user", "email"],
         )

         # Generate authorization URL
         auth_url = await provider.get_authorization_url(
             redirect_uri="https://example.com/auth/gitlab/callback",
             state="random-state-token",
         )

         # After callback, exchange code for token
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/auth/gitlab/callback",
         )

         # Get user info
         user_info = await provider.get_user_info(token.access_token)


Self-Hosted GitLab
------------------

To use a self-hosted GitLab instance, provide the ``base_url`` parameter:

.. code-block:: python

   provider = GitLabOAuthProvider(
       client_id="your-application-id",
       client_secret="your-secret",
       base_url="https://gitlab.mycompany.com",
   )

The provider will automatically construct the correct OAuth endpoints based on your base URL.


Available Scopes
----------------

GitLab offers various scopes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``read_user``
     - Read user profile (username, email, avatar)
   * - ``email``
     - Read user's email address
   * - ``api``
     - Full API access (read/write)
   * - ``read_api``
     - Read-only API access
   * - ``read_repository``
     - Read repository contents
   * - ``write_repository``
     - Write to repository
   * - ``openid``
     - OpenID Connect authentication
   * - ``profile``
     - Read user profile info (OIDC)

**Default scopes in litestar-oauth:** ``read_user``, ``email``


User Info Response
------------------

GitLab API returns user data. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="gitlab",
       oauth_id="12345",                        # GitLab user ID
       email="user@example.com",                # User email
       email_verified=True,                     # Based on confirmed_at field
       username="johndoe",                      # GitLab username
       first_name="John",                       # Parsed from name field
       last_name="Doe",                         # Parsed from name field
       avatar_url="https://gitlab.com/uploads/-/system/user/avatar/...",
       profile_url="https://gitlab.com/johndoe",
       raw_data={...},                          # Complete API response
   )


Troubleshooting
---------------

**"Invalid redirect URI"**
    The callback URL must exactly match what's registered in GitLab, including
    the protocol (http/https) and any trailing slashes.

**"401 Unauthorized" when fetching user info**
    Check that you've requested the ``read_user`` scope and that your access
    token hasn't expired.

**Self-hosted SSL errors**
    If your self-hosted GitLab uses a self-signed certificate, you may need to
    configure httpx to trust it or disable verification (not recommended for production).


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
