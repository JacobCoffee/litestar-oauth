Getting Started
===============

Welcome to litestar-oauth! This section will help you get up and running quickly
with OAuth2 authentication in your Python applications.

Whether you're building a standalone application or integrating with Litestar,
you'll find everything you need to authenticate users via OAuth2 providers.

.. toctree::
   :maxdepth: 2

   quickstart


What You'll Learn
-----------------

By the end of this section, you'll understand:

- How to install litestar-oauth and its optional dependencies
- The OAuth2 authorization flow and how litestar-oauth implements it
- How to configure OAuth providers (GitHub, Google, Discord, etc.)
- How to use the library standalone or with the Litestar plugin
- How to handle OAuth callbacks and retrieve user information


Prerequisites
-------------

Before you begin, make sure you have:

- Python 3.9 or later
- Basic understanding of OAuth2 concepts (authorization codes, tokens, scopes)
- (Optional) Familiarity with `Litestar <https://litestar.dev>`_ web framework


Installation
------------

Install the core library using pip:

.. code-block:: bash

   pip install litestar-oauth

This installs the core OAuth2 functionality with httpx for HTTP operations.

Optional Extras
~~~~~~~~~~~~~~~

For Litestar integration:

.. code-block:: bash

   pip install litestar-oauth[litestar]

For all extras:

.. code-block:: bash

   pip install litestar-oauth[all]


Basic Concepts
--------------

OAuth2 Flow Overview
~~~~~~~~~~~~~~~~~~~~

litestar-oauth implements the standard OAuth2 Authorization Code flow:

1. **Authorization Request**: Your app redirects the user to the OAuth provider
2. **User Authorization**: The user grants permission on the provider's site
3. **Authorization Callback**: The provider redirects back with an authorization code
4. **Token Exchange**: Your app exchanges the code for an access token
5. **API Access**: Use the access token to fetch user information

.. code-block:: text

   Your App                      OAuth Provider                    User
      |                               |                              |
      |----(1) Authorization URL----->|                              |
      |                               |<----(2) User Grants Access---|
      |<---(3) Callback with code-----|                              |
      |----(4) Exchange code--------->|                              |
      |<---(5) Access Token-----------|                              |
      |----(6) Get User Info--------->|                              |
      |<---(7) User Data--------------|                              |


Key Components
~~~~~~~~~~~~~~

**OAuthProvider Protocol**
    Defines the interface all providers must implement. Includes methods for
    generating authorization URLs, exchanging codes, and fetching user info.

**BaseOAuthProvider**
    Abstract base class with common OAuth2 logic. Extend this to create
    custom providers.

**OAuthService**
    Manages multiple providers and handles state management for CSRF protection.

**OAuthStateManager**
    Generates and validates state tokens to prevent cross-site request forgery.


Usage Without Litestar
----------------------

You can use litestar-oauth in any Python application:

.. code-block:: python

   from litestar_oauth import OAuthService
   from litestar_oauth.providers import GitHubOAuthProvider

   # Create and configure provider
   github = GitHubOAuthProvider(
       client_id="your-github-client-id",
       client_secret="your-github-client-secret",
   )

   # Create service and register provider
   oauth = OAuthService()
   oauth.register(github)

   # Step 1: Generate authorization URL
   auth_url = await oauth.get_authorization_url(
       provider_name="github",
       redirect_uri="https://yourapp.com/callback",
       next_url="/dashboard",  # Where to redirect after auth
   )
   # Redirect user to auth_url...

   # Step 2: Handle callback (in your callback endpoint)
   # Validate state and exchange code for token
   state = "state-from-callback"
   code = "code-from-callback"

   oauth_state = oauth.state_manager.consume_state(state, provider="github")
   provider = oauth.get_provider("github")

   token = await provider.exchange_code(
       code=code,
       redirect_uri=oauth_state.redirect_uri,
   )

   # Step 3: Get user information
   user_info = await provider.get_user_info(token.access_token)
   print(f"User: {user_info.username}, Email: {user_info.email}")


Usage With Litestar
-------------------

The Litestar plugin handles routing and dependency injection automatically:

.. code-block:: python

   from litestar import Litestar, get
   from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig
   from litestar_oauth.types import OAuthUserInfo

   @get("/profile")
   async def profile(oauth_user_info: OAuthUserInfo) -> dict:
       return {
           "username": oauth_user_info.username,
           "email": oauth_user_info.email,
           "provider": oauth_user_info.provider,
       }

   app = Litestar(
       route_handlers=[profile],
       plugins=[
           OAuthPlugin(
               config=OAuthConfig(
                   redirect_base_url="https://example.com",
                   github_client_id="your-client-id",
                   github_client_secret="your-client-secret",
                   success_redirect="/profile",
               )
           )
       ],
   )

The plugin automatically registers:

- ``GET /auth/{provider}/login`` - Initiates OAuth flow
- ``GET /auth/{provider}/callback`` - Handles provider callback

And provides dependencies:

- ``oauth_service`` - The configured OAuthService instance
- ``oauth_user_info`` - Current user's OAuth info (when authenticated)


Next Steps
----------

Ready to dive deeper? Continue with the :doc:`quickstart` tutorial to build
your first complete OAuth integration, or jump to :doc:`/providers/index` to
configure specific providers.
