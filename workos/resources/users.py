from workos.resources.base import WorkOSBaseResource


class WorkOSUser(WorkOSBaseResource):
    """Representation of a User as returned by WorkOS through User Management features.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSUser comprises.
    """

    OBJECT_FIELDS = [
        "id",
        "email",
        "first_name",
        "last_name",
        "email_verified",
        "created_at",
        "updated_at",
    ]
