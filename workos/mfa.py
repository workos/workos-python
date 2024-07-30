from typing import Optional, Protocol

import workos
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import (
    REQUEST_METHOD_POST,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    RequestHelper,
)
from workos.utils.validation import MFA_MODULE, validate_settings
from workos.resources.mfa import (
    AuthenticationChallenge,
    AuthenticationChallengeVerificationResponse,
    AuthenticationFactor,
    AuthenticationFactorSms,
    AuthenticationFactorTotp,
    EnrollAuthenticationFactorType,
)


class MFAModule(Protocol):
    def enroll_factor(
        self,
        type: EnrollAuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> AuthenticationFactor: ...

    def get_factor(self, authentication_factor_id: str) -> AuthenticationFactor: ...

    def delete_factor(self, authentication_factor_id: str) -> None: ...

    def challenge_factor(
        self, authentication_factor_id: str, sms_template: Optional[str] = None
    ) -> AuthenticationChallenge: ...

    def verify_challenge(
        self, authentication_challenge_id: str, code: str
    ) -> AuthenticationChallengeVerificationResponse: ...


class Mfa(MFAModule):
    """Methods to assist in creating, challenging, and verifying Authentication Factors through the WorkOS MFA service."""

    _http_client: SyncHTTPClient

    @validate_settings(MFA_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def enroll_factor(
        self,
        type: EnrollAuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> AuthenticationFactor:
        """
        Defines the type of MFA authorization factor to be used. Possible values are sms or totp.

        Kwargs:
            type (str) - The type of factor to be enrolled (sms or totp)
            totp_issuer (str) - Name of the Organization
            totp_user (str) - email of user
            phone_number (str) - phone number of the user

        Returns: AuthenticationFactor
        """

        params = {
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
            "auth/factors/enroll",
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        if type == "totp":
            return AuthenticationFactorTotp.model_validate(response)

        return AuthenticationFactorSms.model_validate(response)

    def get_factor(self, authentication_factor_id: str) -> AuthenticationFactor:
        """
        Returns an authorization factor from its ID.

        Kwargs:
            authentication_factor_id (str) - The ID of the factor to be obtained.

        Returns: Dict containing the authentication factor information.
        """

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/factors/{authentication_factor_id}",
                authentication_factor_id=authentication_factor_id,
            ),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        if response["type"] == "totp":
            return AuthenticationFactorTotp.model_validate(response)

        return AuthenticationFactorSms.model_validate(response)

    def delete_factor(self, authentication_factor_id: str) -> None:
        """
        Deletes an MFA authorization factor.

        Kwargs:
            authentication_factor_id (str) - The ID of the authorization factor to be deleted.

        Returns: Does not provide a response.
        """

        self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/factors/{authentication_factor_id}",
                authentication_factor_id=authentication_factor_id,
            ),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )

    def challenge_factor(
        self,
        authentication_factor_id: str,
        sms_template: Optional[str] = None,
    ) -> AuthenticationChallenge:
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

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/factors/{factor_id}/challenge", factor_id=authentication_factor_id
            ),
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        return AuthenticationChallenge.model_validate(response)

    def verify_challenge(
        self, authentication_challenge_id: str, code: str
    ) -> AuthenticationChallengeVerificationResponse:
        """
        Verifies the one time password provided by the end-user.

        Kwargs:
            authentication_challenge_id (str) - The ID of the authentication challenge that provided the user the verification code.
            code (str) - The verification code sent to and provided by the end user.

        Returns: AuthenticationChallengeVerificationResponse containing the challenge factor details.
        """

        params = {
            "code": code,
        }

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "auth/challenges/{challenge_id}/verify",
                challenge_id=authentication_challenge_id,
            ),
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        return AuthenticationChallengeVerificationResponse.model_validate(response)
