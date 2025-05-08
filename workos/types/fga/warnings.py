from typing import Sequence, Union, Literal, Annotated

from pydantic import Field

from workos.types.workos_model import WorkOSModel


class FGABaseWarning(WorkOSModel):
    code: str
    message: str


class MissingContextKeysWarning(FGABaseWarning):
    code: Literal["missing_context_keys"]
    keys: Sequence[str]


FGAWarning = Annotated[
    Union[MissingContextKeysWarning, FGABaseWarning],
    Field(discriminator='type')
]
