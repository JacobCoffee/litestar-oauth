API Reference
=============

Complete API documentation for litestar-oauth. This reference covers all public
classes, functions, and types.


Base Classes
------------

Base classes and protocols for OAuth providers.

.. automodule:: litestar_oauth.base
   :members:
   :undoc-members:
   :show-inheritance:


Service
-------

The OAuthService manages providers and state.

.. automodule:: litestar_oauth.service
   :members:
   :undoc-members:
   :show-inheritance:


Types
-----

Core data types for OAuth operations.

.. automodule:: litestar_oauth.types
   :members:
   :undoc-members:
   :show-inheritance:


Exceptions
----------

Custom exception hierarchy for OAuth errors.

.. automodule:: litestar_oauth.exceptions
   :members:
   :undoc-members:
   :show-inheritance:


Providers
---------

Pre-built OAuth provider implementations.

GitHub Provider
~~~~~~~~~~~~~~~

.. automodule:: litestar_oauth.providers.github
   :members:
   :undoc-members:
   :show-inheritance:

Google Provider
~~~~~~~~~~~~~~~

.. automodule:: litestar_oauth.providers.google
   :members:
   :undoc-members:
   :show-inheritance:

Discord Provider
~~~~~~~~~~~~~~~~

.. automodule:: litestar_oauth.providers.discord
   :members:
   :undoc-members:
   :show-inheritance:

Generic Provider
~~~~~~~~~~~~~~~~

.. automodule:: litestar_oauth.providers.generic
   :members:
   :undoc-members:
   :show-inheritance:


Litestar Integration
--------------------

Components for Litestar framework integration.

.. note::

   The Litestar integration requires the ``litestar`` extra to be installed:

   .. code-block:: bash

      uv add litestar-oauth[litestar]

Configuration
~~~~~~~~~~~~~

.. automodule:: litestar_oauth.contrib.litestar.config
   :members:
   :undoc-members:
   :show-inheritance:


Testing Utilities
-----------------

Mock implementations for testing OAuth flows.

Mocks
~~~~~

.. automodule:: litestar_oauth.testing.mocks
   :members:
   :undoc-members:
   :show-inheritance:

Fixtures
~~~~~~~~

.. automodule:: litestar_oauth.testing.fixtures
   :members:
   :undoc-members:
   :show-inheritance:


Quick Reference
---------------

Common Classes
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Class
     - Description
   * - :class:`~litestar_oauth.service.OAuthService`
     - Central service for managing OAuth providers and state
   * - :class:`~litestar_oauth.service.OAuthStateManager`
     - Manages CSRF state tokens for OAuth flows
   * - :class:`~litestar_oauth.base.BaseOAuthProvider`
     - Abstract base class for OAuth providers
   * - :class:`~litestar_oauth.base.OAuthProvider`
     - Protocol defining the OAuth provider interface

Data Types
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Type
     - Description
   * - :class:`~litestar_oauth.types.OAuthUserInfo`
     - Normalized user information from OAuth providers
   * - :class:`~litestar_oauth.types.OAuthToken`
     - OAuth access token and metadata
   * - :class:`~litestar_oauth.types.OAuthState`
     - State parameter for CSRF protection

Providers
~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Provider
     - Description
   * - :class:`~litestar_oauth.providers.github.GitHubOAuthProvider`
     - GitHub OAuth2 authentication
   * - :class:`~litestar_oauth.providers.google.GoogleOAuthProvider`
     - Google OAuth2 with OpenID Connect
   * - :class:`~litestar_oauth.providers.discord.DiscordOAuthProvider`
     - Discord OAuth2 authentication
   * - :class:`~litestar_oauth.providers.generic.GenericOAuthProvider`
     - Configurable generic OAuth2 provider

Exceptions
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Exception
     - Description
   * - :class:`~litestar_oauth.exceptions.OAuthError`
     - Base exception for all OAuth errors
   * - :class:`~litestar_oauth.exceptions.ProviderNotConfiguredError`
     - Provider not registered or misconfigured
   * - :class:`~litestar_oauth.exceptions.TokenExchangeError`
     - Authorization code exchange failed
   * - :class:`~litestar_oauth.exceptions.TokenRefreshError`
     - Token refresh failed
   * - :class:`~litestar_oauth.exceptions.UserInfoError`
     - User info retrieval failed
   * - :class:`~litestar_oauth.exceptions.InvalidStateError`
     - Invalid or missing state parameter
   * - :class:`~litestar_oauth.exceptions.ExpiredStateError`
     - State token has expired

Litestar Components
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Component
     - Description
   * - :class:`~litestar_oauth.contrib.litestar.config.OAuthConfig`
     - Configuration dataclass for the plugin
