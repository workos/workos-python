from workos.resources.base import WorkOSBaseResource


class WorkOSMagicAuthChallenge(WorkOSBaseResource):
    """Representation of a MagicAuthChallenge identifier as returned by WorkOS through User Management features.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSMagicAuthChallenge comprises.
    """

    OBJECT_FIELDS = [
        "id",
    ]
