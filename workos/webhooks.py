import hashlib
import hmac
import time
import hashlib
from typing import Optional, Protocol
from workos.types.webhooks.webhook import Webhook
from workos.types.webhooks.webhook_payload import WebhookPayload
from workos.typing.webhooks import WebhookTypeAdapter
from workos.utils.validation import Module, validate_settings


class WebhooksModule(Protocol):
    def verify_event(
        self,
        payload: WebhookPayload,
        sig_header: str,
        secret: str,
        tolerance: Optional[int] = None,
    ) -> Webhook: ...

    def verify_header(
        self,
        event_body: WebhookPayload,
        event_signature: str,
        secret: str,
        tolerance: Optional[int] = None,
    ) -> None: ...

    def constant_time_compare(self, val1: str, val2: str) -> bool: ...

    def check_timestamp_range(self, time: float, max_range: float) -> None: ...


class Webhooks(WebhooksModule):
    """Offers methods through the WorkOS Webhooks service."""

    @validate_settings(Module.WEBHOOKS)
    def __init__(self) -> None:
        pass

    DEFAULT_TOLERANCE = 180

    def verify_event(
        self,
        payload: WebhookPayload,
        sig_header: str,
        secret: str,
        tolerance: Optional[int] = DEFAULT_TOLERANCE,
    ) -> Webhook:
        Webhooks.verify_header(self, payload, sig_header, secret, tolerance)
        return WebhookTypeAdapter.validate_json(payload)

    def verify_header(
        self,
        event_body: WebhookPayload,
        event_signature: str,
        secret: str,
        tolerance: Optional[int] = None,
    ) -> None:
        try:
            # Verify and define variables parsed from the event body
            issued_timestamp, signature_hash = event_signature.split(", ")
        except BaseException:
            raise ValueError(
                "Unable to extract timestamp and signature hash from header",
                event_signature,
            )

        issued_timestamp = issued_timestamp[2:]
        signature_hash = signature_hash[3:]
        max_seconds_since_issued = tolerance or Webhooks.DEFAULT_TOLERANCE
        current_time = time.time()
        timestamp_in_seconds = int(issued_timestamp) / 1000
        seconds_since_issued = current_time - timestamp_in_seconds

        # Check that the webhook timestamp is within the acceptable range
        Webhooks.check_timestamp_range(
            self, seconds_since_issued, max_seconds_since_issued
        )

        # Set expected signature value based on env var secret
        unhashed_string = "{0}.{1}".format(issued_timestamp, event_body.decode("utf-8"))
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            unhashed_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Use constant time comparison function to ensure the sig hash matches
        # the expected sig value
        secure_compare = Webhooks.constant_time_compare(
            self, signature_hash, expected_signature
        )
        if not secure_compare:
            raise ValueError(
                "Signature hash does not match the expected signature hash for payload"
            )

    def constant_time_compare(self, val1: str, val2: str) -> bool:
        if len(val1) != len(val2):
            return False

        result = 0
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
            if result != 0:
                return False

        if result == 0:
            return True

        return False

    def check_timestamp_range(self, time: float, max_range: float) -> None:
        if time > max_range:
            raise ValueError("Timestamp outside the tolerance zone")
