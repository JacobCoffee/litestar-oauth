Quickstart
==========

This tutorial walks you through creating your first OAuth2 integration with
litestar-oauth. In about 15 minutes, you'll build a complete authentication
flow that lets users sign in with GitHub.


What We're Building
-------------------

We'll create a simple web application that:

1. Redirects users to GitHub for authentication
2. Handles the OAuth callback with authorization code
3. Exchanges the code for an access token
4. Retrieves and displays user information

.. code-block:: text

   [Your App]                    [GitHub]                    [User]
       |                            |                           |
       |----> Login button click ---|                           |
       |      (redirect to GitHub)  |<---- User sees login -----|
       |                            |      page                 |
       |                            |<---- User approves -------|
       |<---- Callback with code ---|                           |
       |----> Exchange code ------->|                           |
       |<---- Access token ---------|                           |
       |----> Get user info ------->|                           |
       |<---- User data ------------|                           |
       |----> Show profile ---------|-------------------------->|


Prerequisites
-------------

Before starting, you'll need:

1. **Python 3.9+** installed
2. **A GitHub OAuth App** - Create one at https://github.com/settings/developers

   - Set the callback URL to ``http://localhost:8000/auth/github/callback``
   - Note your Client ID and Client Secret

3. **Dependencies installed**:

   .. code-block:: bash

      pip install litestar-oauth[litestar] uvicorn


Option 1: Standalone Usage
--------------------------

Let's start with the simplest approach - using litestar-oauth without any web framework.

Step 1: Configure the Provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # standalone_example.py
   import asyncio
   from litestar_oauth import OAuthService
   from litestar_oauth.providers import GitHubOAuthProvider

   # Create the GitHub provider with your credentials
   github = GitHubOAuthProvider(
       client_id="your-github-client-id",      # Replace with your Client ID
       client_secret="your-github-client-secret",  # Replace with your Client Secret
   )

   # Create the service and register the provider
   oauth_service = OAuthService()
   oauth_service.register(github)

Step 2: Generate Authorization URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def start_oauth_flow():
       """Generate the URL to send users to GitHub."""
       auth_url = await oauth_service.get_authorization_url(
           provider_name="github",
           redirect_uri="http://localhost:8000/auth/github/callback",
           next_url="/dashboard",  # Where to redirect after successful auth
       )
       print(f"Redirect user to: {auth_url}")
       return auth_url

Step 3: Handle the Callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def handle_callback(code: str, state: str):
       """Process the OAuth callback from GitHub."""
       # Validate the state parameter (CSRF protection)
       oauth_state = oauth_service.state_manager.consume_state(
           state=state,
           provider="github",
       )

       # Get the provider
       provider = oauth_service.get_provider("github")

       # Exchange the authorization code for an access token
       token = await provider.exchange_code(
           code=code,
           redirect_uri=oauth_state.redirect_uri,
       )

       print(f"Access Token: {token.access_token[:20]}...")
       print(f"Token Type: {token.token_type}")

       # Get user information
       user_info = await provider.get_user_info(token.access_token)

       print(f"User ID: {user_info.oauth_id}")
       print(f"Username: {user_info.username}")
       print(f"Email: {user_info.email}")
       print(f"Avatar: {user_info.avatar_url}")

       return user_info

Step 4: Complete Example
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # standalone_example.py
   import asyncio
   from litestar_oauth import OAuthService
   from litestar_oauth.providers import GitHubOAuthProvider

   # Setup
   github = GitHubOAuthProvider(
       client_id="your-github-client-id",
       client_secret="your-github-client-secret",
   )

   oauth_service = OAuthService()
   oauth_service.register(github)


   async def main():
       # Generate the authorization URL
       auth_url = await oauth_service.get_authorization_url(
           provider_name="github",
           redirect_uri="http://localhost:8000/auth/github/callback",
       )
       print(f"\n1. Open this URL in your browser:\n   {auth_url}\n")
       print("2. Authorize the application")
       print("3. Copy the 'code' parameter from the callback URL\n")

       # In a real app, this would come from the callback request
       code = input("Enter the authorization code: ").strip()

       # Get the state from our storage
       # (In a real app, this comes from the callback URL too)
       states = list(oauth_service.state_manager._states.keys())
       if not states:
           print("Error: No state found")
           return

       state = states[0]

       # Process the callback
       oauth_state = oauth_service.state_manager.consume_state(state, "github")
       provider = oauth_service.get_provider("github")

       token = await provider.exchange_code(
           code=code,
           redirect_uri=oauth_state.redirect_uri,
       )

       user_info = await provider.get_user_info(token.access_token)

       print(f"\nWelcome, {user_info.username}!")
       print(f"Email: {user_info.email}")
       print(f"Profile: {user_info.profile_url}")


   if __name__ == "__main__":
       asyncio.run(main())


Option 2: With Litestar Plugin
------------------------------

For web applications, the Litestar plugin provides a much smoother experience
with automatic route registration and dependency injection.

