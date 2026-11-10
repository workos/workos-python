import copy
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Any

import pytest
from workos import WorkOSError
from workos.actions import (
    ActionInvitation,
    ActionOrganization,
    ActionOrganizationDomain,
    ActionOrganizationMembership,
    Actions,
    ActionUser,
    AsyncActions,
    AuthenticationActionContext,
    UserData,
    UserRegistrationActionContext,
)
from workos.common.models.authenticate_response_authentication_method import (
    AuthenticateResponseAuthenticationMethod,
)
from workos.common.models.invitation_state import InvitationState
from workos.common.models.organization_domain_state import OrganizationDomainState
from workos.common.models.organization_membership_status import (
    OrganizationMembershipStatus,
)

SECRET = "test_secret_key"
TIMESTAMP = "2024-10-22T17:12:50.746Z"
PARSED_TIMESTAMP = datetime(2024, 10, 22, 17, 12, 50, 746000, tzinfo=timezone.utc)


def _make_sig_header(body: str, secret: str, timestamp_ms: int = 0) -> str:
    if timestamp_ms == 0:
        timestamp_ms = int(time.time() * 1000)
    ts = str(timestamp_ms)
    unhashed = f"{ts}.{body}"
    sig = hmac.new(
        secret.encode("utf-8"),
        unhashed.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"t={ts}, v1={sig}"


def _sign(payload: dict[str, Any], secret: str = SECRET) -> tuple[str, str]:
    """Serialize a payload and sign it the way WorkOS does."""
    body = json.dumps(payload)
    return body, _make_sig_header(body, secret)


USER: dict[str, Any] = {
    "object": "user",
    "id": "user_01JATCHZVEC5EPANDPEZVM68Y9",
    "email": "jane@foocorp.com",
    "email_verified": True,
    "first_name": "Jane",
    "last_name": "Doe",
    "name": "Jane Doe",
    "profile_picture_url": "https://example.com/jane.jpg",
    "last_sign_in_at": TIMESTAMP,
    "locale": "en-US",
    "created_at": TIMESTAMP,
    "updated_at": TIMESTAMP,
    "external_id": "ext_123",
}

# What the API sends for a real sign-in: the full REST user and organization,
# plus the context-specific organization membership (primary role, no roles list).
AUTHENTICATION_PAYLOAD: dict[str, Any] = {
    "object": "authentication_action_context",
    "id": "actions_execution_01JATCMZJY26PQ59XT9BNT0FNN",
    "issuer": "https://api.workos.com",
    "user": USER,
    "organization": {
        "object": "organization",
        "id": "org_01JATCMZJY26PQ59XT9BNT0FNN",
        "name": "Foo Corp",
        "allow_profiles_outside_organization": False,
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "domains": [
            {
                "object": "organization_domain",
                "id": "org_domain_01JATCNVYCHT1SZGENR4QTXKRM",
                "organization_id": "org_01JATCMZJY26PQ59XT9BNT0FNN",
                "domain": "foocorp.com",
                "state": "verified",
                "verification_strategy": "dns",
                "verification_token": "tok_123",
                "created_at": TIMESTAMP,
                "updated_at": TIMESTAMP,
            }
        ],
        "metadata": {"tier": "enterprise"},
        "stripe_customer_id": "cus_123",
        "external_id": None,
    },
    "organization_membership": {
        "object": "organization_membership",
        "id": "om_01JATCNVYCHT1SZGENR4QTXKRK",
        "organization_id": "org_01JATCMZJY26PQ59XT9BNT0FNN",
        "user_id": "user_01JATCHZVEC5EPANDPEZVM68Y9",
        "status": "active",
        "directory_managed": False,
        "custom_attributes": {"department": "engineering"},
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "role": {"slug": "member"},
        "user": USER,
    },
    "ip_address": "50.141.123.10",
    "user_agent": "Mozilla/5.0",
    "device_fingerprint": "notafingerprint",
    "authentication_method": "Password",
    "client_id": "client_01JATCNVYCHT1SZGENR4QTXKRK",
}

# What the dashboard's "send test request" sends: the API strips it down to the
# fields the actions-types contract guarantees, so the REST extras are absent.
AUTHENTICATION_TEST_PAYLOAD: dict[str, Any] = {
    "object": "authentication_action_context",
    "id": "actions_execution_01JATCMZJY26PQ59XT9BNT0FNM",
    "issuer": "test",
    "user": {
        "object": "user",
        "id": "user_01JATCHZVEC5EPANDPEZVM68Y9",
        "email": "jane@foocorp.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "email_verified": True,
        "profile_picture_url": "https://example.com/jane.jpg",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    },
    "organization": {
        "object": "organization",
        "id": "org_01JATCMZJY26PQ59XT9BNT0FNN",
        "name": "Foo Corp",
        "allow_profiles_outside_organization": False,
        "domains": [],
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    },
    "organization_membership": {
        "object": "organization_membership",
        "id": "om_01JATCNVYCHT1SZGENR4QTXKRK",
        "user_id": "user_01JATCHZVEC5EPANDPEZVM68Y9",
        "organization_id": "org_01JATCMZJY26PQ59XT9BNT0FNN",
        "role": {"slug": "member"},
        "status": "active",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    },
    "ip_address": "50.141.123.10",
    "user_agent": "Mozilla/5.0",
    "authentication_method": "Password",
}

USER_REGISTRATION_PAYLOAD: dict[str, Any] = {
    "object": "user_registration_action_context",
    "id": "actions_execution_01JATCMZJY26PQ59XT9BNT0FNP",
    "user_data": {
        "object": "user_data",
        "email": "jane@foocorp.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "extra_attributes": {"company_size": "50"},
    },
    "invitation": {
        "object": "invitation",
        "id": "invitation_01JBVZWH8HJ855YZ5BWHG1WNZN",
        "email": "jane@foocorp.com",
        "inviter_user_id": "user_01JBVZWAEPWAE3YYKBVT0AF81F",
        "organization_id": "org_01JBW46BTKAA98WZN8826XQ2YP",
        "state": "accepted",
        "accepted_at": "2024-10-22T17:13:50.746Z",
        "revoked_at": None,
        "expires_at": TIMESTAMP,
        "created_at": "2024-10-21T17:12:50.746Z",
        "updated_at": "2024-10-21T17:12:50.746Z",
    },
    "ip_address": "50.141.123.10",
    "user_agent": "Mozilla/5.0",
    "device_fingerprint": "notafingerprint",
    "authentication_method": "GoogleOAuth",
    "client_id": "client_01JATCNVYCHT1SZGENR4QTXKRK",
}

# A direct sign-up with no invitation and no names.
USER_REGISTRATION_PAYLOAD_MINIMAL: dict[str, Any] = {
    "object": "user_registration_action_context",
    "id": "actions_execution_01JATCMZJY26PQ59XT9BNT0FNQ",
    "user_data": {
        "object": "user_data",
        "email": "sam@example.com",
        "first_name": None,
        "last_name": None,
    },
    "authentication_method": "MagicAuth",
    "client_id": "client_01JATCNVYCHT1SZGENR4QTXKRK",
}


class TestActionsVerifyHeader:
    def setup_method(self):
        self.actions = Actions()

    def test_verify_header_valid(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        self.actions.verify_header(payload=body, sig_header=sig, secret=SECRET)

    def test_verify_header_invalid_signature(self):
        _, sig = _sign(AUTHENTICATION_PAYLOAD)
        with pytest.raises(ValueError, match="does not match"):
            self.actions.verify_header(
                payload='{"tampered": true}', sig_header=sig, secret=SECRET
            )

    def test_verify_header_stale_timestamp(self):
        body = json.dumps(AUTHENTICATION_PAYLOAD)
        old_ts = int((time.time() - 60) * 1000)
        sig = _make_sig_header(body, SECRET, old_ts)
        with pytest.raises(ValueError, match="tolerance zone"):
            self.actions.verify_header(
                payload=body, sig_header=sig, secret=SECRET, tolerance=30
            )

    def test_verify_header_future_timestamp(self):
        body = json.dumps(AUTHENTICATION_PAYLOAD)
        future_ts = int((time.time() + 60) * 1000)
        sig = _make_sig_header(body, SECRET, future_ts)
        with pytest.raises(ValueError, match="tolerance zone"):
            self.actions.verify_header(
                payload=body, sig_header=sig, secret=SECRET, tolerance=30
            )

    def test_verify_header_custom_tolerance(self):
        body = json.dumps(AUTHENTICATION_PAYLOAD)
        old_ts = int((time.time() - 10) * 1000)
        sig = _make_sig_header(body, SECRET, old_ts)
        self.actions.verify_header(
            payload=body, sig_header=sig, secret=SECRET, tolerance=60
        )

    def test_verify_header_malformed_header(self):
        body = json.dumps(AUTHENTICATION_PAYLOAD)
        with pytest.raises(ValueError, match="Unable to extract"):
            self.actions.verify_header(
                payload=body, sig_header="invalid-header", secret=SECRET
            )

    def test_verify_header_bytes_payload(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        self.actions.verify_header(
            payload=body.encode("utf-8"), sig_header=sig, secret=SECRET
        )


class TestActionsVerifyAction:
    def setup_method(self):
        self.actions = Actions()

    def test_authentication_action_is_fully_typed(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, AuthenticationActionContext)
        assert action.object == "authentication_action_context"
        assert action.id == "actions_execution_01JATCMZJY26PQ59XT9BNT0FNN"
        assert action.issuer == "https://api.workos.com"
        assert action.ip_address == "50.141.123.10"
        assert action.user_agent == "Mozilla/5.0"
        assert action.device_fingerprint == "notafingerprint"
        assert action.client_id == "client_01JATCNVYCHT1SZGENR4QTXKRK"
        assert (
            action.authentication_method
            is AuthenticateResponseAuthenticationMethod.PASSWORD
        )

        assert isinstance(action.user, ActionUser)
        assert action.user.id == "user_01JATCHZVEC5EPANDPEZVM68Y9"
        assert action.user.email == "jane@foocorp.com"
        assert action.user.email_verified is True
        assert action.user.name == "Jane Doe"
        assert action.user.external_id == "ext_123"
        assert action.user.locale == "en-US"
        assert action.user.last_sign_in_at == PARSED_TIMESTAMP
        assert action.user.created_at == PARSED_TIMESTAMP

        assert isinstance(action.organization, ActionOrganization)
        assert action.organization.id == "org_01JATCMZJY26PQ59XT9BNT0FNN"
        assert action.organization.name == "Foo Corp"
        assert action.organization.metadata == {"tier": "enterprise"}
        assert action.organization.stripe_customer_id == "cus_123"
        assert action.organization.external_id is None
        assert action.organization.allow_profiles_outside_organization is False
        assert len(action.organization.domains) == 1
        domain = action.organization.domains[0]
        assert isinstance(domain, ActionOrganizationDomain)
        assert domain.domain == "foocorp.com"
        assert domain.state is OrganizationDomainState.VERIFIED
        assert domain.verification_token == "tok_123"
        assert domain.created_at == PARSED_TIMESTAMP

        membership = action.organization_membership
        assert isinstance(membership, ActionOrganizationMembership)
        assert membership.id == "om_01JATCNVYCHT1SZGENR4QTXKRK"
        assert membership.role.slug == "member"
        assert membership.status is OrganizationMembershipStatus.ACTIVE
        assert membership.directory_managed is False
        assert membership.custom_attributes == {"department": "engineering"}
        assert isinstance(membership.user, ActionUser)
        assert membership.user.id == action.user.id

    def test_authentication_action_accepts_dashboard_test_request(self):
        body, sig = _sign(AUTHENTICATION_TEST_PAYLOAD)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, AuthenticationActionContext)
        assert action.issuer == "test"
        assert action.device_fingerprint is None
        assert action.client_id is None
        assert action.user.first_name == "Jane"
        assert action.user.name is None
        assert action.user.external_id is None
        assert action.user.last_sign_in_at is None
        assert action.user.locale is None
        assert action.user.metadata is None
        assert isinstance(action.organization, ActionOrganization)
        assert action.organization.domains == []
        assert action.organization.metadata is None
        assert action.organization.external_id is None
        assert isinstance(action.organization_membership, ActionOrganizationMembership)
        assert action.organization_membership.directory_managed is None
        assert action.organization_membership.custom_attributes is None
        assert action.organization_membership.user is None

    def test_authentication_action_without_organization(self):
        payload = copy.deepcopy(AUTHENTICATION_PAYLOAD)
        del payload["organization"]
        del payload["organization_membership"]
        body, sig = _sign(payload)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, AuthenticationActionContext)
        assert action.organization is None
        assert action.organization_membership is None

    def test_user_registration_action_is_fully_typed(self):
        body, sig = _sign(USER_REGISTRATION_PAYLOAD)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, UserRegistrationActionContext)
        assert action.object == "user_registration_action_context"
        assert action.id == "actions_execution_01JATCMZJY26PQ59XT9BNT0FNP"
        assert (
            action.authentication_method
            is AuthenticateResponseAuthenticationMethod.GOOGLE_OAUTH
        )
        assert action.ip_address == "50.141.123.10"
        assert action.client_id == "client_01JATCNVYCHT1SZGENR4QTXKRK"

        assert isinstance(action.user_data, UserData)
        assert action.user_data.email == "jane@foocorp.com"
        assert action.user_data.first_name == "Jane"
        assert action.user_data.last_name == "Doe"
        assert action.user_data.extra_attributes == {"company_size": "50"}

        assert isinstance(action.invitation, ActionInvitation)
        assert action.invitation.id == "invitation_01JBVZWH8HJ855YZ5BWHG1WNZN"
        assert action.invitation.state is InvitationState.ACCEPTED
        assert action.invitation.organization_id == "org_01JBW46BTKAA98WZN8826XQ2YP"
        assert action.invitation.inviter_user_id == "user_01JBVZWAEPWAE3YYKBVT0AF81F"
        assert action.invitation.accepted_at == datetime(
            2024, 10, 22, 17, 13, 50, 746000, tzinfo=timezone.utc
        )
        assert action.invitation.revoked_at is None
        assert action.invitation.expires_at == PARSED_TIMESTAMP

    def test_user_registration_action_without_invitation(self):
        body, sig = _sign(USER_REGISTRATION_PAYLOAD_MINIMAL)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, UserRegistrationActionContext)
        assert action.invitation is None
        assert action.ip_address is None
        assert action.user_agent is None
        assert action.device_fingerprint is None
        assert action.user_data.first_name is None
        assert action.user_data.last_name is None
        assert action.user_data.extra_attributes is None
        assert (
            action.authentication_method
            is AuthenticateResponseAuthenticationMethod.MAGIC_AUTH
        )

    def test_invitation_without_inviter_or_organization(self):
        payload = copy.deepcopy(USER_REGISTRATION_PAYLOAD)
        del payload["invitation"]["inviter_user_id"]
        del payload["invitation"]["organization_id"]
        body, sig = _sign(payload)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, UserRegistrationActionContext)
        assert isinstance(action.invitation, ActionInvitation)
        assert action.invitation.inviter_user_id is None
        assert action.invitation.organization_id is None

    def test_bytes_payload(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        action = self.actions.verify_action(
            payload=body.encode("utf-8"), sig_header=sig, secret=SECRET
        )
        assert isinstance(action, AuthenticationActionContext)

    def test_unknown_authentication_method_is_preserved(self):
        payload = copy.deepcopy(AUTHENTICATION_PAYLOAD)
        payload["authentication_method"] = "SomeFutureOAuth"
        body, sig = _sign(payload)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

        assert isinstance(action, AuthenticationActionContext)
        assert isinstance(
            action.authentication_method, AuthenticateResponseAuthenticationMethod
        )
        assert action.authentication_method.value == "SomeFutureOAuth"

    def test_invalid_signature_is_rejected_before_parsing(self):
        payload = copy.deepcopy(AUTHENTICATION_PAYLOAD)
        payload["object"] = "not_an_action"
        body, sig = _sign(payload, secret="wrong_secret")
        with pytest.raises(ValueError, match="does not match"):
            self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

    def test_unknown_object_raises_workos_error(self):
        payload = copy.deepcopy(AUTHENTICATION_PAYLOAD)
        payload["object"] = "mystery_action_context"
        body, sig = _sign(payload)
        with pytest.raises(WorkOSError, match="mystery_action_context"):
            self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

    def test_missing_required_field_raises_workos_error(self):
        payload = copy.deepcopy(AUTHENTICATION_PAYLOAD)
        del payload["user"]["email"]
        body, sig = _sign(payload)
        with pytest.raises(WorkOSError, match="ActionUser"):
            self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

    def test_non_object_payload_raises_workos_error(self):
        body = "[]"
        sig = _make_sig_header(body, SECRET)
        with pytest.raises(WorkOSError, match="JSON object"):
            self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)

    def test_via_client(self, workos: Any):
        body, sig = _sign(USER_REGISTRATION_PAYLOAD)
        action = workos.actions.verify_action(
            payload=body, sig_header=sig, secret=SECRET
        )
        assert isinstance(action, UserRegistrationActionContext)

    @pytest.mark.asyncio
    async def test_via_async_client(self, async_workos: Any):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        action = async_workos.actions.verify_action(
            payload=body, sig_header=sig, secret=SECRET
        )
        assert isinstance(action, AuthenticationActionContext)


