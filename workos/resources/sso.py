from workos.resources.base import WorkOSBaseResource


class WorkOSProfile(WorkOSBaseResource):
    """Representation of a User Profile as returned by WorkOS through the SSO feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSProfile is comprised of.
    """

    OBJECT_FIELDS = [
        "id",
        "email",
        "first_name",
        "last_name",
        "connection_id",
        "connection_type",
        "idp_id",
        "raw_attributes",
    ]
