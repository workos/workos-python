import asyncio
from types import CoroutineType
from typing import Any, Coroutine, Union


def _call(coro: CoroutineType) -> Any:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


def run_sync(obj: Union[Coroutine[Any, Any, Any], Any]) -> Any:
    if isinstance(obj, CoroutineType):
        return _call(obj)

    return obj
