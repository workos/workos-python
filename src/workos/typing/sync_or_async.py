from typing import Awaitable, TypeVar, Union


T = TypeVar("T")
SyncOrAsync = Union[T, Awaitable[T]]