Step 1: Create the Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # app.py
   from litestar import Litestar, get
   from litestar.response import Redirect

   from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig
   from litestar_oauth import OAuthService, OAuthUserInfo


   @get("/")
   async def home() -> dict:
       """Home page with login link."""
       return {
           "message": "Welcome! Click below to sign in.",
           "login_url": "/auth/github/login",
       }


   @get("/dashboard")
   async def dashboard(oauth_user_info: OAuthUserInfo) -> dict:
       """Protected dashboard showing user info."""
       return {
           "message": f"Welcome back, {oauth_user_info.username}!",
           "user": {
               "id": oauth_user_info.oauth_id,
               "username": oauth_user_info.username,
               "email": oauth_user_info.email,
               "avatar": oauth_user_info.avatar_url,
               "provider": oauth_user_info.provider,
           },
       }


   # Configure the OAuth plugin
   oauth_config = OAuthConfig(
       redirect_base_url="http://localhost:8000",
       route_prefix="/auth",
       success_redirect="/dashboard",
       failure_redirect="/?error=auth_failed",

       # GitHub credentials
       github_client_id="your-github-client-id",
       github_client_secret="your-github-client-secret",

       # Optional: Add more providers
       # google_client_id="your-google-client-id",
       # google_client_secret="your-google-client-secret",
   )


   app = Litestar(
       route_handlers=[home, dashboard],
       plugins=[OAuthPlugin(config=oauth_config)],
   )

Step 2: Run the Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uvicorn app:app --reload

Step 3: Test the Flow
~~~~~~~~~~~~~~~~~~~~~

1. Open http://localhost:8000 in your browser
2. Click the login link to go to ``/auth/github/login``
3. Authorize the app on GitHub
4. You'll be redirected to ``/dashboard`` with your user info


Understanding the Plugin
------------------------

The ``OAuthPlugin`` automatically registers these routes:

``GET /auth/{provider}/login``
    Redirects the user to the OAuth provider's authorization page.
    The ``{provider}`` can be ``github``, ``google``, ``discord``, etc.

``GET /auth/{provider}/callback``
    Handles the callback from the OAuth provider. Validates the state,
    exchanges the code for a token, and redirects to ``success_redirect``.

The plugin also provides these dependencies:

``oauth_service: OAuthService``
    The configured OAuth service with all registered providers.

``oauth_user_info: OAuthUserInfo``
    The authenticated user's information (populated after successful OAuth).


Adding Multiple Providers
-------------------------

You can easily support multiple OAuth providers:

.. code-block:: python

   oauth_config = OAuthConfig(
       redirect_base_url="http://localhost:8000",

       # GitHub
       github_client_id="your-github-client-id",
       github_client_secret="your-github-client-secret",

       # Google
       google_client_id="your-google-client-id",
       google_client_secret="your-google-client-secret",

       # Discord
       discord_client_id="your-discord-client-id",
       discord_client_secret="your-discord-client-secret",

       # Only enable specific providers
       enabled_providers=["github", "google"],
   )

Users can then authenticate via:

- ``/auth/github/login`` - Sign in with GitHub
- ``/auth/google/login`` - Sign in with Google


Handling Errors
---------------

OAuth can fail for various reasons. Here's how to handle common errors:

.. code-block:: python

   from litestar import get
   from litestar.exceptions import HTTPException

   from litestar_oauth.exceptions import (
       OAuthError,
       TokenExchangeError,
       InvalidStateError,
       ExpiredStateError,
   )


   @get("/auth/callback")
   async def custom_callback(code: str, state: str, oauth_service: OAuthService) -> dict:
       try:
           # Validate state
           oauth_state = oauth_service.state_manager.consume_state(state)

           # Exchange code
           provider = oauth_service.get_provider(oauth_state.provider)
           token = await provider.exchange_code(code, oauth_state.redirect_uri)

           # Get user info
           user_info = await provider.get_user_info(token.access_token)

           return {"user": user_info.username}

       except InvalidStateError:
           raise HTTPException(status_code=400, detail="Invalid or missing state parameter")

       except ExpiredStateError:
           raise HTTPException(status_code=400, detail="Authorization request expired. Please try again.")

       except TokenExchangeError as e:
           raise HTTPException(status_code=400, detail=f"Failed to exchange authorization code: {e}")

       except OAuthError as e:
           raise HTTPException(status_code=500, detail=f"OAuth error: {e}")


Storing User Sessions
---------------------

After successful authentication, you'll typically want to create a session:

.. code-block:: python

   from litestar import get, post
   from litestar.datastructures import Cookie
   from litestar.response import Response

   @get("/auth/github/callback")
   async def github_callback(
       code: str,
       state: str,
       oauth_service: OAuthService,
   ) -> Response:
       # Validate and get user info
       oauth_state = oauth_service.state_manager.consume_state(state, "github")
       provider = oauth_service.get_provider("github")
       token = await provider.exchange_code(code, oauth_state.redirect_uri)
       user_info = await provider.get_user_info(token.access_token)

       # Create or update user in your database
       # user = await create_or_update_user(user_info)

       # Create a session (simplified example)
       session_token = create_session_token(user_info.oauth_id)

       response = Response(
           content={"message": "Login successful"},
           status_code=302,
           headers={"Location": oauth_state.next_url or "/dashboard"},
       )
       response.set_cookie(
           key="session",
           value=session_token,
           httponly=True,
           secure=True,
           samesite="lax",
       )
       return response


Next Steps
----------

Congratulations! You've built your first OAuth2 integration. Here's where to go next:

- :doc:`/providers/index` - Configure different OAuth providers
- :doc:`/providers/github` - Detailed GitHub OAuth setup guide
- :doc:`/api/index` - Complete API reference
