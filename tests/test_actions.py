import hashlib
import hmac
import json
import time

import pytest
from workos.actions import Actions, AsyncActions


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


SAMPLE_ACTION_PAYLOAD = json.dumps(
    {
        "type": "authentication",
        "user": {"id": "user_01", "email": "test@example.com"},
        "organization": {"id": "org_01"},
    }
)

SECRET = "test_secret_key"


class TestActions:
    def setup_method(self):
        self.actions = Actions()

    def test_verify_header_valid(self):
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET)
        self.actions.verify_header(
            payload=SAMPLE_ACTION_PAYLOAD,
            sig_header=sig,
            secret=SECRET,
        )

    def test_verify_header_invalid_signature(self):
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET)
        with pytest.raises(ValueError, match="does not match"):
            self.actions.verify_header(
                payload='{"tampered": true}',
                sig_header=sig,
                secret=SECRET,
            )

    def test_verify_header_stale_timestamp(self):
        old_ts = int((time.time() - 60) * 1000)
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET, old_ts)
        with pytest.raises(ValueError, match="tolerance zone"):
            self.actions.verify_header(
                payload=SAMPLE_ACTION_PAYLOAD,
                sig_header=sig,
                secret=SECRET,
                tolerance=30,
            )

    def test_verify_header_custom_tolerance(self):
        old_ts = int((time.time() - 10) * 1000)
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET, old_ts)
        self.actions.verify_header(
            payload=SAMPLE_ACTION_PAYLOAD,
            sig_header=sig,
            secret=SECRET,
            tolerance=60,
        )

    def test_verify_header_malformed_header(self):
        with pytest.raises(ValueError, match="Unable to extract"):
            self.actions.verify_header(
                payload=SAMPLE_ACTION_PAYLOAD,
                sig_header="invalid-header",
                secret=SECRET,
            )

    def test_verify_header_bytes_payload(self):
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET)
        self.actions.verify_header(
            payload=SAMPLE_ACTION_PAYLOAD.encode("utf-8"),
            sig_header=sig,
            secret=SECRET,
        )

    def test_construct_action_valid(self):
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET)
        result = self.actions.construct_action(
            payload=SAMPLE_ACTION_PAYLOAD,
            sig_header=sig,
            secret=SECRET,
        )
        assert result["type"] == "authentication"
        assert result["user"]["id"] == "user_01"

    def test_construct_action_invalid_signature(self):
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, "wrong_secret")
        with pytest.raises(ValueError):
            self.actions.construct_action(
                payload=SAMPLE_ACTION_PAYLOAD,
                sig_header=sig,
                secret=SECRET,
            )

    def test_sign_response_authentication_allow(self):
        result = self.actions.sign_response(
            action_type="authentication",
            verdict="Allow",
            secret=SECRET,
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
            action_type="authentication",
            verdict="Allow",
            secret=SECRET,
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
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET)
        self.actions.verify_header(
            payload=SAMPLE_ACTION_PAYLOAD,
            sig_header=sig,
            secret=SECRET,
        )

    def test_construct_action_valid(self):
        sig = _make_sig_header(SAMPLE_ACTION_PAYLOAD, SECRET)
        result = self.actions.construct_action(
            payload=SAMPLE_ACTION_PAYLOAD,
            sig_header=sig,
            secret=SECRET,
        )
        assert result["type"] == "authentication"

    def test_sign_response(self):
        result = self.actions.sign_response(
            action_type="authentication",
            verdict="Allow",
            secret=SECRET,
        )
        assert result["object"] == "authentication_action_response"
