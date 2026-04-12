API Reference
=============

Complete API documentation for litestar-oauth.

.. contents:: On this page
   :local:
   :depth: 2


Core Types
----------

OAuthUserInfo
~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.types.OAuthUserInfo
   :no-index:

OAuthToken
~~~~~~~~~~

.. autoclass:: litestar_oauth.types.OAuthToken
   :no-index:

OAuthState
~~~~~~~~~~

.. autoclass:: litestar_oauth.types.OAuthState
   :no-index:


Service
-------

OAuthService
~~~~~~~~~~~~

.. autoclass:: litestar_oauth.service.OAuthService
   :members:
   :no-index:

OAuthStateManager
~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.service.OAuthStateManager
   :members:
   :no-index:


Base Classes
------------

BaseOAuthProvider
~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.base.BaseOAuthProvider
   :members:
   :no-index:

OAuthProvider
~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.base.OAuthProvider
   :members:
   :no-index:


Providers
---------

GitHubOAuthProvider
~~~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.providers.github.GitHubOAuthProvider
   :members:
   :show-inheritance:
   :no-index:

GoogleOAuthProvider
~~~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.providers.google.GoogleOAuthProvider
   :members:
   :show-inheritance:
   :no-index:

DiscordOAuthProvider
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.providers.discord.DiscordOAuthProvider
   :members:
   :show-inheritance:
   :no-index:

GenericOAuthProvider
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.providers.generic.GenericOAuthProvider
   :members:
   :show-inheritance:
   :no-index:


Exceptions
----------

.. automodule:: litestar_oauth.exceptions
   :members:
   :show-inheritance:
   :no-index:


Litestar Integration
--------------------

OAuthConfig
~~~~~~~~~~~

.. autoclass:: litestar_oauth.contrib.litestar.config.OAuthConfig
   :no-index:


Testing Utilities
-----------------

MockOAuthProvider
~~~~~~~~~~~~~~~~~

.. autoclass:: litestar_oauth.testing.mocks.MockOAuthProvider
   :members:
   :no-index:
