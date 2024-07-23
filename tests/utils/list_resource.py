from typing import Dict, List, Optional


def list_data_to_dicts(list_data: List):
    return list(map(lambda x: x.dict(), list_data))


def list_response_of(
    data=[Dict], before: Optional[str] = None, after: Optional[str] = None
):
    return {
        "object": "list",
        "data": data,
        "list_metadata": {"before": before, "after": after},
    }
