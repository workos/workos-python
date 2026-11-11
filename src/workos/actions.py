# @oagen-ignore-file
# This file is hand-maintained. AuthKit Actions helpers for request
# verification, typed deserialization, and response signing. Actions requests
# are sent by WorkOS to the customer's endpoint and are not described by the
# OpenAPI spec, so both the crypto and the payload models live here.
#
# The payload models mirror the Actions payload contract enforced by the
# WorkOS API. Fields that contract guarantees are required; fields WorkOS adds
# on a real sign-in (for example `user.external_id`) are optional, because a
# test request sent from the dashboard omits them. The generated REST models
# (`User`, `Organization`, `OrganizationMembership`, `Invitation`) are not
# reused on purpose: an Action payload carries a trimmed organization
# membership (no `roles`) and a trimmed invitation (no `token`), and their
# strict `from_dict` would reject every real request.

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Literal, Optional, Union, cast

from ._types import _parse_datetime, _raise_deserialize_error
from .common.models.authenticate_response_authentication_method import (
    AuthenticateResponseAuthenticationMethod,
)
from .common.models.invitation_state import InvitationState
from .common.models.organization_domain_state import OrganizationDomainState
from .common.models.organization_domain_verification_strategy import (
    OrganizationDomainVerificationStrategy,
)
from .common.models.organization_membership_status import (
    OrganizationMembershipStatus,
)
from .common.models.slim_role import SlimRole

__all__ = [
    "DEFAULT_TOLERANCE",
    "ActionType",
    "ActionContext",
    "ActionInvitation",
    "ActionOrganization",
    "ActionOrganizationDomain",
    "ActionOrganizationMembership",
    "ActionUser",
    "Actions",
    "AsyncActions",
    "AuthenticationActionContext",
    "UserData",
    "UserRegistrationActionContext",
]

DEFAULT_TOLERANCE = 30  # seconds (stricter than webhooks' 180s)

ActionType = Literal["authentication", "user_registration"]

_ACTION_TYPE_TO_RESPONSE_OBJECT = {
    "authentication": "authentication_action_response",
    "user_registration": "user_registration_action_response",
}


# ---------------------------------------------------------------------------
# Payload models
# ---------------------------------------------------------------------------


def _optional_datetime(value: Any) -> datetime | None:
    return _parse_datetime(value) if value is not None else None


