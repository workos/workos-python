from workos.types.workos_model import WorkOSModel
from workos.types.mfa.authentication_challenge import AuthenticationChallenge


class AuthenticationChallengeVerificationResponse(WorkOSModel):
    """Representation of a WorkOS MFA Challenge Verification Response."""

    challenge: AuthenticationChallenge
    valid: bool
