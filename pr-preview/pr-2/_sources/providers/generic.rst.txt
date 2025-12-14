Generic OAuth Provider
======================

The Generic OAuth Provider allows you to integrate with any OAuth2 or OpenID Connect
compliant identity provider.


When to Use
-----------

Use the Generic provider when:

- Integrating with a custom identity provider
- Using an enterprise IdP like Keycloak, Auth0, or Okta
- The built-in providers don't cover your needs
- You need full control over endpoint configuration


Basic Configuration
-------------------

.. tabs::

   .. group-tab:: Manual Endpoints

      .. code-block:: python

         from litestar_oauth.providers import GenericOAuthProvider

         provider = GenericOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
             provider_name="custom-idp",
             authorize_url="https://idp.example.com/oauth/authorize",
             token_url="https://idp.example.com/oauth/token",
             user_info_url="https://idp.example.com/oauth/userinfo",
             scope=["openid", "email", "profile"],
         )

   .. group-tab:: OIDC Discovery

      .. code-block:: python

         from litestar_oauth.providers import GenericOAuthProvider

         # Endpoints are discovered automatically from .well-known/openid-configuration
         provider = GenericOAuthProvider(
             client_id="your-client-id",
             client_secret="your-client-secret",
             provider_name="custom-idp",
             discovery_url="https://idp.example.com/.well-known/openid-configuration",
         )


Field Mapping
-------------

Different identity providers use different field names in their user info responses.
Customize the mapping to match your IdP::

   provider = GenericOAuthProvider(
       client_id="your-client-id",
       client_secret="your-client-secret",
       provider_name="custom-idp",
       authorize_url="https://idp.example.com/oauth/authorize",
       token_url="https://idp.example.com/oauth/token",
       user_info_url="https://idp.example.com/oauth/userinfo",
       # Custom field mappings
       user_id_field="id",            # Default: "sub"
       email_field="mail",            # Default: "email"
       username_field="login",        # Default: "preferred_username"
       first_name_field="firstName",  # Default: "given_name"
       last_name_field="lastName",    # Default: "family_name"
       avatar_url_field="avatarUrl",  # Default: "picture"
   )


Enterprise IdP Examples
-----------------------

Keycloak
~~~~~~~~

.. code-block:: python

   from litestar_oauth.providers import GenericOAuthProvider

   keycloak = GenericOAuthProvider(
       client_id="your-client-id",
       client_secret="your-client-secret",
       provider_name="keycloak",
       authorize_url="https://keycloak.example.com/realms/myrealm/protocol/openid-connect/auth",
       token_url="https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token",
       user_info_url="https://keycloak.example.com/realms/myrealm/protocol/openid-connect/userinfo",
       scope=["openid", "email", "profile"],
   )


Auth0
~~~~~

.. code-block:: python

   from litestar_oauth.providers import GenericOAuthProvider

   auth0 = GenericOAuthProvider(
       client_id="your-client-id",
       client_secret="your-client-secret",
       provider_name="auth0",
       discovery_url="https://your-tenant.auth0.com/.well-known/openid-configuration",
       scope=["openid", "email", "profile"],
   )


Okta
~~~~

.. code-block:: python

   from litestar_oauth.providers import GenericOAuthProvider

   okta = GenericOAuthProvider(
       client_id="your-client-id",
       client_secret="your-client-secret",
       provider_name="okta",
       discovery_url="https://your-org.okta.com/.well-known/openid-configuration",
       scope=["openid", "email", "profile"],
   )


Azure AD / Entra ID
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from litestar_oauth.providers import GenericOAuthProvider

   azure_ad = GenericOAuthProvider(
       client_id="your-client-id",
       client_secret="your-client-secret",
       provider_name="azure",
       discovery_url="https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration",
       scope=["openid", "email", "profile"],
   )


Using with Litestar Plugin
--------------------------

For providers not built into the config, register them manually::

   from litestar import Litestar
   from litestar_oauth import OAuthService
   from litestar_oauth.providers import GenericOAuthProvider
   from litestar_oauth.contrib.litestar import OAuthPlugin, OAuthConfig

   # Create custom provider
   custom_provider = GenericOAuthProvider(
       client_id="your-client-id",
       client_secret="your-client-secret",
       provider_name="custom",
       authorize_url="https://idp.example.com/oauth/authorize",
       token_url="https://idp.example.com/oauth/token",
       user_info_url="https://idp.example.com/oauth/userinfo",
   )

   # Create service with custom provider
   oauth_service = OAuthService()
   oauth_service.register(custom_provider)

   # Use with plugin (the plugin will use your pre-configured service)
   app = Litestar(
       plugins=[
           OAuthPlugin(
               config=OAuthConfig(
                   redirect_base_url="https://example.com",
               )
           )
       ],
       state={"oauth_service": oauth_service},
   )


OIDC Discovery
--------------

When using OIDC discovery, the provider automatically fetches configuration from
the ``.well-known/openid-configuration`` endpoint::

   {
       "issuer": "https://idp.example.com",
       "authorization_endpoint": "https://idp.example.com/oauth/authorize",
       "token_endpoint": "https://idp.example.com/oauth/token",
       "userinfo_endpoint": "https://idp.example.com/oauth/userinfo",
       "jwks_uri": "https://idp.example.com/.well-known/jwks.json",
       ...
   }

This simplifies configuration and ensures endpoints are always up-to-date.
