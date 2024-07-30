import datetime

from workos.resources.directory_sync import DirectoryUserWithGroups
from workos.types.directory_sync.directory_user import DirectoryUserEmail, InlineRole


class MockDirectoryUser(DirectoryUserWithGroups):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="directory_user",
            id=id,
            idp_id="idp_id_" + id,
            directory_id="directory_id",
            organization_id="org_id_" + id,
            first_name="gsuite_directory",
            last_name="fried chicken",
            job_title="developer",
            emails=[
                DirectoryUserEmail(
                    primary=True, type="work", value="marcelina@foo-corp.com"
                )
            ],
            username=None,
            groups=[],
            state="active",
            created_at=now,
            updated_at=now,
            custom_attributes={},
            raw_attributes={
                "schemas": ["urn:scim:schemas:core:1.0"],
                "name": {"familyName": "Seri", "givenName": "Marcelina"},
                "externalId": "external-id",
                "locale": "en_US",
                "userName": "marcelina@foo-corp.com",
                "id": "directory_usr_id",
                "displayName": "Marcelina Seri",
                "title": "developer",
                "active": True,
                "groups": [],
                "meta": None,
                "emails": [
                    {
                        "value": "marcelina@foo-corp.com",
                        "type": "work",
                        "primary": "true",
                    }
                ],
            },
            role=InlineRole(slug="member"),
        )
