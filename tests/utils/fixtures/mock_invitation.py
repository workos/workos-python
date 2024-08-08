import datetime

from workos.types.user_management import Invitation


class MockInvitation(Invitation):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="invitation",
            id=id,
            email="marcelina@foo-corp.com",
            state="pending",
            accepted_at=None,
            revoked_at=None,
            expires_at=now,
            token="Z1uX3RbwcIl5fIGJJJCXXisdI",
            accept_invitation_url="https://your-app.com/invite?invitation_token=Z1uX3RbwcIl5fIGJJJCXXisdI",
            organization_id="org_12345",
            inviter_user_id="user_123",
            created_at=now,
            updated_at=now,
        )
