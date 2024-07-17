from typing import Any
from typing_extensions import TypeIs
from pydantic import BaseModel


class UntypedValue(BaseModel):
    raw_value: Any


def is_untyped_value(value: Any) -> TypeIs[UntypedValue]:
    return isinstance(value, UntypedValue)
