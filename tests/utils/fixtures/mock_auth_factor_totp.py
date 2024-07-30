import datetime

from workos.resources.mfa import AuthenticationFactorTotp, ExtendedTotpFactor


class MockAuthenticationFactorTotp(AuthenticationFactorTotp):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="authentication_factor",
            id=id,
            created_at=now,
            updated_at=now,
            type="totp",
            user_id="user_123",
            totp=ExtendedTotpFactor(
                issuer="FooCorp",
                user="test@example.com",
                qr_code="data:image/png;base64,{base64EncodedPng}",
                secret="NAGCCFS3EYRB422HNAKAKY3XDUORMSRF",
                uri="otpauth://totp/FooCorp:alan.turing@foo-corp.com?secret=NAGCCFS3EYRB422HNAKAKY3XDUORMSRF&issuer=FooCorp",
            ),
        )
