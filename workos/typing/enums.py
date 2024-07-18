from enum import Enum
from typing import Annotated, Any, TypeVar, Union
from pydantic import Field, ValidationError, ValidationInfo, ValidatorFunctionWrapHandler, WrapValidator
from workos.typing.untyped_literal import UntypedLiteral


EnumType = TypeVar('EnumType', bound=Enum)

# Identical to the literal or strings path, except meant for a literal of enum values.


def convert_unknown_enum_to_untyped_literal(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Enum | UntypedLiteral:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return handler(UntypedLiteral(value))
        else:
            return handler(value)


def allow_unknown_enum_value(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Enum | str:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return value
        else:
            return handler(value)


EnumOrUntyped = Annotated[Annotated[Union[EnumType, UntypedLiteral], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_enum_to_untyped_literal)]

PermissiveEnum = Annotated[EnumType, WrapValidator(allow_unknown_enum_value)]
