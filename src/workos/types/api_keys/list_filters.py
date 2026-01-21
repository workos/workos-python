from typing import Optional
from workos.types.list_resource import ListArgs


class ApiKeyListFilters(ListArgs, total=False):
    organization_id: Optional[str]
