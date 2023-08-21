import datetime
from workos.resources.base import WorkOSBaseResource


class MockSession(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.token = "session_token_123abc"
        self.authorized_organizations = [
            {
                "organization": {
                    "id": "org_01E4ZCR3C56J083X43JQXF3JK5",
                    "name": "Foo Corp",
                }
            }
        ]
        self.unauthorized_organizations = [
            {
                "organization": {
                    "id": "org_01H7BA9A1YY5RGBTP1HYKVJPNC",
                    "name": "Bar Corp",
                },
                "reasons": [
                    {
                        "type": "authentication_method_required",
                        "allowed_authentication_methods": ["GoogleOauth"],
                    }
                ],
            }
        ]
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "token",
        "authorized_organizations",
        "unauthorized_organizations",
        "created_at",
        "updated_at",
    ]
