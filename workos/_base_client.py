from abc import abstractmethod
import os
from typing import Generic, Optional, Type, TypeVar

from workos.__about__ import __version__
from workos.fga import FGAModule
from workos.utils._base_http_client import DEFAULT_REQUEST_TIMEOUT
from workos.utils.http_client import HTTPClient
from workos.audit_logs import AuditLogsModule
from workos.directory_sync import DirectorySyncModule
from workos.events import EventsModule
from workos.mfa import MFAModule
from workos.organizations import OrganizationsModule
from workos.passwordless import PasswordlessModule
from workos.portal import PortalModule
from workos.sso import SSOModule
from workos.user_management import UserManagementModule
from workos.webhooks import WebhooksModule


HTTPClientType = TypeVar("HTTPClientType", bound=HTTPClient)


class BaseClient(Generic[HTTPClientType]):
    """Base client for accessing the WorkOS feature set."""

    _api_key: str
    _base_url: str
    _client_id: str
    _request_timeout: int
    _http_client: HTTPClient

    def __init__(
        self,
        *,
        api_key: Optional[str],
        client_id: Optional[str],
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None,
        http_client_cls: Type[HTTPClientType],
    ) -> None:
        api_key = api_key or os.getenv("WORKOS_API_KEY")
        if api_key is None:
            raise ValueError(
                "WorkOS API key must be provided when instantiating the client or via the WORKOS_API_KEY environment variable."
            )

        self._api_key = api_key

        client_id = client_id or os.getenv("WORKOS_CLIENT_ID")
        if client_id is None:
            raise ValueError(
                "WorkOS client ID must be provided when instantiating the client or via the WORKOS_CLIENT_ID environment variable."
            )

        self._client_id = client_id

        self._base_url = (
            base_url
            if base_url
            else os.getenv("WORKOS_BASE_URL", "https://api.workos.com/")
        )
        self._request_timeout = (
            request_timeout
            if request_timeout
            else int(os.getenv("WORKOS_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT))
        )

        self._http_client = http_client_cls(
            api_key=self._api_key,
            base_url=self._base_url,
            client_id=self._client_id,
            version=__version__,
            timeout=self._request_timeout,
        )

    @property
    @abstractmethod
    def audit_logs(self) -> AuditLogsModule: ...

    @property
    @abstractmethod
    def directory_sync(self) -> DirectorySyncModule: ...

    @property
    @abstractmethod
    def events(self) -> EventsModule: ...

    @property
    @abstractmethod
    def fga(self) -> FGAModule: ...

    @property
    @abstractmethod
    def mfa(self) -> MFAModule: ...

    @property
    @abstractmethod
    def organizations(self) -> OrganizationsModule: ...

    @property
    @abstractmethod
    def passwordless(self) -> PasswordlessModule: ...

    @property
    @abstractmethod
    def portal(self) -> PortalModule: ...

    @property
    @abstractmethod
    def sso(self) -> SSOModule: ...

    @property
    @abstractmethod
    def user_management(self) -> UserManagementModule: ...

    @property
    @abstractmethod
    def webhooks(self) -> WebhooksModule: ...
