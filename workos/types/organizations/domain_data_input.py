from typing import Literal, TypedDict


class DomainDataInput(TypedDict):
    domain: str
    state: Literal["verified", "pending"]
