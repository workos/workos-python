import datetime
from workos.resources.base import WorkOSBaseResource


class MockInvitation(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "invitation"
        self.id = id
        self.email = "marcelina@foo-corp.com"
        self.state = "pending"
        self.accepted_at = None
        self.revoked_at = None
        self.expires_at = now
        self.token = "Z1uX3RbwcIl5fIGJJJCXXisdI"
        self.accept_invitation_url = (
            "https://your-app.com/invite?invitation_token=Z1uX3RbwcIl5fIGJJJCXXisdI"
        )
        self.organization_id = "org_12345"
        self.inviter_user_id = "user_123"
        self.created_at = now
        self.updated_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "email",
        "state",
        "accepted_at",
        "revoked_at",
        "expires_at",
        "token",
        "accept_invitation_url",
        "organization_id",
        "inviter_user_id",
        "created_at",
        "updated_at",
    ]
