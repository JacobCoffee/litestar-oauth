litestar-oauth
==============

.. rst-class:: lead

   OAuth2 authentication plugin for Litestar.

----

**litestar-oauth** provides a clean, type-safe API for integrating OAuth2 providers into
your `Litestar <https://litestar.dev>`_ applications. Features automatic route registration,
built-in CSRF protection, and normalized user data across providers.

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item-card:: Getting Started
      :link: getting-started/index
      :link-type: doc

      New to litestar-oauth? Start here for installation and your first OAuth flow.

   .. grid-item-card:: Provider Guides
      :link: providers/index
      :link-type: doc

      Configure OAuth providers: GitHub, Google, Discord, and more.

   .. grid-item-card:: API Reference
      :link: api/index
      :link-type: doc

      Complete API documentation for all public classes and functions.

   .. grid-item-card:: Litestar Plugin
      :link: getting-started/quickstart
      :link-type: doc

      Deep integration with Litestar: routes, dependencies, and guards.


Key Features
------------

- **Async-First Design**: Native ``async/await`` throughout, built on httpx for HTTP operations
- **Provider Agnostic**: Pre-built providers for GitHub, Google, Discord, and more
- **Type-Safe**: Full typing with Protocol-based interfaces for IDE support and type checking
- **CSRF Protection**: Built-in state management to prevent cross-site request forgery
- **Litestar Integration**: Optional deep integration with Litestar's DI, guards, and plugin system
- **Extensible**: Easy to add custom providers for any OAuth2-compliant identity provider
- **Token Management**: Automatic token handling with refresh token support
- **User Info Normalization**: Consistent user data format across all providers


Quick Example
-------------

Here's a taste of what using litestar-oauth looks like:

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
                         github_client_id="your-client-id",
                         github_client_secret="your-client-secret",
                         google_client_id="your-google-id",
                         google_client_secret="your-google-secret",
                     )
                 )
             ],
         )

         # Routes automatically registered:
         # GET /auth/{provider}/login - Redirect to OAuth provider
         # GET /auth/{provider}/callback - Handle OAuth callback

   .. group-tab:: Standalone

      .. code-block:: python

         from litestar_oauth import OAuthService
         from litestar_oauth.providers import GitHubOAuthProvider

         # Configure providers
         github = GitHubOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
         )

         # Create service and register provider
         oauth_service = OAuthService()
         oauth_service.register(github)

         # Generate authorization URL
         auth_url = await oauth_service.get_authorization_url(
             provider_name="github",
             redirect_uri="https://example.com/callback",
         )

         # After user authorizes, exchange code for token
         provider = oauth_service.get_provider("github")
         token = await provider.exchange_code(
             code="authorization-code",
             redirect_uri="https://example.com/callback",
         )

         # Fetch user information
         user_info = await provider.get_user_info(token.access_token)
         print(f"Welcome, {user_info.username}!")


Installation
------------

.. tabs::

   .. group-tab:: uv

      .. code-block:: bash

         uv add litestar-oauth

   .. group-tab:: pip

      .. code-block:: bash

         pip install litestar-oauth

   .. group-tab:: pdm

      .. code-block:: bash

         pdm add litestar-oauth

   .. group-tab:: poetry

      .. code-block:: bash

         poetry add litestar-oauth

Includes Litestar and httpx by default. For provider-specific extras:

.. code-block:: bash

   # Apple Sign In (requires JWT signing)
   uv add litestar-oauth[apple]

   # All provider extras
   uv add litestar-oauth[all]


Supported Providers
-------------------

litestar-oauth includes built-in support for popular OAuth providers:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Provider
     - Class
     - Default Scopes
   * - GitHub
     - ``GitHubOAuthProvider``
     - ``read:user``, ``user:email``
   * - Google
     - ``GoogleOAuthProvider``
     - ``openid``, ``email``, ``profile``
   * - Discord
     - ``DiscordOAuthProvider``
     - ``identify``, ``email``
   * - Microsoft
     - ``MicrosoftOAuthProvider``
     - ``openid``, ``email``, ``profile``
   * - GitLab
     - ``GitLabOAuthProvider``
     - ``read_user``, ``email``
   * - Twitter/X
     - ``TwitterOAuthProvider``
     - ``users.read``, ``tweet.read``
   * - Facebook
     - ``FacebookOAuthProvider``
     - ``email``, ``public_profile``
   * - LinkedIn
     - ``LinkedInOAuthProvider``
     - ``openid``, ``email``, ``profile``
   * - Bitbucket
     - ``BitbucketOAuthProvider``
     - ``account``, ``email``
   * - Generic
     - ``GenericOAuthProvider``
     - Configurable


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Learn

   getting-started/index
   providers/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Reference

   api/index

.. toctree::
   :hidden:
   :caption: Project

   GitHub <https://github.com/JacobCoffee/litestar-oauth>
   Discord <https://discord.gg/litestar-919193495116337154>


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