class TestActionsConstructAction:
    def setup_method(self):
        self.actions = Actions()

    def test_construct_action_returns_raw_dict(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        result = self.actions.construct_action(
            payload=body, sig_header=sig, secret=SECRET
        )
        assert result == AUTHENTICATION_PAYLOAD
        assert result["user"]["id"] == "user_01JATCHZVEC5EPANDPEZVM68Y9"

    def test_construct_action_invalid_signature(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD, secret="wrong_secret")
        with pytest.raises(ValueError):
            self.actions.construct_action(payload=body, sig_header=sig, secret=SECRET)

    def test_construct_action_non_object_payload(self):
        body = "[]"
        sig = _make_sig_header(body, SECRET)
        with pytest.raises(WorkOSError, match="JSON object"):
            self.actions.construct_action(payload=body, sig_header=sig, secret=SECRET)


class TestActionsSignResponse:
    def setup_method(self):
        self.actions = Actions()

    def test_sign_response_authentication_allow(self):
        result = self.actions.sign_response(
            action_type="authentication", verdict="Allow", secret=SECRET
        )
        assert result["object"] == "authentication_action_response"
        assert result["payload"]["verdict"] == "Allow"
        assert "error_message" not in result["payload"]
        assert len(result["signature"]) == 64

    def test_sign_response_user_registration_deny(self):
        result = self.actions.sign_response(
            action_type="user_registration",
            verdict="Deny",
            error_message="Account suspended",
            secret=SECRET,
        )
        assert result["object"] == "user_registration_action_response"
        assert result["payload"]["verdict"] == "Deny"
        assert result["payload"]["error_message"] == "Account suspended"

    def test_sign_response_signature_is_verifiable(self):
        result = self.actions.sign_response(
            action_type="authentication", verdict="Allow", secret=SECRET
        )
        ts = result["payload"]["timestamp"]
        payload_json = json.dumps(result["payload"], separators=(",", ":"))
        signed_payload = f"{ts}.{payload_json}"
        expected = hmac.new(
            SECRET.encode("utf-8"),
            signed_payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        assert result["signature"] == expected


class TestAsyncActions:
    def setup_method(self):
        self.actions = AsyncActions()

    def test_verify_header_valid(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        self.actions.verify_header(payload=body, sig_header=sig, secret=SECRET)

    def test_verify_action_valid(self):
        body, sig = _sign(USER_REGISTRATION_PAYLOAD)
        action = self.actions.verify_action(payload=body, sig_header=sig, secret=SECRET)
        assert isinstance(action, UserRegistrationActionContext)
        assert action.user_data.email == "jane@foocorp.com"

    def test_construct_action_valid(self):
        body, sig = _sign(AUTHENTICATION_PAYLOAD)
        result = self.actions.construct_action(
            payload=body, sig_header=sig, secret=SECRET
        )
        assert result["object"] == "authentication_action_context"

    def test_sign_response(self):
        result = self.actions.sign_response(
            action_type="authentication", verdict="Allow", secret=SECRET
        )
        assert result["object"] == "authentication_action_response"
