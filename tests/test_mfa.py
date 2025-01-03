from workos.mfa import Mfa
import pytest


class TestMfa(object):
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.mfa = Mfa(http_client=self.http_client)

    @pytest.fixture
    def mock_enroll_factor_no_type(self):
        return None

    @pytest.fixture
    def mock_enroll_factor_incorrect_type(self):
        return "dinosaur"

    @pytest.fixture
    def mock_enroll_factor_totp_payload(self):
        return [
            "totp",
            "workos",
            "stanley@yelnats.com",
        ]

    @pytest.fixture
    def mock_enroll_factor_sms_payload(self):
        return ["sms", "7208675309"]

    @pytest.fixture
    def mock_challenge_factor_payload(self):
        return ["auth_factor_01FWRSPQ2XXXQKBCY5AAW5T59W", "Your code is {{code}}"]

    @pytest.fixture
    def mock_verify_challenge_payload(self):
        return ["auth_challenge_01FWRY5H0XXXX0JGGVTY6QFX7X", "626592"]

    @pytest.fixture
    def mock_enroll_factor_response_sms(self):
        return {
            "object": "authentication_factor",
            "id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
            "created_at": "2022-02-15T15:14:19.392Z",
            "updated_at": "2022-02-15T15:14:19.392Z",
            "type": "sms",
            "sms": {"phone_number": "+19204703484"},
            "user_id": None,
        }

    @pytest.fixture
    def mock_enroll_factor_response_totp(self):
        return {
            "object": "authentication_factor",
            "id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
            "created_at": "2022-02-15T15:14:19.392Z",
            "updated_at": "2022-02-15T15:14:19.392Z",
            "type": "totp",
            "totp": {
                "issuer": "FooCorp",
                "user": "test@example.com",
                "qr_code": "data:image/png;base64,{base64EncodedPng}",
                "secret": "NAGCCFS3EYRB422HNAKAKY3XDUORMSRF",
                "uri": "otpauth://totp/FooCorp:alan.turing@foo-corp.com?secret=NAGCCFS3EYRB422HNAKAKY3XDUORMSRF&issuer=FooCorp",
            },
            "user_id": None,
        }

    @pytest.fixture
    def mock_get_factor_response_totp(self):
        return {
            "object": "authentication_factor",
            "id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
            "created_at": "2022-02-15T15:14:19.392Z",
            "updated_at": "2022-02-15T15:14:19.392Z",
            "type": "totp",
            "totp": {
                "issuer": "FooCorp",
                "user": "test@example.com",
            },
            "user_id": None,
        }

    @pytest.fixture
    def mock_challenge_factor_response(self):
        return {
            "object": "authentication_challenge",
            "id": "auth_challenge_01FVYZWQTZQ5VB6BC5MPG2EYC5",
            "created_at": "2022-02-15T15:26:53.274Z",
            "updated_at": "2022-02-15T15:26:53.274Z",
            "expires_at": "2022-02-15T15:36:53.279Z",
            "authentication_factor_id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
            "code": None,
        }

    @pytest.fixture
    def mock_verify_challenge_response(self):
        return {
            "challenge": {
                "object": "authentication_challenge",
                "id": "auth_challenge_01FVYZWQTZQ5VB6BC5MPG2EYC5",
                "created_at": "2022-02-15T15:26:53.274Z",
                "updated_at": "2022-02-15T15:26:53.274Z",
                "expires_at": "2022-02-15T15:36:53.279Z",
                "authentication_factor_id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
                "code": None,
            },
            "valid": True,
        }

    def test_enroll_factor_totp_no_issuer(self, mock_enroll_factor_totp_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(
                type=mock_enroll_factor_totp_payload[0],
                totp_issuer=None,
                totp_user=mock_enroll_factor_totp_payload[2],
            )
        assert (
            "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp"
            in str(err.value)
        )

    def test_enroll_factor_totp_no_user(self, mock_enroll_factor_totp_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(
                type=mock_enroll_factor_totp_payload[0],
                totp_issuer=mock_enroll_factor_totp_payload[1],
                totp_user=None,
            )
        assert (
            "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp"
            in str(err.value)
        )

    def test_enroll_factor_sms_no_phone_number(self, mock_enroll_factor_sms_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(
                type=mock_enroll_factor_sms_payload[0], phone_number=None
            )
        assert (
            "Incomplete arguments. Need to specify phone_number when type is sms"
            in str(err.value)
        )

    def test_enroll_factor_sms_success(
        self, mock_enroll_factor_response_sms, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_enroll_factor_response_sms, 200
        )
        enroll_factor = self.mfa.enroll_factor(type="sms", phone_number="9204448888")

        assert request_kwargs["url"].endswith("/auth/factors/enroll")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "type": "sms",
            "phone_number": "9204448888",
        }
        assert enroll_factor.dict() == mock_enroll_factor_response_sms

    def test_enroll_factor_totp_success(
        self, mock_enroll_factor_response_totp, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_enroll_factor_response_totp, 200
        )
        enroll_factor = self.mfa.enroll_factor(
            type="totp", totp_issuer="testissuer", totp_user="testuser"
        )

        assert request_kwargs["url"].endswith("/auth/factors/enroll")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "type": "totp",
            "totp_issuer": "testissuer",
            "totp_user": "testuser",
        }
        assert enroll_factor.dict() == mock_enroll_factor_response_totp

    def test_get_factor_totp_success(
        self, mock_get_factor_response_totp, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_get_factor_response_totp, 200
        )
        authentication_factor_id = mock_get_factor_response_totp["id"]
        response = self.mfa.get_factor(
            authentication_factor_id=authentication_factor_id
        )

        assert request_kwargs["url"].endswith(
            f"/auth/factors/{authentication_factor_id}"
        )
        assert request_kwargs["method"] == "get"
        assert response.dict() == mock_get_factor_response_totp

    def test_get_factor_sms_success(
        self, mock_enroll_factor_response_sms, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_enroll_factor_response_sms, 200
        )

        authentication_factor_id = mock_enroll_factor_response_sms["id"]
        response = self.mfa.get_factor(
            authentication_factor_id=authentication_factor_id
        )

        assert request_kwargs["url"].endswith(
            f"/auth/factors/{authentication_factor_id}"
        )
        assert request_kwargs["method"] == "get"
        assert response.dict() == mock_enroll_factor_response_sms

    def test_delete_factor_success(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, None, 200
        )
        response = self.mfa.delete_factor("auth_factor_01FZ4TS14D1PHFNZ9GF6YD8M1F")
        assert request_kwargs["url"].endswith(
            "/auth/factors/auth_factor_01FZ4TS14D1PHFNZ9GF6YD8M1F"
        )
        assert request_kwargs["method"] == "delete"
        assert response is None

    def test_challenge_success(
        self, mock_challenge_factor_response, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_challenge_factor_response, 200
        )
        challenge_factor = self.mfa.challenge_factor(
            authentication_factor_id="auth_factor_01FXNWW32G7F3MG8MYK5D1HJJM"
        )
        assert request_kwargs["url"].endswith(
            "/auth/factors/auth_factor_01FXNWW32G7F3MG8MYK5D1HJJM/challenge"
        )
        assert request_kwargs["method"] == "post"
        assert challenge_factor.dict() == mock_challenge_factor_response

    def test_verify_success(
        self, mock_verify_challenge_response, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_verify_challenge_response, 200
        )
        verify_challenge = self.mfa.verify_challenge(
            authentication_challenge_id="auth_challenge_01FXNXH8Y2K3YVWJ10P139A6DT",
            code="093647",
        )

        assert request_kwargs["url"].endswith(
            "/auth/challenges/auth_challenge_01FXNXH8Y2K3YVWJ10P139A6DT/verify"
        )
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {"code": "093647"}
        assert verify_challenge.dict() == mock_verify_challenge_response
