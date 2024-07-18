import re
from typing import Annotated, Any, TypeGuard
from pydantic_core import CoreSchema, core_schema
from typing_extensions import TypeIs

from pydantic import Field, GetCoreSchemaHandler


class UntypedLiteral(str):
    def __new__(cls, value: str):
        return super().__new__(cls, f"Untyped[{value}]")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


def is_untyped_literal(value: Any) -> TypeIs[UntypedLiteral]:
    return isinstance(value, UntypedLiteral)
