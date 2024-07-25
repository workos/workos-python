from typing import Any
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler


class UntypedLiteral(str):
    def __new__(cls, value: str):
        return super().__new__(cls, f"Untyped[{value}]")

    @classmethod
    def validate_untyped_literal(cls, value: Any) -> Any:
        if isinstance(value, UntypedLiteral):
            return value
        else:
            # TODO: Should this raise an error that translates to pydantic's is_instance_of error?
            raise ValueError("Value is not an instance of UntypedLiteral")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(
            function=cls.validate_untyped_literal,
        )


# TypeGuard doesn't actually work for exhaustiveness checking, but we can return a boolean expression instead
# https://github.com/python/mypy/issues/15305
# TODO: see if there is a way to define this as TypeGuard, TypeIs, or bool depending on python version
# def is_untyped_literal(value: Union[str, UntypedLiteral]) -> TypeGuard[UntypedLiteral]:
#     return isinstance(value, UntypedLiteral)


def is_untyped_literal(value: Any) -> bool:
    # A helper to detect untyped values from the API (more explainer here)
    # Does not help with exhaustiveness checking
    return isinstance(value, UntypedLiteral)
