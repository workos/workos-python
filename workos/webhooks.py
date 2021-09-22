from workos.utils.request import RequestHelper
from workos.utils.validation import WEBHOOKS_MODULE, validate_settings
import hmac
import json
import time
from collections import OrderedDict
import hashlib

class Webhooks(object):
    """Offers methods through the WorkOS Webhooks service."""
    DEFAULT_TOLERANCE = 180

    @validate_settings(WEBHOOKS_MODULE)
    def __init__(self):
        pass

    @staticmethod
    def verify_event(
        payload, sig_header, secret, tolerance=DEFAULT_TOLERANCE
    ):

        WebhookSignature.verify_header(payload, sig_header, secret, tolerance)
        event = json.loads(payload, object_pairs_hook=OrderedDict) 
        return event


class WebhookSignature(object):
    @staticmethod 
    def constant_time_compare(val1, val2):
        if len(val1) != len(val2):
            return False
        result = 0
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
        return result == 0

    @staticmethod
    def verify_header(event_body, event_signature, secret, tolerance=None):
        try:
            # Define variables parsed from the event body
            issued_timestamp, signature_hash = event_signature.split(', ')
            issued_timestamp = issued_timestamp[2:]
            signature_hash = signature_hash[3:]

            # Define time related variables
            MAX_SECONDS_SINCE_ISSUED = tolerance
            current_time = time.time()
            timestamp_in_seconds = int(issued_timestamp) / 1000
            seconds_since_issued = current_time - timestamp_in_seconds

        except Exception:
            raise ValueError(
                "Unable to extract timestamp and signature hash from header",
                event_body,
                event_signature,
            )

        # Check that the webhook timestamp is within the acceptable range
        if seconds_since_issued > MAX_SECONDS_SINCE_ISSUED:
            raise ValueError(
                "Timestamp outside the tolerance zone"
            )

        #Set expected signature value based on env var secret
        unhashed_string = f'{issued_timestamp}.{event_body.decode("utf-8")}'
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            unhashed_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Use a secure constant time comparison function to ensure the signature hash matches the expected signature value
        #check time comparison with sig hash from the webhook against the expected sig
        if WebhookSignature.constant_time_compare(signature_hash, expected_signature):
            return True
        else: raise ValueError(
                "Signature hash does not match the expected signature hash for payload"
            )
