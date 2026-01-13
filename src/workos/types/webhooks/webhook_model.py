from typing import Generic
from workos.types.events.event_model import EventPayload
from workos.types.workos_model import WorkOSModel


class WebhookModel(WorkOSModel, Generic[EventPayload]):
    """Representation of an Webhook delivered via Webhook.
    Attributes:
        OBJECT_FIELDS (list): List of fields an Webhook is comprised of.
    """

    id: str
    data: EventPayload
    created_at: str
