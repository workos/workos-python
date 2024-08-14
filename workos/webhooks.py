import hashlib
import hmac
import time
from typing import Optional, Protocol
from workos.types.webhooks.webhook import Webhook
from workos.types.webhooks.webhook_payload import WebhookPayload
from workos.typing.webhooks import WebhookTypeAdapter


class WebhooksModule(Protocol):
    """Offers methods through the WorkOS Webhooks service."""

    def verify_event(
        self,
        *,
        event_body: WebhookPayload,
        event_signature: str,
        secret: str,
        tolerance: Optional[int] = None,
    ) -> Webhook:
        """Verify and deserialize the signature of a Webhook event.

        Kwargs:
            event_body (WebhookPayload): The Webhook body.
            event_signature (str): The signature of the Webhook from the 'WorkOS-Signature' header.
            secret (str): The secret for the webhook endpoint, you can find this in the WorkOS dashboard.
            tolerance (int): The number of seconds the Webhook event is valid for. (Optional)
        Returns:
            Webhook: The deserialized Webhook.
        """
        ...

    def verify_header(
        self,
        *,
        event_body: WebhookPayload,
        event_signature: str,
        secret: str,
        tolerance: Optional[int] = None,
    ) -> None:
        """Verify the signature of a Webhook, raise ValueError if the signature can't be verified.

        Kwargs:
            event_body (WebhookPayload): The Webhook body.
            event_signature (str): The signature of the Webhook from the 'WorkOS-Signature' header.
            secret (str): The secret for the webhook endpoint, you can find this in the WorkOS dashboard.
            tolerance (int): The number of seconds the Webhook event is valid for. (Optional)
        Returns:
            None
        """
        ...

    def _constant_time_compare(self, val1: str, val2: str) -> bool: ...

    def _check_timestamp_range(self, time: float, max_range: float) -> None: ...


class Webhooks(WebhooksModule):
    DEFAULT_TOLERANCE = 180

    def verify_event(
        self,
        *,
        event_body: WebhookPayload,
        event_signature: str,
        secret: str,
        tolerance: Optional[int] = DEFAULT_TOLERANCE,
    ) -> Webhook:
        Webhooks.verify_header(
            self,
            event_body=event_body,
            event_signature=event_signature,
            secret=secret,
            tolerance=tolerance,
        )
        return WebhookTypeAdapter.validate_json(event_body)

    def verify_header(
        self,
        *,
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
        Webhooks._check_timestamp_range(
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
        secure_compare = Webhooks._constant_time_compare(
            self, signature_hash, expected_signature
        )
        if not secure_compare:
            raise ValueError(
                "Signature hash does not match the expected signature hash for payload"
            )

    def _constant_time_compare(self, val1: str, val2: str) -> bool:
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

    def _check_timestamp_range(self, time: float, max_range: float) -> None:
        if time > max_range:
            raise ValueError("Timestamp outside the tolerance zone")
