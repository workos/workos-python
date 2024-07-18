from enum import Enum
import re
from typing import Annotated, Any, LiteralString, TypeGuard, TypeVar, Union
from pydantic_core import CoreSchema, core_schema
from typing_extensions import TypeIs
from pydantic import Field, GetCoreSchemaHandler, ValidationError, ValidationInfo, ValidatorFunctionWrapHandler, WrapValidator, model_validator, validate_call
from workos.typing.untyped_literal import UntypedLiteral

# Identical to the enums approach, except typed for a literal of string.


def convert_unknown_literal_to_untyped_literal(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> LiteralString | UntypedLiteral:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return handler(UntypedLiteral(value))
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
LiteralOrUntyped = Annotated[Annotated[Union[LiteralType, UntypedLiteral], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_literal_to_untyped_literal)]
PermissiveLiteral = Annotated[LiteralType,
                              WrapValidator(allow_unknown_literal_value)]
