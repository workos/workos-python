from typing import Optional

from workos.types.list_resource import ListArgs


class ResourceListFilters(ListArgs, total=False):
    resource_type: Optional[str]
    search: Optional[str]


class WarrantListFilters(ListArgs, total=False):
    resource_type: Optional[str]
    resource_id: Optional[str]
    relation: Optional[str]
    subject_type: Optional[str]
    subject_id: Optional[str]
    subject_relation: Optional[str]
    warrant_token: Optional[str]
