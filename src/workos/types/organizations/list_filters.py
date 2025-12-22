from typing import Optional, Sequence
from workos.types.list_resource import ListArgs


class OrganizationListFilters(ListArgs, total=False):
    domains: Optional[Sequence[str]]
