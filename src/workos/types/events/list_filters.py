from typing import Optional, Sequence
from workos.types.events import EventType
from workos.types.list_resource import ListArgs


class EventsListFilters(ListArgs, total=False):
    events: Sequence[EventType]
    organization_id: Optional[str]
    range_start: Optional[str]
    range_end: Optional[str]
