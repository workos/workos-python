import asyncio
from typing import Any, Coroutine, TypeVar, Union

ReturnType = TypeVar("ReturnType")


def _call(coro: Coroutine[Any, Any, ReturnType]) -> ReturnType:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


def syncify(obj: Union[Coroutine[Any, Any, ReturnType], ReturnType]) -> ReturnType:
    if isinstance(obj, Coroutine):
        return _call(obj)

    return obj
