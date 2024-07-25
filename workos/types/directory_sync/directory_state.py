from typing import Any, Literal
from pydantic import BeforeValidator, ValidationInfo
from typing_extensions import Annotated


ApiDirectoryState = Literal[
    "active",
    "unlinked",
    "validating",
    "deleting",
    "invalid_credentials",
]


def convert_linked_to_active(value: Any, info: ValidationInfo) -> Any:
    if isinstance(value, str) and value == "linked":
        return "active"
    else:
        return value


DirectoryState = Annotated[
    ApiDirectoryState,
    BeforeValidator(convert_linked_to_active),
]
