import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_POST,
)
from workos.utils.validation import MFA_MODULE, validate_settings

ENROLL_PATH = "auth/factors/enroll"
CHALLENGE_PATH = "auth/factors/challenge"
VERIFY_PATH = "auth/factors/verify"


class Mfa(object):
    """Methods to assist in creating, challenging, and verifying Authentication Factors through the WorkOS MFA service."""

    @validate_settings(MFA_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def enroll_factor(
        self, type=None, totp_issuer=None, totp_user=None, phone_number=None,
    ):
        """
        Defines the type of MFA authorization factor to be used. Possible values are sms or totp.

        Kwargs:
            type (str) - The type of factor to be enrolled (sms or totp)
            totp_issuer (str) - Name of the Organization
            totp_user (str) - email of user
            phone_number (str) - phone number of the user

        Returns: Dict containing the authentication factor information.
        """

        params = {
            "type": type,
            "totp_issuer": totp_issuer,
            "totp_user": totp_user,
            "phone_number": phone_number,
        }

        if type is None:
            raise ValueError("Incomplete arguments. Need to specify a type of factor")

        if type is not "sms" and type is not "totp":
            raise ValueError("Type parameter must be either 'sms' or 'totp'")

        if (
            type is "totp"
            and totp_issuer is None
            or type is "totp"
            and totp_user is None
        ):
            raise ValueError(
                "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp"
            )

        if type is "sms" and phone_number is None:
            raise ValueError(
                "Incomplete arguments. Need to specify phone_number when type is sms"
            )

        return self.request_helper.request(
            ENROLL_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

    def challenge_factor(
        self, authentication_factor_id=None, sms_template=None,
    ):

        """
        Initiates the authentication process for the newly created MFA authorization factor, referred to as a challenge.

        Kwargs:
            authentication_factor_id (str) - ID of the authorization factor
            sms_template (str) - Optional parameter to customize the message for sms type factors. Must include "{{code}}" if used.

        Returns: Dict containing the authentication challenge factor details.
        """

        params = {
            "authentication_factor_id": authentication_factor_id,
            "sms_template": sms_template,
        }

        if authentication_factor_id is None:
            raise ValueError(
                "Incomplete arguments: 'authentication_factor_id' is a required parameter"
            )

        return self.request_helper.request(
            CHALLENGE_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

    def verify_factor(
        self, authentication_challenge_id=None, code=None,
    ):

        """
        Verifies the one time password provided by the end-user.

        Kwargs:
            authentication_challenge_id (str) - The ID of the authentication challenge that provided the user the verification code.
            code (str) - The verification code sent to and provided by the end user.

        Returns: Dict containing the  challenge factor details.
        """

        params = {
            "authentication_challenge_id": authentication_challenge_id,
            "code": code,
        }

        if authentication_challenge_id is None or code is None:
            raise ValueError(
                "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters"
            )

        return self.request_helper.request(
            VERIFY_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )
