from typing import Any, Dict, Union
from typing_extensions import Annotated
from pydantic import Field, TypeAdapter
from workos.types.webhooks.webhook import Webhook
from workos.types.workos_model import WorkOSModel


# Fall back to untyped Webhook if the event type is not recognized
class UntypedWebhook(WorkOSModel):
    id: str
    event: str
    data: Dict[str, Any]
    created_at: str


WebhookTypeAdapter: TypeAdapter[Webhook] = TypeAdapter(
    Annotated[Union[Webhook, UntypedWebhook], Field(union_mode="left_to_right")],
)
