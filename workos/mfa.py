from warnings import warn
import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
)
from workos.utils.validation import MFA_MODULE, validate_settings
from workos.resources.mfa import (
    WorkOSAuthenticationFactorSms,
    WorkOSAuthenticationFactorTotp,
    WorkOSChallenge,
    WorkOSChallengeVerification,
)


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
        self,
        type=None,
        totp_issuer=None,
        totp_user=None,
        phone_number=None,
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

        if type not in ["sms", "totp"]:
            raise ValueError("Type parameter must be either 'sms' or 'totp'")

        if (
            type == "totp"
            and totp_issuer is None
            or type == "totp"
            and totp_user is None
        ):
            raise ValueError(
                "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp"
            )

        if type == "sms" and phone_number is None:
            raise ValueError(
                "Incomplete arguments. Need to specify phone_number when type is sms"
            )

        response = self.request_helper.request(
            "auth/factors/enroll",
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        if type == "totp":
            return WorkOSAuthenticationFactorTotp.construct_from_response(
                response
            ).to_dict()

        return WorkOSAuthenticationFactorSms.construct_from_response(response).to_dict()

    def get_factor(
        self,
        authentication_factor_id=None,
    ):
        """
        Returns an authorization factor from its ID.

        Kwargs:
            authentication_factor_id (str) - The ID of the factor to be obtained.

        Returns: Dict containing the authentication factor information.
        """

        if authentication_factor_id is None:
            raise ValueError("Incomplete arguments. Need to specify a factor ID")

        response = self.request_helper.request(
            self.request_helper.build_parameterized_url(
                "auth/factors/{authentication_factor_id}",
                authentication_factor_id=authentication_factor_id,
            ),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        if response["type"] == "totp":
            return WorkOSAuthenticationFactorTotp.construct_from_response(
                response
            ).to_dict()

        return WorkOSAuthenticationFactorSms.construct_from_response(response).to_dict()

    def delete_factor(
        self,
        authentication_factor_id=None,
    ):
        """
        Deletes an MFA authorization factor.

        Kwargs:
            authentication_factor_id (str) - The ID of the authorization factor to be deleted.

        Returns: Does not provide a response.
        """

        if authentication_factor_id is None:
            raise ValueError("Incomplete arguments. Need to specify a factor ID.")

        return self.request_helper.request(
            self.request_helper.build_parameterized_url(
                "auth/factors/{authentication_factor_id}",
                authentication_factor_id=authentication_factor_id,
            ),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )

    def challenge_factor(
        self,
        authentication_factor_id=None,
        sms_template=None,
    ):
        """
        Initiates the authentication process for the newly created MFA authorization factor, referred to as a challenge.

        Kwargs:
            authentication_factor_id (str) - ID of the authorization factor
            sms_template (str) - Optional parameter to customize the message for sms type factors. Must include "{{code}}" if used.

        Returns: Dict containing the authentication challenge factor details.
        """

        params = {
            "sms_template": sms_template,
        }

        if authentication_factor_id is None:
            raise ValueError(
                "Incomplete arguments: 'authentication_factor_id' is a required parameter"
            )

        response = self.request_helper.request(
            self.request_helper.build_parameterized_url(
                "auth/factors/{factor_id}/challenge", factor_id=authentication_factor_id
            ),
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        return WorkOSChallenge.construct_from_response(response).to_dict()

    def verify_factor(
        self,
        authentication_challenge_id=None,
        code=None,
    ):
        """
        Verifies the one time password provided by the end-user.

        Deprecated: Please use `verify_challenge` instead.

        Kwargs:
            authentication_challenge_id (str) - The ID of the authentication challenge that provided the user the verification code.
            code (str) - The verification code sent to and provided by the end user.

        Returns: Dict containing the  challenge factor details.
        """

        warn(
            "'verify_factor' is deprecated. Please use 'verify_challenge' instead.",
            DeprecationWarning,
        )

        return self.verify_challenge(authentication_challenge_id, code)

    def verify_challenge(
        self,
        authentication_challenge_id=None,
        code=None,
    ):
        """
        Verifies the one time password provided by the end-user.

        Kwargs:
            authentication_challenge_id (str) - The ID of the authentication challenge that provided the user the verification code.
            code (str) - The verification code sent to and provided by the end user.

        Returns: Dict containing the  challenge factor details.
        """

        params = {
            "code": code,
        }

        if authentication_challenge_id is None or code is None:
            raise ValueError(
                "Incomplete arguments: 'authentication_challenge_id' and 'code' are required parameters"
            )

        response = self.request_helper.request(
            self.request_helper.build_parameterized_url(
                "auth/challenges/{challenge_id}/verify",
                challenge_id=authentication_challenge_id,
            ),
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        return WorkOSChallengeVerification.construct_from_response(response).to_dict()
