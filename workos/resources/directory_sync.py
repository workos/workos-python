from workos.resources.base import WorkOSBaseResource


class WorkOSDirectoryGroup(WorkOSBaseResource):
    """Representation of a User Profile as returned by WorkOS through the SSO feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSProfile is comprised of.
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
