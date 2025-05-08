from typing import Sequence, Union, Any, Dict, Literal
from typing_extensions import Annotated

from pydantic import BeforeValidator
from pydantic_core.core_schema import ValidationInfo

from workos.types.workos_model import WorkOSModel


class FGABaseWarning(WorkOSModel):
    code: str
    message: str


class MissingContextKeysWarning(FGABaseWarning):
    code: Literal["missing_context_keys"]
    keys: Sequence[str]


def fga_warning_dispatch_validator(
    value: Dict[str, Any], info: ValidationInfo
) -> FGABaseWarning:
    if value.get("code") == "missing_context_keys":
        return MissingContextKeysWarning.model_validate(value)

    # Fallback to the base warning model
    return FGABaseWarning.model_validate(value)


FGAWarning = Annotated[
    Union[MissingContextKeysWarning, FGABaseWarning],
    BeforeValidator(fga_warning_dispatch_validator),
]
