from typing import Optional, Protocol

from workos.types.mfa.enroll_authentication_factor_type import (
    EnrollAuthenticationFactorType,
)
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import (
    REQUEST_METHOD_POST,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    RequestHelper,
)
from workos.types.mfa import (
    AuthenticationChallenge,
    AuthenticationChallengeVerificationResponse,
    AuthenticationFactor,
    AuthenticationFactorExtended,
    AuthenticationFactorSms,
    AuthenticationFactorTotp,
    AuthenticationFactorTotpExtended,
)


class MFAModule(Protocol):
    """Offers methods through the WorkOS MFA service."""

    def enroll_factor(
        self,
        *,
        type: EnrollAuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> AuthenticationFactorExtended:
        """
        Defines the type of MFA authorization factor to be used. Possible values are sms or totp.

        Kwargs:
            type (str): The type of factor to be enrolled (sms or totp).
            totp_issuer (str): Name of the Organization. Required when type is totp, ignored otherwise.
            totp_user (str): email of user. Required when type is totp, ignored otherwise.
            phone_number (str): phone number of the user. (Optional)

        Returns:
            AuthenticationFactor:
        """
        ...

    def get_factor(self, authentication_factor_id: str) -> AuthenticationFactor:
        """
        Returns an authorization factor from its ID.

        Args:
            authentication_factor_id (str): The ID of the factor to be obtained.

        Returns:
            AuthenticationFactor: AuthenticationFactor response from WorkOS.
        """
        ...

    def delete_factor(self, authentication_factor_id: str) -> None:
        """
        Deletes an MFA authorization factor.

        Args:
            authentication_factor_id (str): The ID of the authorization factor to be deleted.

        Returns:
            None
        """
        ...

    def challenge_factor(
        self, *, authentication_factor_id: str, sms_template: Optional[str] = None
    ) -> AuthenticationChallenge:
        """
        Initiates the authentication process for the newly created MFA authorization factor, referred to as a challenge.

        Kwargs:
            authentication_factor_id (str): ID of the authorization factor
            sms_template (str): Optional parameter to customize the message for sms type factors. Must include "{{code}}" if used. (Optional)

        Returns:
            AuthenticationChallenge: AuthenticationChallenge response from WorkOS.
        """
        ...

    def verify_challenge(
        self, *, authentication_challenge_id: str, code: str
    ) -> AuthenticationChallengeVerificationResponse:
        """
        Verifies the one time password provided by the end-user.

        Kwargs:
            authentication_challenge_id (str): The ID of the authentication challenge that provided the user the verification code.
            code (str): The verification code sent to and provided by the end user.

        Returns:
            AuthenticationChallengeVerificationResponse: AuthenticationChallengeVerificationResponse response from WorkOS.
        """
        ...


class Mfa(MFAModule):
    """Methods to assist in creating, challenging, and verifying Authentication Factors through the WorkOS MFA service."""

    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def enroll_factor(
        self,
        *,
        type: EnrollAuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> AuthenticationFactorExtended:
        json = {
            "type": type,
            "totp_issuer": totp_issuer,
            "totp_user": totp_user,
            "phone_number": phone_number,
        }

        if type == "totp" and (totp_issuer is None or totp_user is None):
            raise ValueError(
                "Incomplete arguments. Need to specify both totp_issuer and totp_user when type is totp"
            )

        if type == "sms" and phone_number is None:
            raise ValueError(
                "Incomplete arguments. Need to specify phone_number when type is sms"
            )

        response = self._http_client.request(
            "auth/factors/enroll", method=REQUEST_METHOD_POST, json=json
        )

        if type == "totp":
            return AuthenticationFactorTotpExtended.model_validate(response)

        return AuthenticationFactorSms.model_validate(response)

    def get_factor(self, authentication_factor_id: str) -> AuthenticationFactor:
        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/factors/{authentication_factor_id}",
                authentication_factor_id=authentication_factor_id,
            ),
            method=REQUEST_METHOD_GET,
        )

        if response["type"] == "totp":
            return AuthenticationFactorTotp.model_validate(response)

        return AuthenticationFactorSms.model_validate(response)

    def delete_factor(self, authentication_factor_id: str) -> None:
        self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/factors/{authentication_factor_id}",
                authentication_factor_id=authentication_factor_id,
            ),
            method=REQUEST_METHOD_DELETE,
        )

    def challenge_factor(
        self,
        *,
        authentication_factor_id: str,
        sms_template: Optional[str] = None,
    ) -> AuthenticationChallenge:
        json = {
            "sms_template": sms_template,
        }

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/factors/{factor_id}/challenge", factor_id=authentication_factor_id
            ),
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AuthenticationChallenge.model_validate(response)

    def verify_challenge(
        self, *, authentication_challenge_id: str, code: str
    ) -> AuthenticationChallengeVerificationResponse:
        json = {
            "code": code,
        }

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/challenges/{challenge_id}/verify",
                challenge_id=authentication_challenge_id,
            ),
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AuthenticationChallengeVerificationResponse.model_validate(response)
