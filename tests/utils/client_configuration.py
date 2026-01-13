from workos._client_configuration import (
    ClientConfiguration as ClientConfigurationProtocol,
)


class ClientConfiguration(ClientConfigurationProtocol):
    def __init__(
        self,
        base_url: str,
        client_id: str,
        request_timeout: int,
        jwt_leeway: float = 0,
    ):
        self._base_url = base_url
        self._client_id = client_id
        self._request_timeout = request_timeout
        self._jwt_leeway = jwt_leeway

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def request_timeout(self) -> int:
        return self._request_timeout

    @property
    def jwt_leeway(self) -> float:
        return self._jwt_leeway
