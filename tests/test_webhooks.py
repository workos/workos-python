import json
import pytest
from workos.webhooks import Webhooks


class TestWebhooks(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.webhooks = Webhooks()

    @pytest.fixture
    def mock_event_body(self):
        return '{"id":"event_01J44T8116Q5M0RYCFA6KWNXN9","data":{"id":"conn_01EHWNC0FCBHZ3BJ7EGKYXK0E6","name":"Foo Corp\'s Connection","state":"active","object":"connection","status":"linked","domains":[{"id":"conn_domain_01EHWNFTAFCF3CQAE5A9Q0P1YB","domain":"foo-corp.com","object":"connection_domain"}],"created_at":"2021-06-25T19:07:33.155Z","updated_at":"2021-06-25T19:07:33.155Z","external_key":"3QMR4u0Tok6SgwY2AWG6u6mkQ","connection_type":"OktaSAML","organization_id":"org_01EHWNCE74X7JSDV0X3SZ3KJNY"},"event":"connection.activated","created_at":"2021-06-25T19:07:33.155Z"}'

    @pytest.fixture
    def mock_header(self):
        return "t=1722443701539, v1=bd54a3768f461461c8439c2f97ab0d646ef3976f84d5d5b132d18f2fa89cdad5"

    @pytest.fixture
    def mock_secret(self):
        return "2sAZJlbjP8Ce3rwkKEv2GfKef"

    @pytest.fixture
    def mock_bad_secret(self):
        return "this_is_not_it_123"

    @pytest.fixture
    def mock_header_no_timestamp(self):
        return "v1=bd54a3768f461461c8439c2f97ab0d646ef3976f84d5d5b132d18f2fa89cdad5"

    @pytest.fixture
    def mock_sig_hash(self):
        return "df25b6efdd39d82e7b30e75ea19655b306860ad5cde3eeaeb6f1dfea029ea259"

    @pytest.fixture
    def mock_unknown_webhook_body(self):
        return '{"id":"event_01J44T8116Q5M0RYCFA6KWNXN9","data":{"id":"meow_123","name":"Meow Corp","object":"kitten","status":"cuteness","created_at":"2021-06-25T19:07:33.155Z","updated_at":"2021-06-25T19:07:33.155Z"},"event":"kitten.created","created_at":"2021-06-25T19:07:33.155Z"}'

    @pytest.fixture
    def mock_unknown_webhook_header(self):
        return "t=1722443701539, v1=f82f88dd60d5bc8a803686a27f83ce148b8c37c54490c52b77d00d62da891f1b"

    def test_unable_to_extract_timestamp(
        self, mock_event_body, mock_header_no_timestamp, mock_secret
    ):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(
                event_body=mock_event_body.encode("utf-8"),
                event_signature=mock_header_no_timestamp,
                secret=mock_secret,
                tolerance=180,
            )
        assert "Unable to extract timestamp and signature hash from header" in str(
            err.value
        )

    def test_timestamp_outside_threshold(
        self, mock_event_body, mock_header, mock_secret
    ):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_event(
                event_body=mock_event_body.encode("utf-8"),
                event_signature=mock_header,
                secret=mock_secret,
                tolerance=0,
            )
        assert "Timestamp outside the tolerance zone" in str(err.value)

    def test_sig_hash_does_not_match_expected_sig_length(self, mock_sig_hash):
        result = self.webhooks._constant_time_compare(
            mock_sig_hash,
            "df25b6efdd39d82e7b30e75ea19655b306860ad5cde3eeaeb6f1dfea029ea25",
        )
        assert result == False

    def test_sig_hash_does_not_match_expected_sig_value(self, mock_sig_hash):
        result = self.webhooks._constant_time_compare(
            mock_sig_hash,
            "df25b6efdd39d82e7b30e75ea19655b306860ad5cde3eeaeb6f1dfea029ea252",
        )
        assert result == False

    def test_passed_expected_event_validation(
        self, mock_event_body, mock_header, mock_secret
    ):
        try:
            webhook = self.webhooks.verify_event(
                event_body=mock_event_body.encode("utf-8"),
                event_signature=mock_header,
                secret=mock_secret,
                tolerance=99999999999999,
            )
            assert type(webhook).__name__ == "ConnectionActivatedWebhook"
        except BaseException:
            pytest.fail(
                "There was an error in validating the webhook with the expected values"
            )

    def test_sign_hash_does_not_match_expected_sig_hash_verify_header(
        self, mock_event_body, mock_header, mock_bad_secret
    ):
        with pytest.raises(ValueError) as err:
            self.webhooks.verify_header(
                event_body=mock_event_body.encode("utf-8"),
                event_signature=mock_header,
                secret=mock_bad_secret,
                tolerance=99999999999999,
            )
        assert (
            "Signature hash does not match the expected signature hash for payload"
            in str(err.value)
        )

    def test_unrecognized_webhook_type_returns_untyped_webhook(
        self, mock_unknown_webhook_body, mock_unknown_webhook_header, mock_secret
    ):
        result = self.webhooks.verify_event(
            event_body=mock_unknown_webhook_body.encode("utf-8"),
            event_signature=mock_unknown_webhook_header,
            secret=mock_secret,
            tolerance=99999999999999,
        )
        assert type(result).__name__ == "UntypedWebhook"
        assert result.dict() == json.loads(mock_unknown_webhook_body)
