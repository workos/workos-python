import hashlib
import hmac
import json
import time

import pytest
from workos.events.models import EventSchema
from workos.webhooks._verification import (
    verify_event as standalone_verify_event,
    verify_header as standalone_verify_header,
)


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


SAMPLE_EVENT = json.dumps(
    {
        "object": "event",
        "id": "evt_01",
        "event": "user.created",
        "data": {"id": "user_01", "email": "test@example.com"},
        "created_at": "2024-01-01T00:00:00Z",
    }
)
SECRET = "whsec_test_secret"


class TestWebhooksVerifyEvent:
    def test_verify_event_valid(self, workos):
        sig = _make_sig_header(SAMPLE_EVENT, SECRET)
        result = workos.webhooks.verify_event(
            event_body=SAMPLE_EVENT, event_signature=sig, secret=SECRET
        )
        assert isinstance(result, EventSchema)
        assert result.id == "evt_01"

    def test_verify_event_valid_bytes(self, workos):
        sig = _make_sig_header(SAMPLE_EVENT, SECRET)
        result = workos.webhooks.verify_event(
            event_body=SAMPLE_EVENT.encode("utf-8"), event_signature=sig, secret=SECRET
        )
        assert isinstance(result, EventSchema)
        assert result.id == "evt_01"

    def test_verify_event_invalid_signature(self, workos):
        sig = _make_sig_header(SAMPLE_EVENT, "wrong_secret")
        with pytest.raises(ValueError, match="does not match"):
            workos.webhooks.verify_event(
                event_body=SAMPLE_EVENT, event_signature=sig, secret=SECRET
            )

    def test_verify_event_stale_timestamp(self, workos):
        old_ts = int((time.time() - 300) * 1000)
        sig = _make_sig_header(SAMPLE_EVENT, SECRET, old_ts)
        with pytest.raises(ValueError, match="tolerance zone"):
            workos.webhooks.verify_event(
                event_body=SAMPLE_EVENT,
                event_signature=sig,
                secret=SECRET,
                tolerance=180,
            )

    def test_verify_event_custom_tolerance(self, workos):
        old_ts = int((time.time() - 10) * 1000)
        sig = _make_sig_header(SAMPLE_EVENT, SECRET, old_ts)
        result = workos.webhooks.verify_event(
            event_body=SAMPLE_EVENT, event_signature=sig, secret=SECRET, tolerance=60
        )
        assert isinstance(result, EventSchema)
        assert result.id == "evt_01"

    def test_verify_event_malformed_header(self, workos):
        with pytest.raises(ValueError, match="Unable to extract"):
            workos.webhooks.verify_event(
                event_body=SAMPLE_EVENT, event_signature="bad-header", secret=SECRET
            )


class TestWebhooksVerifyHeader:
    def test_verify_header_valid(self, workos):
        sig = _make_sig_header(SAMPLE_EVENT, SECRET)
        workos.webhooks.verify_header(
            event_body=SAMPLE_EVENT, event_signature=sig, secret=SECRET
        )

    def test_verify_header_invalid_signature(self, workos):
        sig = _make_sig_header(SAMPLE_EVENT, "wrong_secret")
        with pytest.raises(ValueError, match="does not match"):
            workos.webhooks.verify_header(
                event_body=SAMPLE_EVENT, event_signature=sig, secret=SECRET
            )

    def test_verify_header_stale_timestamp(self, workos):
        old_ts = int((time.time() - 300) * 1000)
        sig = _make_sig_header(SAMPLE_EVENT, SECRET, old_ts)
        with pytest.raises(ValueError, match="tolerance zone"):
            workos.webhooks.verify_header(
                event_body=SAMPLE_EVENT,
                event_signature=sig,
                secret=SECRET,
                tolerance=180,
            )


class TestStandaloneVerifyEvent:
    def test_standalone_verify_event(self):
        sig = _make_sig_header(SAMPLE_EVENT, SECRET)
        result = standalone_verify_event(
            event_body=SAMPLE_EVENT.encode("utf-8"), event_signature=sig, secret=SECRET
        )
        assert isinstance(result, EventSchema)
        assert result.id == "evt_01"

    def test_standalone_verify_event_invalid(self):
        sig = _make_sig_header(SAMPLE_EVENT, "wrong")
        with pytest.raises(ValueError, match="does not match"):
            standalone_verify_event(
                event_body=SAMPLE_EVENT.encode("utf-8"),
                event_signature=sig,
                secret=SECRET,
            )

    def test_standalone_verify_header(self):
        sig = _make_sig_header(SAMPLE_EVENT, SECRET)
        standalone_verify_header(
            event_body=SAMPLE_EVENT.encode("utf-8"), event_signature=sig, secret=SECRET
        )

    def test_standalone_verify_header_invalid(self):
        sig = _make_sig_header(SAMPLE_EVENT, "wrong")
        with pytest.raises(ValueError, match="does not match"):
            standalone_verify_header(
                event_body=SAMPLE_EVENT.encode("utf-8"),
                event_signature=sig,
                secret=SECRET,
            )
