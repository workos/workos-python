import json
from os import error
from workos.webhooks import Webhooks
from requests import Response
import time
import pytest
import workos
from workos.webhooks import Webhooks
from workos.utils.request import RESPONSE_TYPE_CODE


class TestWebhooks(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.webhooks = Webhooks()

    @pytest.fixture
    def mock_event_body(self):
        return '{"id":"wh_01FG9JXJ9C9S052FX59JVG4EG1","data":{"id":"conn_01EHWNC0FCBHZ3BJ7EGKYXK0E6","name":"Foo Corp\'s Connection","state":"active","object":"connection","domains":[{"id":"conn_domain_01EHWNFTAFCF3CQAE5A9Q0P1YB","domain":"foo-corp.com","object":"connection_domain"}],"connection_type":"OktaSAML","organization_id":"org_01EHWNCE74X7JSDV0X3SZ3KJNY"},"event":"connection.activated"}'

    @pytest.fixture
    def mock_header(self):
        return "t=1632409405772, v1=67612f0e74f008b436a13b00266f90ef5c13f9cbcf6262206f5f4a539ff61702"

    @pytest.fixture
    def mock_secret(self):
        return "1lyKDzhJjuCkIscIWqkSe4YsQ"

    @pytest.fixture
    def mock_bad_secret(self):
        return "this_is_not_it_123"

    @pytest.fixture
    def mock_header_no_timestamp(self):
        return "v1=67612f0e74f008b436a13b00266f90ef5c13f9cbcf6262206f5f4a539ff61702"

    @pytest.fixture
    def mock_sig_hash(self):
        return "df25b6efdd39d82e7b30e75ea19655b306860ad5cde3eeaeb6f1dfea029ea259"

    def test_missing_body(self, mock_header, mock_secret):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(None, mock_header, mock_secret)
        assert "Payload body is missing and is a required parameter" in str(err.value)

    def test_missing_header(self, mock_event_body, mock_secret):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(
                mock_event_body.encode("utf-8"), None, mock_secret
            )
        assert "Payload signature missing and is a required parameter" in str(err.value)

    def test_missing_secret(self, mock_event_body, mock_header):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(
                mock_event_body.encode("utf-8"), mock_header, None
            )
        assert "Secret is missing and is a required parameter" in str(err.value)

    def test_unable_to_extract_timestamp(
        self, mock_event_body, mock_header_no_timestamp, mock_secret
    ):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(
                mock_event_body.encode("utf-8"),
                mock_header_no_timestamp,
                mock_secret,
                180,
            )
        assert "Unable to extract timestamp and signature hash from header" in str(
            err.value
        )

    def test_timestamp_outside_threshold(
        self, mock_event_body, mock_header, mock_secret
    ):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(
                mock_event_body.encode("utf-8"), mock_header, mock_secret, 0
            )
        assert "Timestamp outside the tolerance zone" in str(err.value)

    def test_sig_hash_does_not_match_expected_sig_length(self, mock_sig_hash):
        result = self.webhooks.constant_time_compare(
            mock_sig_hash,
            "df25b6efdd39d82e7b30e75ea19655b306860ad5cde3eeaeb6f1dfea029ea25",
        )
        assert result == False

    def test_sig_hash_does_not_match_expected_sig_value(self, mock_sig_hash):
        result = self.webhooks.constant_time_compare(
            mock_sig_hash,
            "df25b6efdd39d82e7b30e75ea19655b306860ad5cde3eeaeb6f1dfea029ea252",
        )
        assert result == False

    def test_passed_expected_event_validation(
        self, mock_event_body, mock_header, mock_secret
    ):
        try:
            self.webhooks.verify_event(
                mock_event_body.encode("utf-8"),
                mock_header,
                mock_secret,
                99999999999999,
            )
        except BaseException:
            pytest.fail(
                "There was an error in validating the webhook with the expected values"
            )

    def test_sign_hash_does_not_match_expected_sig_hash_verify_header(
        self, mock_event_body, mock_header, mock_bad_secret
    ):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_header(
                mock_event_body.encode("utf-8"),
                mock_header,
                mock_bad_secret,
                99999999999999,
            )
        assert (
            "Signature hash does not match the expected signature hash for payload"
            in str(err.value)
        )
