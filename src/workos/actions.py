# @oagen-ignore-file
# This file is hand-maintained. AuthKit Actions helpers for request
# verification and response signing. These are client-side cryptographic
# helpers that will always be hand-maintained.

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Literal, Optional, Union

DEFAULT_TOLERANCE = 30  # seconds (stricter than webhooks' 180s)

ActionType = Literal["authentication", "user_registration"]

_ACTION_TYPE_TO_RESPONSE_OBJECT = {
    "authentication": "authentication_action_response",
    "user_registration": "user_registration_action_response",
}


def _verify_signature(
    *,
    payload: Union[bytes, str],
    sig_header: str,
    secret: str,
    tolerance: int = DEFAULT_TOLERANCE,
) -> None:
    """Verify an HMAC-SHA256 signature header. Raises ValueError on failure."""
    try:
        issued_part, sig_part = sig_header.split(", ")
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

    if seconds_since_issued > tolerance:
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


class Actions:
    """AuthKit Actions request verification and response signing."""

    def verify_header(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> None:
        """Verify the signature of an Actions request."""
        _verify_signature(
            payload=payload, sig_header=sig_header, secret=secret, tolerance=tolerance,
        )

    def construct_action(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> Dict[str, Any]:
        """Verify and deserialize an Actions request payload."""
        self.verify_header(
            payload=payload, sig_header=sig_header, secret=secret, tolerance=tolerance,
        )
        body = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        return json.loads(body)

    def sign_response(
        self,
        *,
        action_type: ActionType,
        verdict: Literal["Allow", "Deny"],
        error_message: Optional[str] = None,
        secret: str,
    ) -> Dict[str, Any]:
        """Build and sign an Actions response."""
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


class AsyncActions:
    """Async variant of AuthKit Actions helpers."""

    def verify_header(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> None:
        """Verify the signature of an Actions request."""
        _verify_signature(
            payload=payload, sig_header=sig_header, secret=secret, tolerance=tolerance,
        )

    def construct_action(
        self,
        *,
        payload: Union[bytes, str],
        sig_header: str,
        secret: str,
        tolerance: int = DEFAULT_TOLERANCE,
    ) -> Dict[str, Any]:
        """Verify and deserialize an Actions request payload."""
        self.verify_header(
            payload=payload, sig_header=sig_header, secret=secret, tolerance=tolerance,
        )
        body = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        return json.loads(body)

    def sign_response(
        self,
        *,
        action_type: ActionType,
        verdict: Literal["Allow", "Deny"],
        error_message: Optional[str] = None,
        secret: str,
    ) -> Dict[str, Any]:
        """Build and sign an Actions response."""
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
