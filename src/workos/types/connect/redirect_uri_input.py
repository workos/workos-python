from typing import Optional

from typing_extensions import TypedDict


class RedirectUriInput(TypedDict, total=False):
    uri: str
    default: Optional[bool]
