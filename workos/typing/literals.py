from enum import Enum
from typing import Annotated, Any, LiteralString, TypeVar, Union
from pydantic import Field, ValidationError, ValidationInfo, ValidatorFunctionWrapHandler, WrapValidator
from workos.typing.untyped_literal import UntypedLiteral
from workos.typing.untyped_value import UntypedValue


def convert_unknown_literal_to_untyped(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> LiteralString | UntypedValue:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return handler(UntypedValue(raw_value=value))
        else:
            return handler(value)


def convert_unknown_literal_to_untyped_literal(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> LiteralString | UntypedLiteral:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return handler(f"Untyped[{value}]")
        else:
            return handler(value)


def allow_unknown_literal_value(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> LiteralString | UntypedLiteral:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return value
        else:
            return handler(value)


LiteralType = TypeVar('LiteralType', bound=LiteralString)
SafeLiteral = Annotated[Annotated[Union[LiteralType, UntypedValue], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_literal_to_untyped)]

# It we take the path of a sentinel value, I think we should do something like this.
LiteralOrUntyped = Annotated[Annotated[Union[LiteralType, UntypedLiteral], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_literal_to_untyped_literal)]

PermissiveLiteral = Annotated[LiteralType,
                              WrapValidator(allow_unknown_literal_value)]
