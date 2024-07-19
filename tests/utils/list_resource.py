from typing import Dict, List, Optional, TypeVar, TypedDict, Union
from workos.resources.list import ListPage, WorkOsListResource


def list_data_to_dicts(listResource: WorkOsListResource):
    return list(map(lambda x: x.dict(), listResource.data))


def list_resource_of(
    data=[Dict], before: Optional[str] = None, after: Optional[str] = None
):
    return {
        "object": "list",
        "data": data,
        "list_metadata": {"before": before, "after": after},
    }
