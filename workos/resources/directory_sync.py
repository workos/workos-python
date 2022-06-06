from workos.resources.base import WorkOSBaseResource


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
