from typing import Optional
from workos.__about__ import __version__
from workos._base_client import BaseClient
from workos.audit_logs import AuditLogsModule
from workos.directory_sync import AsyncDirectorySync
from workos.events import AsyncEvents
from workos.fga import FGAModule
from workos.mfa import MFAModule
from workos.organizations import AsyncOrganizations
from workos.passwordless import PasswordlessModule
from workos.portal import PortalModule
from workos.sso import AsyncSSO
from workos.user_management import AsyncUserManagement
from workos.utils.http_client import AsyncHTTPClient
from workos.webhooks import WebhooksModule
from workos.widgets import WidgetsModule


class AsyncClient(BaseClient):
    """Client for a convenient way to access the WorkOS feature set."""

    _http_client: AsyncHTTPClient

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None,
    ):
        super().__init__(
            api_key=api_key,
            client_id=client_id,
            base_url=base_url,
            request_timeout=request_timeout,
        )
        self._http_client = AsyncHTTPClient(
            api_key=self._api_key,
            base_url=self.base_url,
            client_id=self._client_id,
            version=__version__,
            timeout=self.request_timeout,
        )

    @property
    def sso(self) -> AsyncSSO:
        if not getattr(self, "_sso", None):
            self._sso = AsyncSSO(
                http_client=self._http_client, client_configuration=self
            )
        return self._sso

    @property
    def audit_logs(self) -> AuditLogsModule:
        raise NotImplementedError(
            "Audit logs APIs are not yet supported in the async client."
        )

    @property
    def directory_sync(self) -> AsyncDirectorySync:
        if not getattr(self, "_directory_sync", None):
            self._directory_sync = AsyncDirectorySync(self._http_client)
        return self._directory_sync

    @property
    def events(self) -> AsyncEvents:
        if not getattr(self, "_events", None):
            self._events = AsyncEvents(self._http_client)
        return self._events

    @property
    def fga(self) -> FGAModule:
        raise NotImplementedError("FGA APIs are not yet supported in the async client.")

    @property
    def organizations(self) -> AsyncOrganizations:
        if not getattr(self, "_organizations", None):
            self._organizations = AsyncOrganizations(self._http_client)
        return self._organizations

    @property
    def passwordless(self) -> PasswordlessModule:
        raise NotImplementedError(
            "Passwordless APIs are not yet supported in the async client."
        )

    @property
    def portal(self) -> PortalModule:
        raise NotImplementedError(
            "Portal APIs are not yet supported in the async client."
        )

    @property
    def webhooks(self) -> WebhooksModule:
        raise NotImplementedError("Webhooks are not yet supported in the async client.")

    @property
    def mfa(self) -> MFAModule:
        raise NotImplementedError("MFA APIs are not yet supported in the async client.")

    @property
    def user_management(self) -> AsyncUserManagement:
        if not getattr(self, "_user_management", None):
            self._user_management = AsyncUserManagement(
                http_client=self._http_client, client_configuration=self
            )
        return self._user_management

    @property
    def widgets(self) -> WidgetsModule:
        raise NotImplementedError(
            "Widgets APIs are not yet supported in the async client."
        )
