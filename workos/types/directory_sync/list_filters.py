from typing import Optional
from workos.types.list_resource import ListArgs


class DirectoryListFilters(ListArgs, total=False):
    search: Optional[str]
    organization_id: Optional[str]
    domain: Optional[str]


class DirectoryUserListFilters(
    ListArgs,
    total=False,
):
    group: Optional[str]
    directory: Optional[str]


class DirectoryGroupListFilters(ListArgs, total=False):
    user: Optional[str]
    directory: Optional[str]
