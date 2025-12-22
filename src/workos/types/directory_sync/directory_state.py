from typing import Any, Literal
from pydantic import BeforeValidator, ValidationInfo
from typing_extensions import Annotated


ApiDirectoryState = Literal[
    "active",
    "inactive",
    "validating",
    "deleting",
    "invalid_credentials",
]


def convert_legacy_directory_state(value: Any, info: ValidationInfo) -> Any:
    if isinstance(value, str):
        if value == "linked":
            return "active"
        elif value == "unlinked":
            return "inactive"

    return value


DirectoryState = Annotated[
    ApiDirectoryState,
    BeforeValidator(convert_legacy_directory_state),
]
