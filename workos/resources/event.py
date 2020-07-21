from workos.resources.base import WorkOSBaseResource
from workos.resources.event_action import WorkOSEventAction


class WorkOSEvent(WorkOSBaseResource):
    """Representation of an Event as returned by WorkOS through the Audit Trail feature.
    
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSEvent is comprised of.
    """

    OBJECT_FIELDS = [
        "id",
        "group",
        "location",
        "latitude",
        "longitude",
        "type",
        "actor_name",
        "actor_id",
        "target_name",
        "target_id",
        "metadata",
        "occurred_at",
    ]

    @classmethod
    def construct_from_response(cls, response):
        event = super(WorkOSEvent, cls).construct_from_response(response)

        event_action = WorkOSEventAction.construct_from_response(response["action"])
        event.action = event_action

        return event

    def to_dict(self):
        event_dict = super(WorkOSEvent, self).to_dict()

        event_action_dict = self.action.to_dict()
        event_dict["action"] = event_action_dict

        return event_dict
