# @oagen-ignore-file
# This file is hand-maintained. The passwordless API endpoints are not yet in
# the OpenAPI spec, so this module provides the functionality until they are.

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional

if TYPE_CHECKING:
    from ._client import AsyncWorkOSClient, WorkOSClient

PasswordlessSessionType = Literal["MagicLink"]


@dataclass(slots=True)
class PasswordlessSession:
    """Representation of a WorkOS Passwordless Session Response."""

    object: Literal["passwordless_session"]
    id: str
    email: str
    expires_at: str
    link: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PasswordlessSession":
        return cls(
            object=data.get("object", "passwordless_session"),
            id=data["id"],
            email=data["email"],
            expires_at=data["expires_at"],
            link=data["link"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object": self.object,
            "id": self.id,
            "email": self.email,
            "expires_at": self.expires_at,
            "link": self.link,
        }


class Passwordless:
    """Offers methods through the WorkOS Passwordless service."""

    def __init__(self, client: "WorkOSClient") -> None:
        self._client = client

    def create_session(
        self,
        *,
        email: str,
        type: PasswordlessSessionType,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> PasswordlessSession:
        """Create a Passwordless Session.

        Args:
            email: The email of the user to authenticate.
            type: The type of Passwordless Session ('MagicLink').
            redirect_uri: The redirect endpoint for the callback from WorkOS. (Optional)
            state: Arbitrary state to pass through the redirect. (Optional)
            expires_in: Seconds until expiry (900–86400). (Optional)

        Returns:
            PasswordlessSession
        """
        body: Dict[str, Any] = {
            k: v
            for k, v in {
                "email": email,
                "type": type,
                "redirect_uri": redirect_uri,
                "state": state,
                "expires_in": expires_in,
            }.items()
            if v is not None
        }

        response = self._client.request(
            method="post",
            path=("passwordless", "sessions"),
            body=body,
            model=PasswordlessSession,
        )
        return response

    def send_session(self, session_id: str) -> Literal[True]:
        """Send a Passwordless Session via email.

        Args:
            session_id: The unique identifier of the Passwordless Session.

        Returns:
            True on success.
        """
        self._client.request(
            method="post",
            path=("passwordless", "sessions", str(session_id), "send"),
        )
        return True


class AsyncPasswordless:
    """Async variant of the WorkOS Passwordless service."""

    def __init__(self, client: "AsyncWorkOSClient") -> None:
        self._client = client

    async def create_session(
        self,
        *,
        email: str,
        type: PasswordlessSessionType,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> PasswordlessSession:
        """Create a Passwordless Session.

        Args:
            email: The email of the user to authenticate.
            type: The type of Passwordless Session ('MagicLink').
            redirect_uri: The redirect endpoint for the callback from WorkOS. (Optional)
            state: Arbitrary state to pass through the redirect. (Optional)
            expires_in: Seconds until expiry (900–86400). (Optional)

        Returns:
            PasswordlessSession
        """
        body: Dict[str, Any] = {
            k: v
            for k, v in {
                "email": email,
                "type": type,
                "redirect_uri": redirect_uri,
                "state": state,
                "expires_in": expires_in,
            }.items()
            if v is not None
        }

        response = await self._client.request(
            method="post",
            path=("passwordless", "sessions"),
            body=body,
            model=PasswordlessSession,
        )
        return response

    async def send_session(self, session_id: str) -> Literal[True]:
        """Send a Passwordless Session via email.

        Args:
            session_id: The unique identifier of the Passwordless Session.

        Returns:
            True on success.
        """
        await self._client.request(
            method="post",
            path=("passwordless", "sessions", str(session_id), "send"),
        )
        return True
