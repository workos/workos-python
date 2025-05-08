from typing import Sequence, Annotated, Union, Any, Dict

from pydantic import BeforeValidator
from pydantic_core.core_schema import ValidationInfo

from workos.types.workos_model import WorkOSModel


class FGABaseWarning(WorkOSModel):
    code: str
    message: str


class MissingContextKeysWarning(FGABaseWarning):
    keys: Sequence[str]


def fga_warning_dispatch_validator(
    value: Dict[str, Any], info: ValidationInfo
) -> FGABaseWarning:
    if value.get("code") == "missing_context_keys":
        return MissingContextKeysWarning.model_validate(value)
    return FGABaseWarning.model_validate(value)


FGAWarning = Annotated[
    Union[MissingContextKeysWarning, FGABaseWarning],
    BeforeValidator(fga_warning_dispatch_validator),
]
