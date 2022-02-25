from workos.mfa import MFA
import pytest

class TestWebhooks(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.mfa = MFA()

    @pytest.fixture
    def mock_enroll_factor_no_type(self):
        return None
        
    @pytest.fixture
    def mock_enroll_factor_incorrect_type(self):
        return "dinosaur"

    @pytest.fixture
    def mock_enroll_factor_totp_payload(self):
        return ["totp", "workos", "stanley@yelnats.com",]

    @pytest.fixture
    def mock_enroll_factor_sms_payload(self):
        return ["sms", "7208675309"]

    @pytest.fixture
    def mock_challenge_factor_payload(self):
        return ["auth_factor_01FWRSPQ2XXXQKBCY5AAW5T59W", "Your code is {{code}}"]

    @pytest.fixture
    def mock_verify_factor_payload(self):
        return ["auth_challenge_01FWRY5H0XXXX0JGGVTY6QFX7X", "626592"]


    def test_enroll_factor_no_type(self, mock_enroll_factor_no_type):
        print(mock_enroll_factor_no_type)
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_no_type)
        assert "Incomplete arguments. Need to specify a type of factor" in str(err.value)

    def test_enroll_factor_incorrect_type(self, mock_enroll_factor_incorrect_type):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_incorrect_type)
        assert "Type parameter must be either 'sms' or 'totp'" in str(err.value)

    def test_enroll_factor_totp_no_issuer(self, mock_enroll_factor_totp_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_totp_payload[0], totp_issuer=None, totp_user=mock_enroll_factor_totp_payload[2])
        assert "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp" in str(err.value)
    
    def test_enroll_factor_totp_no_user(self, mock_enroll_factor_totp_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_totp_payload[0], totp_issuer=mock_enroll_factor_totp_payload[1], totp_user=None)
        assert "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp" in str(err.value)

    def test_enroll_factor_sms_no_phone_number(self, mock_enroll_factor_sms_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.enroll_factor(type=mock_enroll_factor_sms_payload[0], phone_number=None)
        assert "Incomplete arguments. Need to specify phone_number when type is sms" in str(err.value)

    def test_enroll_factor_sms_success(
        self, mock_enroll_factor_sms_payload
    ):
        try:
            self.mfa.enroll_factor(
                type=mock_enroll_factor_sms_payload[0],
                phone_number=mock_enroll_factor_sms_payload[1]
            )
        except BaseException:
            pytest.fail(
                "There was an error in validating the request"
            )

    # def test_enroll_factor_totp_success(
    #     self, mock_enroll_factor_totp_payload
    # ):
    #     try:
    #         self.mfa.enroll_factor(
    #             type=mock_enroll_factor_totp_payload[0],
    #             totp_issuer=mock_enroll_factor_totp_payload[1],
    #             totp_user=mock_enroll_factor_totp_payload[2]
    #         )
    #     except BaseException:
    #         pytest.fail(
    #             "There was an error in validating the enroll factor request"
    #         )

    def test_challenge_factor_no_id(self, mock_challenge_factor_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.challenge_factor(authentication_factor_id=None, sms_template=mock_challenge_factor_payload[1])
        assert "Incomplete arguments: 'authentication_factor_id' is a required parameter" in str(err.value)

    # def test_challenge_success(
    #     self, mock_challenge_factor_payload
    # ):
    #     try:
    #         self.mfa.challenge_factor(
    #            authentication_factor_id=mock_challenge_factor_payload[0],
    #         )
    #     except BaseException:
    #         pytest.fail(
    #             "There was an error in validating the challenge factor request"
    #         )

    def test_verify_factor_no_id(self, mock_verify_factor_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.verify_factor(authentication_challenge_id=None, code=mock_verify_factor_payload[1])
        assert "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters" in str(err.value)

    def test_verify_factor_no_code(self, mock_verify_factor_payload):
        with pytest.raises(ValueError) as err:
            self.mfa.verify_factor(authentication_challenge_id=mock_verify_factor_payload[0], code=None)
        assert "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters" in str(err.value)

    # def test_verify_success(
    #     self, mock_verify_factor_payload
    # ):
    #     try:
    #         self.mfa.verify_factor(
    #            authentication_challenge_id=mock_verify_factor_payload[0],
    #            code=mock_verify_factor_payload[1]
    #         )
    #     except BaseException:
    #         pytest.fail(
    #             "There was an error in validating the verify factor request"
    #         )
