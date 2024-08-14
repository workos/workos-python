from workos.types.workos_model import WorkOSModel
from workos.types.mfa.authentication_challenge import AuthenticationChallenge
from workos.types.mfa.authentication_factor import AuthenticationFactorTotpExtended


class AuthenticationFactorTotpAndChallengeResponse(WorkOSModel):
    """Representation of an authentication factor and authentication challenge response as returned by WorkOS through User Management features."""

    authentication_factor: AuthenticationFactorTotpExtended
    authentication_challenge: AuthenticationChallenge
