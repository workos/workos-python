from typing import Optional, Sequence
from workos.resources.list import ListArgs


class OrganizationListFilters(ListArgs, total=False):
    domains: Optional[Sequence[str]]
