from workos.mfa import Mfa
import pytest


class TestMfa(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.mfa = Mfa()

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
                "qr_code": "data:image/png;base64,{base64EncodedPng}",
                "secret": "NAGCCFS3EYRB422HNAKAKY3XDUORMSRF",
                "uri": "otpauth://totp/FooCorp:alan.turing@foo-corp.com?secret=NAGCCFS3EYRB422HNAKAKY3XDUORMSRF&issuer=FooCorp",
            },
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
            },
            "valid": "true",
        }

    def test_enroll_factor_no_type(self, mock_enroll_factor_no_type):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_no_type)
        assert "Incomplete arguments. Need to specify a type of factor" in str(
            err.value
        )

    def test_enroll_factor_incorrect_type(self, mock_enroll_factor_incorrect_type):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_incorrect_type)
        assert "Type parameter must be either 'sms' or 'totp'" in str(err.value)

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
        self, mock_enroll_factor_response_sms, mock_request_method
    ):
        mock_request_method("post", mock_enroll_factor_response_sms, 200)
        enroll_factor = self.mfa.enroll_factor("sms", None, None, 9204448888)
        assert enroll_factor == mock_enroll_factor_response_sms

    def test_enroll_factor_totp_success(
        self, mock_enroll_factor_response_totp, mock_request_method
    ):
        mock_request_method("post", mock_enroll_factor_response_totp, 200)
        enroll_factor = self.mfa.enroll_factor(
            "totp", "testytest", "berniesanders", None
        )
        assert enroll_factor == mock_enroll_factor_response_totp

    def test_get_factor_no_id(self):
        with pytest.raises(ValueError) as err:
            self.mfa.delete_factor(authentication_factor_id=None)
        assert "Incomplete arguments. Need to specify a factor ID." in str(err.value)

    def test_get_factor_totp_success(
        self, mock_enroll_factor_response_totp, mock_request_method
    ):
        mock_request_method("get", mock_enroll_factor_response_totp, 200)
        response = self.mfa.get_factor(mock_enroll_factor_response_totp["id"])
        assert response == mock_enroll_factor_response_totp

    def test_get_factor_sms_success(
        self, mock_enroll_factor_response_sms, mock_request_method
    ):
        mock_request_method("get", mock_enroll_factor_response_sms, 200)
        response = self.mfa.get_factor(mock_enroll_factor_response_sms["id"])
        assert response == mock_enroll_factor_response_sms

    def test_delete_factor_no_id(self):
        with pytest.raises(ValueError) as err:
            self.mfa.delete_factor(authentication_factor_id=None)
        assert "Incomplete arguments. Need to specify a factor ID." in str(err.value)

    def test_delete_factor_success(self, mock_request_method):
        mock_request_method("delete", None, 200)
        response = self.mfa.delete_factor("auth_factor_01FZ4TS14D1PHFNZ9GF6YD8M1F")
        assert response == None

    def test_challenge_factor_no_id(self, mock_challenge_factor_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.challenge_factor(
                authentication_factor_id=None,
                sms_template=mock_challenge_factor_payload[1],
            )
        assert (
            "Incomplete arguments: 'authentication_factor_id' is a required parameter"
            in str(err.value)
        )

    def test_challenge_success(
        self, mock_challenge_factor_response, mock_request_method
    ):
        mock_request_method("post", mock_challenge_factor_response, 200)
        challenge_factor = self.mfa.challenge_factor(
            "auth_factor_01FXNWW32G7F3MG8MYK5D1HJJM"
        )
        assert challenge_factor == mock_challenge_factor_response

    def test_verify_factor_no_id(self, mock_verify_challenge_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.verify_factor(
                authentication_challenge_id=None, code=mock_verify_challenge_payload[1]
            )
        assert (
            "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters"
            in str(err.value)
        )

    def test_verify_factor_no_code(self, mock_verify_challenge_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.verify_factor(
                authentication_challenge_id=mock_verify_challenge_payload[0], code=None
            )
        assert (
            "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters"
            in str(err.value)
        )

    def test_verify_factor_success(
        self, mock_verify_challenge_response, mock_request_method
    ):
        mock_request_method("post", mock_verify_challenge_response, 200)
        verify_factor = self.mfa.verify_factor(
            "auth_challenge_01FXNXH8Y2K3YVWJ10P139A6DT", "093647"
        )
        assert verify_factor == mock_verify_challenge_response

    def test_verify_challenge_no_id(self, mock_verify_challenge_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.verify_challenge(
                authentication_challenge_id=None, code=mock_verify_challenge_payload[1]
            )
            assert (
                "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters"
                in str(err.value)
            )

    def test_verify_challenge_no_code(self, mock_verify_challenge_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.verify_challenge(
                authentication_challenge_id=mock_verify_challenge_payload[0], code=None
            )
            assert (
                "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters"
                in str(err.value)
            )

    def test_verify_success(self, mock_verify_challenge_response, mock_request_method):
        mock_request_method("post", mock_verify_challenge_response, 200)
        verify_challenge = self.mfa.verify_challenge(
            "auth_challenge_01FXNXH8Y2K3YVWJ10P139A6DT", "093647"
        )
        assert verify_challenge == mock_verify_challenge_response
