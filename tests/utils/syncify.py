import asyncio
from types import CoroutineType
from typing import Any, TypeVar, Union

ReturnType = TypeVar("ReturnType")


def _call(coro: CoroutineType) -> Any:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


def run_sync(obj: Union[CoroutineType, ReturnType]) -> ReturnType:
    if isinstance(obj, CoroutineType):
        return _call(obj)

    return obj
