from abc import abstractmethod
import os
from typing import Optional
from workos.__about__ import __version__
from workos._client_configuration import ClientConfiguration
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


class BaseClient(ClientConfiguration):
    """Base client for accessing the WorkOS feature set."""

    _api_key: str
    _base_url: str
    _client_id: str
    _request_timeout: int

    def __init__(
        self,
        *,
        api_key: Optional[str],
        client_id: Optional[str],
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None,
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

        self._base_url = self._enforce_trailing_slash(
            url=(
                base_url
                if base_url
                else os.getenv("WORKOS_BASE_URL", "https://api.workos.com/")
            )
        )

        self._request_timeout = (
            request_timeout
            if request_timeout
            else int(os.getenv("WORKOS_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT))
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

    def _enforce_trailing_slash(self, url: str) -> str:
        return url if url.endswith("/") else url + "/"

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def request_timeout(self) -> int:
        return self._request_timeout
