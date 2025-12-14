OAuth Providers
===============

litestar-oauth includes pre-built support for popular OAuth2 providers, plus a generic
provider class for any OAuth2/OIDC-compliant identity provider.

.. toctree::
   :maxdepth: 2

   github


Available Providers
-------------------

.. list-table::
   :header-rows: 1
   :widths: 15 25 30 30

   * - Provider
     - Class
     - Default Scopes
     - Features
   * - GitHub
     - ``GitHubOAuthProvider``
     - ``read:user``, ``user:email``
     - User profile, emails, avatar
   * - Google
     - ``GoogleOAuthProvider``
     - ``openid``, ``email``, ``profile``
     - OpenID Connect, email verified status
   * - Discord
     - ``DiscordOAuthProvider``
     - ``identify``, ``email``
     - User profile, avatar (CDN URL)
   * - Generic
     - ``GenericOAuthProvider``
     - Configurable
     - Any OAuth2/OIDC provider


Provider Configuration
----------------------

All providers require at minimum a ``client_id`` and ``client_secret``, which you obtain
by registering your application with the OAuth provider.

Standalone Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

   from litestar_oauth.providers import (
       GitHubOAuthProvider,
       GoogleOAuthProvider,
       DiscordOAuthProvider,
   )

   github = GitHubOAuthProvider(
       client_id="your-github-client-id",
       client_secret="your-github-client-secret",
       scope=["read:user", "user:email"],  # Optional: override defaults
   )

   google = GoogleOAuthProvider(
       client_id="your-google-client-id.apps.googleusercontent.com",
       client_secret="your-google-client-secret",
   )

   discord = DiscordOAuthProvider(
       client_id="your-discord-client-id",
       client_secret="your-discord-client-secret",
   )


With Litestar Plugin
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from litestar_oauth.contrib.litestar import OAuthConfig

   config = OAuthConfig(
       redirect_base_url="https://example.com",

       # GitHub
       github_client_id="your-github-client-id",
       github_client_secret="your-github-client-secret",

       # Google
       google_client_id="your-google-client-id",
       google_client_secret="your-google-client-secret",

       # Discord
       discord_client_id="your-discord-client-id",
       discord_client_secret="your-discord-client-secret",

       # Only enable specific providers (optional)
       enabled_providers=["github", "google"],
   )


User Info Mapping
-----------------

Each provider returns user information in their own format. litestar-oauth normalizes
this into a consistent ``OAuthUserInfo`` dataclass:

.. code-block:: python

   @dataclass(frozen=True, slots=True)
   class OAuthUserInfo:
       provider: str          # e.g., "github", "google"
       oauth_id: str          # Provider-specific user ID
       email: str | None      # User's email address
       email_verified: bool   # Whether email is verified
       username: str | None   # Username (if available)
       first_name: str | None # First name
       last_name: str | None  # Last name
       avatar_url: str | None # URL to user's avatar
       profile_url: str | None  # URL to user's profile page
       raw_data: dict         # Complete raw response from provider


Provider-Specific Mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~

**GitHub**

- ``oauth_id``: GitHub user ID
- ``username``: GitHub login (e.g., "octocat")
- ``email``: Primary verified email (fetched via separate API call if not public)
- ``avatar_url``: GitHub avatar URL
- ``profile_url``: GitHub profile URL (e.g., "https://github.com/octocat")

**Google**

- ``oauth_id``: Google "sub" claim
- ``username``: Email address (Google doesn't provide usernames)
- ``email``: Google account email
- ``email_verified``: Always accurate from Google
- ``avatar_url``: Google profile picture URL

**Discord**

- ``oauth_id``: Discord snowflake ID
- ``username``: Discord username (with discriminator if applicable)
- ``email``: Discord account email
- ``avatar_url``: Discord CDN avatar URL (handles animated avatars)


Custom Scopes
-------------

Override default scopes when creating a provider:

.. code-block:: python

   # Request additional GitHub scopes
   github = GitHubOAuthProvider(
       client_id="...",
       client_secret="...",
       scope=["read:user", "user:email", "repo", "read:org"],
   )

   # Request additional Google scopes
   google = GoogleOAuthProvider(
       client_id="...",
       client_secret="...",
       scope=["openid", "email", "profile", "https://www.googleapis.com/auth/calendar.readonly"],
   )


Generic Provider
----------------

For OAuth2 providers not included by default, use ``GenericOAuthProvider``:

.. code-block:: python

   from litestar_oauth.providers import GenericOAuthProvider

   custom_provider = GenericOAuthProvider(
       provider_name="custom",
       client_id="your-client-id",
       client_secret="your-client-secret",
       authorize_url="https://auth.example.com/oauth/authorize",
       token_url="https://auth.example.com/oauth/token",
       user_info_url="https://api.example.com/userinfo",
       scope=["openid", "profile", "email"],
   )


Creating Custom Providers
-------------------------

For providers with unique requirements, extend ``BaseOAuthProvider``:

.. code-block:: python

   from litestar_oauth.base import BaseOAuthProvider
   from litestar_oauth.types import OAuthUserInfo


   class CustomProvider(BaseOAuthProvider):
       """Custom OAuth provider implementation."""

       @property
       def provider_name(self) -> str:
           return "custom"

       @property
       def authorize_url(self) -> str:
           return "https://auth.example.com/authorize"

       @property
       def token_url(self) -> str:
           return "https://auth.example.com/token"

       @property
       def user_info_url(self) -> str:
           return "https://api.example.com/me"

       def _default_scope(self) -> list[str]:
           return ["openid", "profile", "email"]

       async def get_user_info(self, access_token: str, **kwargs) -> OAuthUserInfo:
           import httpx

           async with httpx.AsyncClient() as client:
               response = await client.get(
                   self.user_info_url,
                   headers={"Authorization": f"Bearer {access_token}"},
               )
               response.raise_for_status()
               data = response.json()

           return OAuthUserInfo(
               provider=self.provider_name,
               oauth_id=str(data["id"]),
               email=data.get("email"),
               email_verified=data.get("email_verified", False),
               username=data.get("username"),
               first_name=data.get("given_name"),
               last_name=data.get("family_name"),
               avatar_url=data.get("picture"),
               profile_url=data.get("profile"),
               raw_data=data,
           )


Environment Variables
---------------------

For security, store OAuth credentials in environment variables:

.. code-block:: python

   import os
   from litestar_oauth.contrib.litestar import OAuthConfig

   config = OAuthConfig(
       redirect_base_url=os.environ["OAUTH_REDIRECT_BASE_URL"],
       github_client_id=os.environ.get("GITHUB_CLIENT_ID"),
       github_client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
       google_client_id=os.environ.get("GOOGLE_CLIENT_ID"),
       google_client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
   )

Example ``.env`` file:

.. code-block:: bash

   OAUTH_REDIRECT_BASE_URL=https://example.com
   GITHUB_CLIENT_ID=Iv1.abc123...
   GITHUB_CLIENT_SECRET=secret123...
   GOOGLE_CLIENT_ID=123456-abc.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-...


Next Steps
----------

- :doc:`github` - Detailed GitHub OAuth setup guide
- :doc:`/api/index` - Complete API reference
