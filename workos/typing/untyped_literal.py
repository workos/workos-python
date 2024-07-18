from typing import Any
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler


class UntypedLiteral(str):
    def __new__(cls, value: str):
        return super().__new__(cls, f"Untyped[{value}]")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # TODO: should this handler check that the incoming value is an instance of UntypedLiteral?
        return core_schema.no_info_after_validator_function(cls, handler(str))


# TypeGuard doesn't actually work for exhaustiveness checking, but we can return a boolean expression instead
# TODO: see if there is a way to define this as TypeGuard, TypeIs, or bool depending on python version
# def is_untyped_literal(value: str | UntypedLiteral) -> TypeGuard[UntypedLiteral]:
#     return isinstance(value, UntypedLiteral)


def is_untyped_literal(value: Any) -> bool:
    # A helper to detect untyped values from the API (more explainer here)
    # Does not help with exhaustiveness checking
    return isinstance(value, UntypedLiteral)
