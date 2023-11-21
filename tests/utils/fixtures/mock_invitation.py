import datetime
from workos.resources.base import WorkOSBaseResource


class MockInvitation(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.email = "marcelina@foo-corp.com"
        self.state = "pending"
        self.accepted_at = None
        self.revoked_at = None
        self.expires_at = datetime.datetime.now()
        self.token = "ABCDE12345"
        self.organization_id = "org_12345"
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "email",
        "state",
        "accepted_at",
        "revoked_at",
        "expires_at",
        "token",
        "organization_id",
        "created_at",
        "updated_at",
    ]