@dataclass(slots=True)
class ActionUser:
    """The user signing in, as sent in an Authentication Action request.

    Mirrors the REST ``User`` object. Fields WorkOS adds on a real sign-in
    (``name``, ``external_id``, ``last_sign_in_at``, ``locale``, ``metadata``)
    are ``None`` when the request omits them, as a dashboard test request does.
    """

    object: Literal["user"]
    id: str
    email: str
    email_verified: bool
    first_name: str | None
    last_name: str | None
    profile_picture_url: str | None
    created_at: datetime
    updated_at: datetime
    name: str | None = None
    external_id: str | None = None
    last_sign_in_at: datetime | None = None
    locale: str | None = None
    metadata: dict[str, str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionUser:
        """Deserialize from a dictionary."""
        try:
            return cls(
                object=data.get("object", "user"),
                id=data["id"],
                email=data["email"],
                email_verified=data["email_verified"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                profile_picture_url=data["profile_picture_url"],
                created_at=_parse_datetime(data["created_at"]),
                updated_at=_parse_datetime(data["updated_at"]),
                name=data.get("name"),
                external_id=data.get("external_id"),
                last_sign_in_at=_optional_datetime(data.get("last_sign_in_at")),
                locale=data.get("locale"),
                metadata=data.get("metadata"),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("ActionUser", e)


@dataclass(slots=True)
class ActionOrganizationDomain:
    """A domain of the organization in an Authentication Action request."""

    object: Literal["organization_domain"]
    id: str
    organization_id: str
    domain: str
    state: OrganizationDomainState | None = None
    verification_strategy: OrganizationDomainVerificationStrategy | None = None
    verification_token: str | None = None
    verification_prefix: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionOrganizationDomain:
        """Deserialize from a dictionary."""
        try:
            state = data.get("state")
            strategy = data.get("verification_strategy")
            return cls(
                object=data.get("object", "organization_domain"),
                id=data["id"],
                organization_id=data["organization_id"],
                domain=data["domain"],
                state=OrganizationDomainState(state) if state is not None else None,
                verification_strategy=OrganizationDomainVerificationStrategy(strategy)
                if strategy is not None
                else None,
                verification_token=data.get("verification_token"),
                verification_prefix=data.get("verification_prefix"),
                created_at=_optional_datetime(data.get("created_at")),
                updated_at=_optional_datetime(data.get("updated_at")),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("ActionOrganizationDomain", e)


@dataclass(slots=True)
class ActionOrganization:
    """The organization the user is signing in to, when there is one.

    Mirrors the REST ``Organization`` object. ``metadata`` and ``external_id``
    are present on a real sign-in and ``None`` on a dashboard test request.
    """

    object: Literal["organization"]
    id: str
    name: str
    domains: list[ActionOrganizationDomain]
    created_at: datetime
    updated_at: datetime
    allow_profiles_outside_organization: bool | None = None
    stripe_customer_id: str | None = None
    metadata: dict[str, str] | None = None
    external_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionOrganization:
        """Deserialize from a dictionary."""
        try:
            return cls(
                object=data.get("object", "organization"),
                id=data["id"],
                name=data["name"],
                domains=[
                    ActionOrganizationDomain.from_dict(cast(dict[str, Any], item))
                    for item in cast(list[Any], data["domains"])
                ],
                created_at=_parse_datetime(data["created_at"]),
                updated_at=_parse_datetime(data["updated_at"]),
                allow_profiles_outside_organization=data.get(
                    "allow_profiles_outside_organization"
                ),
                stripe_customer_id=data.get("stripe_customer_id"),
                metadata=data.get("metadata"),
                external_id=data.get("external_id"),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("ActionOrganization", e)


@dataclass(slots=True)
class ActionOrganizationMembership:
    """The user's membership in the organization, when there is one.

    This is a trimmed form of the REST ``OrganizationMembership`` object: it
    carries the primary ``role`` but not the ``roles`` list. ``directory_managed``,
    ``custom_attributes`` and ``user`` are present on a real sign-in and ``None``
    on a dashboard test request.
    """

    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    role: SlimRole
    status: OrganizationMembershipStatus
    created_at: datetime
    updated_at: datetime
    directory_managed: bool | None = None
    custom_attributes: dict[str, Any] | None = None
    user: ActionUser | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionOrganizationMembership:
        """Deserialize from a dictionary."""
        try:
            user = data.get("user")
            return cls(
                object=data.get("object", "organization_membership"),
                id=data["id"],
                user_id=data["user_id"],
                organization_id=data["organization_id"],
                role=SlimRole.from_dict(cast(dict[str, Any], data["role"])),
                status=OrganizationMembershipStatus(data["status"]),
                created_at=_parse_datetime(data["created_at"]),
                updated_at=_parse_datetime(data["updated_at"]),
                directory_managed=data.get("directory_managed"),
                custom_attributes=data.get("custom_attributes"),
                user=ActionUser.from_dict(cast(dict[str, Any], user))
                if user is not None
                else None,
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("ActionOrganizationMembership", e)


@dataclass(slots=True)
class UserData:
    """The details a prospective user submitted at sign-up.

    Sent in a User Registration Action request; no user exists yet.
    """

    object: Literal["user_data"]
    email: str
    first_name: str | None
    last_name: str | None
    extra_attributes: dict[str, str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserData:
        """Deserialize from a dictionary."""
        try:
            return cls(
                object=data.get("object", "user_data"),
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                extra_attributes=data.get("extra_attributes"),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("UserData", e)


@dataclass(slots=True)
class ActionInvitation:
    """The invitation the prospective user is accepting, when there is one.

    This is a trimmed form of the REST ``Invitation`` object: it has no
    ``token``, ``accept_invitation_url``, ``accepted_user_id`` or ``role_slug``.
    """

    object: Literal["invitation"]
    id: str
    email: str
    state: InvitationState
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    accepted_at: datetime | None = None
    revoked_at: datetime | None = None
    organization_id: str | None = None
    inviter_user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionInvitation:
        """Deserialize from a dictionary."""
        try:
            return cls(
                object=data.get("object", "invitation"),
                id=data["id"],
                email=data["email"],
                state=InvitationState(data["state"]),
                expires_at=_parse_datetime(data["expires_at"]),
                created_at=_parse_datetime(data["created_at"]),
                updated_at=_parse_datetime(data["updated_at"]),
                accepted_at=_optional_datetime(data.get("accepted_at")),
                revoked_at=_optional_datetime(data.get("revoked_at")),
                organization_id=data.get("organization_id"),
                inviter_user_id=data.get("inviter_user_id"),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("ActionInvitation", e)


@dataclass(slots=True)
class AuthenticationActionContext:
    """An Authentication Action request: a user is about to sign in.

    ``id`` is the action execution ID, which also appears in the
    ``action.authentication_denied`` event and the dashboard's Actions log.
    """

    object: Literal["authentication_action_context"]
    id: str
    user: ActionUser
    authentication_method: AuthenticateResponseAuthenticationMethod
    organization: ActionOrganization | None = None
    organization_membership: ActionOrganizationMembership | None = None
    issuer: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    device_fingerprint: str | None = None
    client_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthenticationActionContext:
        """Deserialize from a dictionary."""
        try:
            organization = data.get("organization")
            membership = data.get("organization_membership")
            return cls(
                object=data.get("object", "authentication_action_context"),
                id=data["id"],
                user=ActionUser.from_dict(cast(dict[str, Any], data["user"])),
                authentication_method=AuthenticateResponseAuthenticationMethod(
                    data["authentication_method"]
                ),
                organization=ActionOrganization.from_dict(
                    cast(dict[str, Any], organization)
                )
                if organization is not None
                else None,
                organization_membership=ActionOrganizationMembership.from_dict(
                    cast(dict[str, Any], membership)
                )
                if membership is not None
                else None,
                issuer=data.get("issuer"),
                ip_address=data.get("ip_address"),
                user_agent=data.get("user_agent"),
                device_fingerprint=data.get("device_fingerprint"),
                client_id=data.get("client_id"),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("AuthenticationActionContext", e)


@dataclass(slots=True)
class UserRegistrationActionContext:
    """A User Registration Action request: someone is about to sign up.

    ``id`` is the action execution ID, which also appears in the
    ``action.user_registration_denied`` event and the dashboard's Actions log.
    """

    object: Literal["user_registration_action_context"]
    id: str
    user_data: UserData
    authentication_method: AuthenticateResponseAuthenticationMethod
    invitation: ActionInvitation | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    device_fingerprint: str | None = None
    client_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserRegistrationActionContext:
        """Deserialize from a dictionary."""
        try:
            invitation = data.get("invitation")
            return cls(
                object=data.get("object", "user_registration_action_context"),
                id=data["id"],
                user_data=UserData.from_dict(cast(dict[str, Any], data["user_data"])),
                authentication_method=AuthenticateResponseAuthenticationMethod(
                    data["authentication_method"]
                ),
                invitation=ActionInvitation.from_dict(cast(dict[str, Any], invitation))
                if invitation is not None
                else None,
                ip_address=data.get("ip_address"),
                user_agent=data.get("user_agent"),
                device_fingerprint=data.get("device_fingerprint"),
                client_id=data.get("client_id"),
            )
        except (KeyError, TypeError, ValueError) as e:
            _raise_deserialize_error("UserRegistrationActionContext", e)


ActionContext = Union[AuthenticationActionContext, UserRegistrationActionContext]
"""A verified Actions request, narrowed by ``isinstance`` on its ``object``."""


def _deserialize_action_context(data: dict[str, Any]) -> ActionContext:
    object_type = data.get("object")
    if object_type == "authentication_action_context":
        return AuthenticationActionContext.from_dict(data)
    if object_type == "user_registration_action_context":
        return UserRegistrationActionContext.from_dict(data)
    _raise_deserialize_error(
        "ActionContext",
        ValueError(f"Unknown action context object {object_type!r}"),
    )


# ---------------------------------------------------------------------------
# Signature helpers
# ---------------------------------------------------------------------------


def _verify_signature(
    *,
    payload: Union[bytes, str],
    sig_header: str,
    secret: str,
    tolerance: int = DEFAULT_TOLERANCE,
) -> None:
    """Verify an HMAC-SHA256 signature header. Raises ValueError on failure."""
    try:
        issued_part, sig_part = sig_header.split(", ", 1)
    except (ValueError, AttributeError) as exc:
        raise ValueError(
            "Unable to extract timestamp and signature hash from header",
            sig_header,
        ) from exc

    issued_timestamp = issued_part[2:]
    signature_hash = sig_part[3:]

    current_time = time.time()
    timestamp_in_seconds = int(issued_timestamp) / 1000
    seconds_since_issued = current_time - timestamp_in_seconds

    if abs(seconds_since_issued) > tolerance:
        raise ValueError("Timestamp outside the tolerance zone")

    body_str = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    unhashed_string = f"{issued_timestamp}.{body_str}"
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        unhashed_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature_hash, expected_signature):
        raise ValueError(
            "Signature hash does not match the expected signature hash for payload"
        )


def _compute_signature(payload_str: str, secret: str) -> str:
    """Compute HMAC-SHA256 hex digest for a signed payload string."""
    return hmac.new(
        secret.encode("utf-8"),
        payload_str.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def _load_verified_payload(
    *,
    payload: Union[bytes, str],
    sig_header: str,
    secret: str,
    tolerance: int,
) -> Dict[str, Any]:
    """Verify the signature, then parse the body as a JSON object."""
    _verify_signature(
        payload=payload,
        sig_header=sig_header,
        secret=secret,
        tolerance=tolerance,
    )
    body = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    data = json.loads(body)
    if not isinstance(data, dict):
        _raise_deserialize_error(
            "ActionContext", ValueError("Actions payload must be a JSON object")
        )
    return cast(Dict[str, Any], data)


def _build_signed_response(
    *,
    action_type: ActionType,
    verdict: Literal["Allow", "Deny"],
    error_message: Optional[str],
    secret: str,
) -> Dict[str, Any]:
    timestamp = int(time.time() * 1000)
    response_payload: Dict[str, Any] = {
        "timestamp": timestamp,
        "verdict": verdict,
    }
    if error_message is not None:
        response_payload["error_message"] = error_message

    payload_json = json.dumps(response_payload, separators=(",", ":"))
    signed_payload = f"{timestamp}.{payload_json}"
    signature = _compute_signature(signed_payload, secret)
    object_type = _ACTION_TYPE_TO_RESPONSE_OBJECT[action_type]

    return {
        "object": object_type,
        "payload": response_payload,
        "signature": signature,
    }


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


class Actions:
    """AuthKit Actions request verification and response signing.

    These helpers are local and synchronous; they make no HTTP calls.
    """

    def verify_header(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> None:
        """Verify the signature of an Actions request.

        Args:
            payload: The raw request body (bytes or str), never a re-serialized dict.
            sig_header: The value of the ``WorkOS-Signature`` request header.
            secret: The Actions signing secret from the WorkOS dashboard.
            tolerance: Maximum age of the request in seconds. Defaults to 30.

        Raises:
            ValueError: If the signature is invalid or the timestamp is stale.
        """
        _verify_signature(
            payload=payload,
            sig_header=sig_header,
            secret=secret,
            tolerance=tolerance,
        )

    def verify_action(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> ActionContext:
        """Verify an Actions request and deserialize it into a typed context.

        Returns an :class:`AuthenticationActionContext` for a sign-in or a
        :class:`UserRegistrationActionContext` for a sign-up; narrow with
        ``isinstance``. Use :meth:`construct_action` for the raw payload instead.

        Args:
            payload: The raw request body (bytes or str), never a re-serialized dict.
            sig_header: The value of the ``WorkOS-Signature`` request header.
            secret: The Actions signing secret from the WorkOS dashboard.
            tolerance: Maximum age of the request in seconds. Defaults to 30.

        Raises:
            ValueError: If the signature is invalid or the timestamp is stale.
            WorkOSError: If the payload is not a recognized Actions request.
        """
        data = _load_verified_payload(
            payload=payload,
            sig_header=sig_header,
            secret=secret,
            tolerance=tolerance,
        )
        return _deserialize_action_context(data)

    def construct_action(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> Dict[str, Any]:
        """Verify an Actions request and return its payload as a plain dict.

        Prefer :meth:`verify_action`, which returns a typed context.

        Raises:
            ValueError: If the signature is invalid or the timestamp is stale.
            WorkOSError: If the payload is not a JSON object.
        """
        return _load_verified_payload(
            payload=payload,
            sig_header=sig_header,
            secret=secret,
            tolerance=tolerance,
        )

    def sign_response(
        self,
        *,
        action_type: ActionType,
        verdict: Literal["Allow", "Deny"],
        error_message: Optional[str] = None,
        secret: str,
    ) -> Dict[str, Any]:
        """Build and sign an Actions response.

        Returns the JSON-serializable body to respond with, including the
        ``object``, ``payload`` and ``signature`` fields WorkOS expects.
        """
        return _build_signed_response(
            action_type=action_type,
            verdict=verdict,
            error_message=error_message,
            secret=secret,
        )


class AsyncActions(Actions):
    """AuthKit Actions helpers on the async client.

    Verification and signing are local computations, so the methods are the
    same synchronous ones as :class:`Actions`.
    """
