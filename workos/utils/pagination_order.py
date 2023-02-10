from enum import Enum


class Order(Enum):
    Asc = "asc"
    Desc = "desc"


def timestamp_compare(timestamp_0, timestamp_1):
    if timestamp_0 < timestamp_1:
        return Order.Asc
    else:
        return Order.Desc
