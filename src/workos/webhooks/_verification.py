# @oagen-ignore-file
# This file is hand-maintained. It provides webhook signature verification
# utilities that complement the auto-generated webhook CRUD operations.

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Optional, Union

from workos.events.models import EventSchema, EventSchemaVariant

WebhookPayload = Union[bytes, bytearray]

DEFAULT_TOLERANCE = 180  # seconds


def verify_event(
    *,
    event_body: WebhookPayload,
    event_signature: str,
    secret: str,
    tolerance: Optional[int] = DEFAULT_TOLERANCE,
) -> EventSchemaVariant:
    """Verify and deserialize the signature of a Webhook event.

    Args:
        event_body: The Webhook body (bytes).
        event_signature: The signature from the 'WorkOS-Signature' header.
        secret: The secret for the webhook endpoint (from the WorkOS dashboard).
        tolerance: The number of seconds the Webhook event is valid for. (Optional)

    Returns:
        EventSchema: The deserialized webhook event.

    Raises:
        ValueError: If the signature cannot be verified or the timestamp is out of range.
    """
    verify_header(
        event_body=event_body,
        event_signature=event_signature,
        secret=secret,
        tolerance=tolerance,
    )
    return EventSchema.from_dict(json.loads(event_body))


def verify_header(
    *,
    event_body: WebhookPayload,
    event_signature: str,
    secret: str,
    tolerance: Optional[int] = None,
) -> None:
    """Verify the signature of a Webhook. Raises ValueError if verification fails.

    Args:
        event_body: The Webhook body (bytes).
        event_signature: The signature from the 'WorkOS-Signature' header.
        secret: The secret for the webhook endpoint (from the WorkOS dashboard).
        tolerance: The number of seconds the Webhook event is valid for. (Optional)

    Raises:
        ValueError: If the signature cannot be verified or the timestamp is out of range.
    """
    try:
        issued_timestamp, signature_hash = event_signature.split(", ")
    except (ValueError, AttributeError):
        raise ValueError(
            "Unable to extract timestamp and signature hash from header",
            event_signature,
        )

    issued_timestamp = issued_timestamp[2:]
    signature_hash = signature_hash[3:]
    max_seconds_since_issued = tolerance or DEFAULT_TOLERANCE
    current_time = time.time()
    timestamp_in_seconds = int(issued_timestamp) / 1000
    seconds_since_issued = current_time - timestamp_in_seconds

    if seconds_since_issued > max_seconds_since_issued:
        raise ValueError("Timestamp outside the tolerance zone")

    unhashed_string = "{0}.{1}".format(issued_timestamp, event_body.decode("utf-8"))
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        unhashed_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature_hash, expected_signature):
        raise ValueError(
            "Signature hash does not match the expected signature hash for payload"
        )
