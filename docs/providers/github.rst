GitHub OAuth
============

This guide covers setting up GitHub as an OAuth provider for your application.
GitHub OAuth is commonly used for developer tools, open-source projects, and
applications targeting the developer community.


Creating a GitHub OAuth App
---------------------------

Step 1: Navigate to Developer Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://github.com/settings/developers
2. Click on "OAuth Apps" in the sidebar
3. Click "New OAuth App"

Step 2: Configure Your Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fill in the required fields:

**Application name**
    A descriptive name for your app (e.g., "My Awesome App")

**Homepage URL**
    Your application's homepage (e.g., ``https://myapp.com``)

**Authorization callback URL**
    Where GitHub redirects after authorization.
    For development: ``http://localhost:8000/auth/github/callback``
    For production: ``https://myapp.com/auth/github/callback``

**Application description** (optional)
    A brief description shown to users during authorization

Step 3: Get Your Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After creating the app:

1. Note your **Client ID** (visible immediately)
2. Click "Generate a new client secret"
3. Copy your **Client Secret** (only shown once!)

.. warning::

   Never commit your Client Secret to version control. Use environment variables
   or a secrets manager.


Configuration
-------------

Standalone Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

   from litestar_oauth.providers import GitHubOAuthProvider

   github = GitHubOAuthProvider(
       client_id="Iv1.abc123456789",
       client_secret="your-client-secret",
   )

With Litestar Plugin
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from litestar_oauth.contrib.litestar import OAuthConfig

   config = OAuthConfig(
       redirect_base_url="https://myapp.com",
       github_client_id="Iv1.abc123456789",
       github_client_secret="your-client-secret",
       github_scope="read:user user:email",
   )

Using Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os

   github = GitHubOAuthProvider(
       client_id=os.environ["GITHUB_CLIENT_ID"],
       client_secret=os.environ["GITHUB_CLIENT_SECRET"],
   )


Available Scopes
----------------

GitHub offers various scopes to access different parts of the API:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Scope
     - Description
   * - ``(no scope)``
     - Public read-only access
   * - ``read:user``
     - Read user profile data
   * - ``user:email``
     - Access email addresses (including private)
   * - ``user:follow``
     - Follow and unfollow users
   * - ``repo``
     - Full access to repositories
   * - ``repo:status``
     - Access commit statuses
   * - ``read:org``
     - Read organization membership
   * - ``admin:org``
     - Full access to organization
   * - ``gist``
     - Create and manage gists
   * - ``notifications``
     - Access notifications
   * - ``delete_repo``
     - Delete repositories

**Default scopes in litestar-oauth:** ``read:user``, ``user:email``

Custom Scopes Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Access user profile, emails, and public repos
   github = GitHubOAuthProvider(
       client_id="...",
       client_secret="...",
       scope=["read:user", "user:email", "public_repo"],
   )


Complete Example
----------------

Here's a complete example with GitHub OAuth:

.. code-block:: python

   # app.py
   from litestar import Litestar, get
   from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig
   from litestar_oauth import OAuthUserInfo


   @get("/")
   async def home() -> dict:
       return {
           "message": "Welcome! Sign in with GitHub.",
           "login": "/auth/github/login",
       }


   @get("/profile")
   async def profile(oauth_user_info: OAuthUserInfo) -> dict:
       return {
           "id": oauth_user_info.oauth_id,
           "username": oauth_user_info.username,
           "email": oauth_user_info.email,
           "email_verified": oauth_user_info.email_verified,
           "avatar": oauth_user_info.avatar_url,
           "profile": oauth_user_info.profile_url,
           "full_name": oauth_user_info.full_name,
       }


   app = Litestar(
       route_handlers=[home, profile],
       plugins=[
           OAuthPlugin(
               config=OAuthConfig(
                   redirect_base_url="http://localhost:8000",
                   success_redirect="/profile",
                   github_client_id="your-client-id",
                   github_client_secret="your-client-secret",
               )
           )
       ],
   )


User Info Response
------------------

GitHub's user info endpoint returns extensive data. Here's what litestar-oauth extracts:

.. code-block:: python

   OAuthUserInfo(
       provider="github",
       oauth_id="1234567",                        # GitHub user ID
       email="octocat@example.com",               # Primary verified email
       email_verified=True,                       # From email verification status
       username="octocat",                        # GitHub login
       first_name="Mona",                         # Parsed from name field
       last_name="Octocat",                       # Parsed from name field
       avatar_url="https://avatars.githubusercontent.com/u/1234567",
       profile_url="https://github.com/octocat",
       raw_data={...},                            # Complete API response
   )


Accessing Additional Data
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``raw_data`` field contains the complete GitHub API response:

.. code-block:: python

   user_info = await provider.get_user_info(access_token)

   # Access additional fields
   company = user_info.raw_data.get("company")
   location = user_info.raw_data.get("location")
   bio = user_info.raw_data.get("bio")
   public_repos = user_info.raw_data.get("public_repos")
   followers = user_info.raw_data.get("followers")
   following = user_info.raw_data.get("following")
   created_at = user_info.raw_data.get("created_at")


Fetching Private Emails
-----------------------

If the user's email is private, litestar-oauth automatically makes an additional
API call to ``/user/emails`` to fetch their verified email addresses:

.. code-block:: python

   # This is handled automatically by GitHubOAuthProvider
   # The primary verified email is selected, or falls back to
   # any verified email, or finally the first email in the list

   user_info = await provider.get_user_info(access_token)
   print(user_info.email)  # Works even for private emails


Making Additional API Calls
---------------------------

Use the access token to make additional GitHub API calls:

.. code-block:: python

   import httpx

   async def get_user_repos(access_token: str) -> list:
       """Fetch user's repositories."""
       async with httpx.AsyncClient() as client:
           response = await client.get(
               "https://api.github.com/user/repos",
               headers={
                   "Authorization": f"Bearer {access_token}",
                   "Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
               },
               params={
                   "sort": "updated",
                   "per_page": 10,
               },
           )
           response.raise_for_status()
           return response.json()


   async def get_user_orgs(access_token: str) -> list:
       """Fetch user's organizations (requires read:org scope)."""
       async with httpx.AsyncClient() as client:
           response = await client.get(
               "https://api.github.com/user/orgs",
               headers={
                   "Authorization": f"Bearer {access_token}",
                   "Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
               },
           )
           response.raise_for_status()
           return response.json()


Token Management
----------------

GitHub access tokens don't expire by default, but you can still store and manage them:

.. code-block:: python

   from litestar_oauth import OAuthToken

   # Exchange code for token
   token: OAuthToken = await provider.exchange_code(code, redirect_uri)

   # Token attributes
   print(token.access_token)      # The access token
   print(token.token_type)        # "bearer"
   print(token.scope)             # Granted scopes
   print(token.expires_in)        # None for GitHub (no expiration)
   print(token.refresh_token)     # None for GitHub (not provided)

   # Store the access token securely for future API calls
   # await store_token(user_id, token.access_token)


GitHub Enterprise
-----------------

For GitHub Enterprise, you'll need to use the ``GenericOAuthProvider`` with your
enterprise domain:

.. code-block:: python

   from litestar_oauth.providers import GenericOAuthProvider

   github_enterprise = GenericOAuthProvider(
       provider_name="github-enterprise",
       client_id="your-client-id",
       client_secret="your-client-secret",
       authorize_url="https://github.mycompany.com/login/oauth/authorize",
       token_url="https://github.mycompany.com/login/oauth/access_token",
       user_info_url="https://github.mycompany.com/api/v3/user",
       scope=["read:user", "user:email"],
   )


Troubleshooting
---------------

**"redirect_uri_mismatch" error**
    The callback URL in your code doesn't match what's registered in GitHub.
    Make sure they're identical, including trailing slashes.

**"bad_verification_code" error**
    The authorization code has expired or was already used. Codes are single-use
    and expire after 10 minutes.

**Empty email in user info**
    The user's email might be private. Ensure you're requesting the ``user:email``
    scope and that litestar-oauth is fetching emails from the ``/user/emails`` endpoint.

**Rate limiting**
    GitHub has rate limits on API calls. Authenticated requests get 5,000 requests/hour.
    Consider caching user info to reduce API calls.


Next Steps
----------

- :doc:`/providers/index` - Explore other OAuth providers
- :doc:`/api/index` - Complete API reference
- :doc:`/getting-started/quickstart` - Full tutorial with code examples
