from typing import Literal
from typing_extensions import TypedDict


class DomainDataInput(TypedDict):
    domain: str
    state: Literal["verified", "pending"]
