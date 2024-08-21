import asyncio
from functools import wraps
from types import CoroutineType, FunctionType
from typing import Any, Coroutine, Protocol, TypeVar, Union

ReturnType = TypeVar("ReturnType")


def _call(coro: Coroutine[Any, Any, ReturnType]) -> ReturnType:
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


def _run_sync_wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        return run_sync(method(*args, **kwargs))

    return wrapped


class SyncifyMetaClass(type(Protocol)):
    def __new__(cls, classname, bases, class_dict):
        new_class_dict = {}
        for attribute_name, attribute in class_dict.items():
            # Only modify "public" methods
            if isinstance(attribute, FunctionType) and not attribute_name.startswith(
                "_"
            ):
                # Replace the method with a version wrapped in run_sync
                attribute = _run_sync_wrapper(attribute)

            new_class_dict[attribute_name] = attribute
        return type.__new__(cls, classname, bases, new_class_dict)
