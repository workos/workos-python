from typing_extensions import TypedDict


class _RedirectUriInputRequired(TypedDict):
    uri: str


class RedirectUriInput(_RedirectUriInputRequired, total=False):
    default: bool
