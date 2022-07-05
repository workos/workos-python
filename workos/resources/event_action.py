from workos.resources.base import WorkOSBaseResource


class WorkOSEventAction(WorkOSBaseResource):
    """Representation of an Event Action as returned by WorkOS through the Audit Trail feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSEventAction is comprised of.
    """

    OBJECT_FIELDS = ["id", "name"]
