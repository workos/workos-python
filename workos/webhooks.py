from workos.utils.request import RequestHelper
from workos.utils.validation import WEBHOOKS_MODULE, validate_settings
import hmac
import json
import time
from collections import OrderedDict
import hashlib


class Webhooks(object):
    """Offers methods through the WorkOS Webhooks service."""

    @validate_settings(WEBHOOKS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    DEFAULT_TOLERANCE = 180

    def verify_event(self, payload, sig_header, secret, tolerance=DEFAULT_TOLERANCE):

        if payload is None:
            raise ValueError("Payload body is missing and is a required parameter")
        if sig_header is None:
            raise ValueError("Payload signature missing and is a required parameter")
        if secret is None:
            raise ValueError("Secret is missing and is a required parameter")

        Webhooks.verify_header(self, payload, sig_header, secret, tolerance)
        event = json.loads(payload, object_pairs_hook=OrderedDict)
        return event

    def verify_header(self, event_body, event_signature, secret, tolerance=None):
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
        max_seconds_since_issued = tolerance
        current_time = time.time()
        timestamp_in_seconds = int(issued_timestamp) / 1000
        seconds_since_issued = current_time - timestamp_in_seconds

        # Check that the webhook timestamp is within the acceptable range
        Webhooks.check_timestamp_range(
            self, seconds_since_issued, max_seconds_since_issued
        )

        # Set expected signature value based on env var secret
        unhashed_string = "{0}.{1}".format(issued_timestamp, event_body)
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            unhashed_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Use constant time comparison function to ensure the sig hash matches
        # the expected sig value
        Webhooks.constant_time_compare(self, signature_hash, expected_signature)

    def constant_time_compare(self, val1, val2):
        if len(val1) != len(val2):
            raise ValueError(
                "Signature hash does not match the expected signature hash for payload"
            )

        result = 0
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
        return result == 0

    def check_timestamp_range(self, time, max_range):
        if time > max_range:
            raise ValueError("Timestamp outside the tolerance zone")
