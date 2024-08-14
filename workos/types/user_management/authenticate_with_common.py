from typing import Literal, Union
from typing_extensions import TypedDict


class AuthenticateWithBaseParameters(TypedDict):
    ip_address: Union[str, None]
    user_agent: Union[str, None]


class AuthenticateWithPasswordParameters(AuthenticateWithBaseParameters):
    email: str
    password: str
    grant_type: Literal["password"]


class AuthenticateWithCodeParameters(AuthenticateWithBaseParameters):
    code: str
    code_verifier: Union[str, None]
    grant_type: Literal["authorization_code"]


class AuthenticateWithMagicAuthParameters(AuthenticateWithBaseParameters):
    code: str
    email: str
    link_authorization_code: Union[str, None]
    grant_type: Literal["urn:workos:oauth:grant-type:magic-auth:code"]


class AuthenticateWithEmailVerificationParameters(AuthenticateWithBaseParameters):
    code: str
    pending_authentication_token: str
    grant_type: Literal["urn:workos:oauth:grant-type:email-verification:code"]


class AuthenticateWithTotpParameters(AuthenticateWithBaseParameters):
    code: str
    authentication_challenge_id: str
    pending_authentication_token: str
    grant_type: Literal["urn:workos:oauth:grant-type:mfa-totp"]


class AuthenticateWithOrganizationSelectionParameters(AuthenticateWithBaseParameters):
    organization_id: str
    pending_authentication_token: str
    grant_type: Literal["urn:workos:oauth:grant-type:organization-selection"]


class AuthenticateWithRefreshTokenParameters(AuthenticateWithBaseParameters):
    refresh_token: str
    organization_id: Union[str, None]
    grant_type: Literal["refresh_token"]


AuthenticateWithParameters = Union[
    AuthenticateWithPasswordParameters,
    AuthenticateWithCodeParameters,
    AuthenticateWithMagicAuthParameters,
    AuthenticateWithEmailVerificationParameters,
    AuthenticateWithTotpParameters,
    AuthenticateWithOrganizationSelectionParameters,
    AuthenticateWithRefreshTokenParameters,
]
