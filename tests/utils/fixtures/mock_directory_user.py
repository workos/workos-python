import datetime
from workos.resources.base import WorkOSBaseResource


class MockDirectoryUser(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.idp_id = "idp_id_" + id
        self.directory_id = "directory_id"
        self.organization_id = "org_id_" + id
        self.first_name = "gsuite_directory"
        self.last_name = "fried chicken"
        self.job_title = "developer"
        self.emails = [
            {"primary": "true", "type": "work", "value": "marcelina@foo-corp.com"}
        ]
        self.username = None
        self.groups = None
        self.state = None
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.custom_attributes = None
        self.raw_attributes = {
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
                {"value": "marcelina@foo-corp.com", "type": "work", "primary": "true"}
            ],
        }
        self.object = "directory_user"

    OBJECT_FIELDS = [
        "id",
        "idp_id",
        "directory_id",
        "organization_id",
        "first_name",
        "last_name",
        "job_title",
        "emails",
        "username",
        "groups",
        "state",
        "created_at",
        "updated_at",
        "custom_attributes",
        "raw_attributes",
        "object",
    ]
