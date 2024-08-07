from typing import Optional, Sequence
from workos.resources.events import EventType
from workos.resources.list import ListArgs


class EventsListFilters(ListArgs, total=False):
    events: Sequence[EventType]
    organization_id: Optional[str]
    range_start: Optional[str]
    range_end: Optional[str]
