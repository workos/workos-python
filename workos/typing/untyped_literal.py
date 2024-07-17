import re
from typing import Annotated, Any
from typing_extensions import TypeIs

from pydantic import Field


untyped_literal_re = re.compile(r"^Untyped\[[a-zA-Z_ ]+\]$")
UntypedLiteral = Annotated[str, Field(pattern=untyped_literal_re)]


def is_untyped_literal(value: str) -> TypeIs[UntypedLiteral]:
    return untyped_literal_re.match(value) is not None
