from typing import TypedDict


class SsoIntentOptions(TypedDict):
    bookmark_slug: str


class IntentOptions(TypedDict):
    sso: SsoIntentOptions
