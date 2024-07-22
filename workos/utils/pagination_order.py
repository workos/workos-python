from enum import Enum
from typing import Literal


class Order(Enum):
    Asc = "asc"
    Desc = "desc"


PaginationOrder = Literal["asc", "desc"]
