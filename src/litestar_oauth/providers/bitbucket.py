"""Bitbucket OAuth2 provider implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar_oauth.base import BaseOAuthProvider

if TYPE_CHECKING:
    from litestar_oauth.types import OAuthUserInfo


class BitbucketOAuthProvider(BaseOAuthProvider):
    """Bitbucket OAuth2 provider.

    Implements OAuth2 authentication flow for Bitbucket.

    Default scopes:
        - account: Access user account information
        - email: Access user email addresses

    User Info Mapping:
        - oauth_id: Bitbucket user UUID (curly braces removed)
        - email: Primary email address (fetched from emails endpoint)
        - email_verified: Email verification status
        - username: Bitbucket username
        - first_name: Extracted from display_name field (first word)
        - last_name: Extracted from display_name field (remaining words)
        - avatar_url: Bitbucket avatar URL from links
        - profile_url: Bitbucket profile URL from links

    Args:
        client_id: Bitbucket OAuth consumer key.
        client_secret: Bitbucket OAuth consumer secret.
        scope: Optional custom scopes. Defaults to ["account", "email"].
    """

    @property
    def provider_name(self) -> str:
        """Return provider identifier.

        Returns:
            Provider name 'bitbucket'.
        """
        return "bitbucket"

    @property
    def authorize_url(self) -> str:
        """Return Bitbucket authorization endpoint.

        Returns:
            Bitbucket OAuth authorization URL.
        """
        return "https://bitbucket.org/site/oauth2/authorize"

    @property
    def token_url(self) -> str:
        """Return Bitbucket token exchange endpoint.

        Returns:
            Bitbucket OAuth token URL.
        """
        return "https://bitbucket.org/site/oauth2/access_token"

    @property
    def user_info_url(self) -> str:
        """Return Bitbucket user info endpoint.

        Returns:
            Bitbucket API user endpoint URL.
        """
        return "https://api.bitbucket.org/2.0/user"

    def _default_scope(self) -> list[str]:
        """Return default scopes for Bitbucket OAuth.

        Returns:
            List of default OAuth scopes.
        """
        return ["account", "email"]

    async def get_user_info(
        self,
        access_token: str,
        **kwargs: Any,
    ) -> OAuthUserInfo:
        """Fetch and normalize Bitbucket user information.

        Retrieves user profile from Bitbucket API and normalizes it to OAuthUserInfo format.
        Makes an additional API call to fetch email information from the emails endpoint.

        Args:
            access_token: Bitbucket OAuth access token.
            **kwargs: Additional parameters (unused).

        Returns:
            Normalized user information.

        Raises:
            ImportError: If httpx is not installed.
            Exception: If user info fetch fails.
        """
        try:
            import httpx
        except ImportError as e:
            msg = "httpx is required for Bitbucket OAuth. Install it with: pip install httpx"
            raise ImportError(msg) from e

        from litestar_oauth.types import OAuthUserInfo

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            # Fetch user profile
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()

            # Fetch email from emails endpoint
            email_response = await client.get(
                "https://api.bitbucket.org/2.0/user/emails",
                headers=headers,
            )
            email_response.raise_for_status()
            emails_data = email_response.json()

        # Extract email information
        email = ""
        email_verified = False

        if emails_data and "values" in emails_data:
            emails = emails_data["values"]

            # Find primary email
            for email_data in emails:
                if email_data.get("is_primary"):
                    email = email_data.get("email", "")
                    email_verified = email_data.get("is_confirmed", False)
                    break

            # Fallback to first confirmed email
            if not email:
                for email_data in emails:
                    if email_data.get("is_confirmed"):
                        email = email_data.get("email", "")
                        email_verified = True
                        break

            # Last resort: first email
            if not email and emails:
                email = emails[0].get("email", "")
                email_verified = emails[0].get("is_confirmed", False)

        # Parse display_name into first and last name
        display_name = user_data.get("display_name", "")
        first_name = ""
        last_name = ""

        if display_name:
            name_parts = display_name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Extract avatar URL from links
        avatar_url = ""
        links = user_data.get("links", {})
        if "avatar" in links and "href" in links["avatar"]:
            avatar_url = links["avatar"]["href"]

        # Extract profile URL from links
        profile_url = ""
        if "html" in links and "href" in links["html"]:
            profile_url = links["html"]["href"]

        # Clean up UUID by removing curly braces if present
        oauth_id = user_data.get("uuid", "")
        oauth_id = oauth_id.strip("{}") if oauth_id else ""

        return OAuthUserInfo(
            provider=self.provider_name,
            oauth_id=oauth_id,
            email=email,
            email_verified=email_verified,
            username=user_data.get("username", ""),
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            profile_url=profile_url,
            raw_data=user_data,
        )
