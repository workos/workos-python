from workos.resources.base import WorkOSBaseResource
from workos.resources.event_action import WorkOSEventAction


class WorkOSAuditLogExport(WorkOSBaseResource):
    """Representation of an export as returned by WorkOS through the Audit Logs Create/Get Export feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSAuditLogsEvent is comprised of.
    """

    OBJECT_FIELDS = [
        "id",
        "object",
        "state",
        "url",
        "created_at",
        "updated_at",
    ]

    @classmethod
    def construct_from_response(cls, response):
        export = super(WorkOSAuditLogExport, cls).construct_from_response(response)
        return export

    def to_dict(self):
        export_dict = super(WorkOSAuditLogExport, self).to_dict()
        return export_dict
