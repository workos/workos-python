import workos
from workos.resources.base import WorkOSBaseResource


class WorkOSDirectory(WorkOSBaseResource):
    """Representation of a Directory Response as returned by WorkOS through the Directory Sync feature.
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSConnection is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "domain",
        "name",
        "organization_id",
        "state",
        "type",
        "created_at",
        "updated_at",
    ]

    @classmethod
    def construct_from_response(cls, response):
        connection_response = super(WorkOSDirectory, cls).construct_from_response(
            response
        )

        return connection_response

    def to_dict(self):
        connection_response_dict = super(WorkOSDirectory, self).to_dict()

        return connection_response_dict


class WorkOSDirectoryGroup(WorkOSBaseResource):
    """Representation of a Directory Group as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryGroup is comprised of.
    """

    OBJECT_FIELDS = [
        "id",
        "idp_id",
        "directory_id",
        "name",
        "created_at",
        "updated_at",
        "raw_attributes",
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSDirectoryGroup, cls).construct_from_response(response)

    def to_dict(self):
        directory_group = super(WorkOSDirectoryGroup, self).to_dict()

        return directory_group


class WorkOSDirectoryUser(WorkOSBaseResource):
    """Representation of a Directory User as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryUser is comprised of.
    """

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
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSDirectoryUser, cls).construct_from_response(response)

    def to_dict(self):
        directory_group = super(WorkOSDirectoryUser, self).to_dict()

        return directory_group

    def primary_email(self):
        self_dict = self.to_dict()
        return next((email for email in self_dict["emails"] if email["primary"]), None)


class WorkOSDirectoryList(WorkOSBaseResource):
    """Representation of a Directory List as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryList is comprised of.
    """

    OBJECT_FIELDS = [
        "data",
        "list_metadata",
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSDirectoryList, cls).construct_from_response(response)

    def to_dict(self):
        response = super(WorkOSDirectoryList, self).to_dict()
        return response

    def auto_paging_iter(self):
        directories = self.to_dict()["data"]
        before = self.to_dict()["list_metadata"]["before"]

        while before is not None:
            response = workos.client.directory_sync.list_directories(
                limit=100, before=before
            )
            for i in response["data"]:
                directories.append(i)
            before = response["list_metadata"]["before"]

        return directories


class WorkOSDirectoryUserList(WorkOSBaseResource):
    """Representation of a Directory List as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryList is comprised of.
    """

    OBJECT_FIELDS = [
        "data",
        "list_metadata",
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSDirectoryUserList, cls).construct_from_response(response)

    def to_dict(self):
        response = super(WorkOSDirectoryUserList, self).to_dict()
        return response

    def auto_paging_iter(self):
        directory = self.to_dict()["data"][0]["directory_id"]
        users = self.to_dict()["data"]
        before = self.to_dict()["list_metadata"]["before"]

        while before is not None:
            response = workos.client.directory_sync.list_users(
                directory=directory, limit=100, before=before
            )
            for i in response["data"]:
                users.append(i)
            before = response["list_metadata"]["before"]

        return users


class WorkOSDirectoryGroupList(WorkOSBaseResource):
    """Representation of a Directory List as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryList is comprised of.
    """

    OBJECT_FIELDS = [
        "data",
        "list_metadata",
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSDirectoryGroupList, cls).construct_from_response(response)

    def to_dict(self):
        response = super(WorkOSDirectoryGroupList, self).to_dict()
        return response

    def auto_paging_iter(self):
        print(self.to_dict())
        directory = self.to_dict()["data"][0]["directory_id"]
        groups = self.to_dict()["data"]
        before = self.to_dict()["list_metadata"]["before"]

        while before is not None:
            response = workos.client.directory_sync.list_groups(
                directory=directory, limit=100, before=before
            )
            for i in response["data"]:
                groups.append(i)
            before = response["list_metadata"]["before"]

        return groups
