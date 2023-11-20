import datetime
from workos.resources.base import WorkOSBaseResource


class MockAuthFactorTotp(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "authentication_factor"
        self.id = id
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.type = "totp"
        self.totp = {
            "qr_code": "data:image/png;base64,{base64EncodedPng}",
            "secret": "NAGCCFS3EYRB422HNAKAKY3XDUORMSRF",
            "uri": "otpauth://totp/FooCorp:alan.turing@foo-corp.com?secret=NAGCCFS3EYRB422HNAKAKY3XDUORMSRF&issuer=FooCorp",
        }

    OBJECT_FIELDS = [
        "object",
        "id",
        "created_at",
        "updated_at",
        "type",
        "totp",
    ]
