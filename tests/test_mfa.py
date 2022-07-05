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
        return ["Your code is {{code}}"]

    @pytest.fixture
    def mock_verify_challenge_payload(self):
        return ["auth_challenge_01FWRY5H0XXXX0JGGVTY6QFX7X", "626592"]

    @pytest.fixture
    def mock_enroll_factor_response_sms(self):
        return {
            "object": "authentication_factor",
            "id": "auth_factor_01FXK4YXEZEEQ0AYNJE5PA7FQR",
            "created_at": "2022-03-07T21:35:57.853Z",
            "updated_at": "2022-03-07T21:35:57.853Z",
            "type": "sms",
            "sms": {"phone_number": "+17208675309"},
        }

    @pytest.fixture
    def mock_enroll_factor_response_totp(self):
        return {
            "object": "authentication_factor",
            "id": "auth_factor_01FXNWW32G7F3MG8MYK5D1HJJM",
            "created_at": "2022-03-08T23:12:20.157Z",
            "updated_at": "2022-03-08T23:12:20.157Z",
            "type": "totp",
            "totp": {
                "qr_code": "data:image/png;base64,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",
                "secret": "JJWBYBLLH5TRKYZEGMREU6DRKFRVMTCV",
                "uri": "otpauth://totp/testytest:berniesanders?secret=JJWBYBLLH5TRKYZEGMREU6DRKFRVMTCV&issuer=testytest",
            },
        }

    @pytest.fixture
    def mock_challenge_factor_response(self):
        return {
            "object": "authentication_challenge",
            "id": "auth_challenge_01FXNX3BTZPPJVKF65NNWGRHZJ",
            "created_at": "2022-03-08T23:16:18.532Z",
            "updated_at": "2022-03-08T23:16:18.532Z",
            "expires_at": "2022-03-08T23:16:18.532Z",
            "code": "XXX123XXX",
            "authentication_factor_id": "auth_factor_01FXNWW32G7F3MG8MYK5D1HJJM",
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
            "valid": True,
        }

    def test_enroll_factor_no_type(self, mock_enroll_factor_no_type):
        print(mock_enroll_factor_no_type)
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
        self, mock_verify_factor_response, mock_request_method
    ):
        mock_request_method("post", mock_verify_factor_response, 200)
        verify_factor = self.mfa.verify_factor(
            "auth_challenge_01FXNXH8Y2K3YVWJ10P139A6DT", "093647"
        )
        assert verify_factor == mock_verify_factor_response

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
