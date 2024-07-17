from enum import Enum
from typing import Annotated, Any, TypeVar, Union

from pydantic import Field, ValidationError, ValidationInfo, ValidatorFunctionWrapHandler, WrapValidator

from workos.typing.literals import LiteralType
from workos.typing.untyped_literal import UntypedLiteral
from workos.typing.untyped_value import UntypedValue


EnumType = TypeVar('EnumType', bound=Enum)

# This is identical to the string literals approach, but handles literal enums. Maybe the types can be unified?


def convert_unknown_enum_to_untyped_value(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Enum:  # TODO: can I make this a generic?
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'enum':
            return handler(UntypedValue(raw_value=value))
        else:
            return handler(value)


def convert_unknown_enum_to_untyped_literal(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Enum | str:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return handler(f"Untyped[{value}]")
        else:
            return handler(value)


def allow_unknown_enum_value(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Enum:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return value
        else:
            return handler(value)


SafeEnum = Annotated[Annotated[Union[EnumType, UntypedValue], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_enum_to_untyped_value)]

# It we take the path of a sentinel value, I think we should do something like this.
EnumOrUntyped = Annotated[Annotated[Union[EnumType, UntypedLiteral], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_enum_to_untyped_literal)]

PermissiveEnum = Annotated[EnumType, WrapValidator(allow_unknown_enum_value)]
