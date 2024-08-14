from typing import Protocol


class ClientConfiguration(Protocol):
    @property
    def base_url(self) -> str: ...
    @property
    def client_id(self) -> str: ...
    @property
    def request_timeout(self) -> int: ...
