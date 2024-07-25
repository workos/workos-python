from typing import Any, TypeVar, Union
from typing_extensions import Annotated, LiteralString
from pydantic import (
    Field,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from workos.typing.untyped_literal import UntypedLiteral


def convert_unknown_literal_to_untyped_literal(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Union[LiteralString, UntypedLiteral]:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]["type"] == "literal_error":
            return handler(UntypedLiteral(value))
        else:
            return handler(value)


def allow_unknown_literal_value(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Union[LiteralString, UntypedLiteral]:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]["type"] == "literal_error" and isinstance(
            value, str
        ):
            return UntypedLiteral(value)
        else:
            return handler(value)


LiteralType = TypeVar("LiteralType", bound=LiteralString)
LiteralOrUntyped = Annotated[
    Annotated[Union[LiteralType, UntypedLiteral], Field(union_mode="left_to_right")],
    WrapValidator(convert_unknown_literal_to_untyped_literal),
]
PermissiveLiteral = Annotated[LiteralType, WrapValidator(allow_unknown_literal_value)]
