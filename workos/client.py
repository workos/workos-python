from typing import Optional
from workos.__about__ import __version__
from workos._base_client import BaseClient
from workos.audit_logs import AuditLogs
from workos.directory_sync import DirectorySync
from workos.fga import FGA
from workos.organizations import Organizations
from workos.passwordless import Passwordless
from workos.portal import Portal
from workos.sso import SSO
from workos.webhooks import Webhooks
from workos.mfa import Mfa
from workos.events import Events
from workos.user_management import UserManagement
from workos.utils.http_client import SyncHTTPClient
from workos.widgets import Widgets


class SyncClient(BaseClient):
    """Client for a convenient way to access the WorkOS feature set."""

    _http_client: SyncHTTPClient

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
        self._http_client = SyncHTTPClient(
            api_key=self._api_key,
            base_url=self.base_url,
            client_id=self._client_id,
            version=__version__,
            timeout=self.request_timeout,
        )

    @property
    def sso(self) -> SSO:
        if not getattr(self, "_sso", None):
            self._sso = SSO(http_client=self._http_client, client_configuration=self)
        return self._sso

    @property
    def audit_logs(self) -> AuditLogs:
        if not getattr(self, "_audit_logs", None):
            self._audit_logs = AuditLogs(self._http_client)
        return self._audit_logs

    @property
    def directory_sync(self) -> DirectorySync:
        if not getattr(self, "_directory_sync", None):
            self._directory_sync = DirectorySync(self._http_client)
        return self._directory_sync

    @property
    def events(self) -> Events:
        if not getattr(self, "_events", None):
            self._events = Events(self._http_client)
        return self._events

    @property
    def fga(self) -> FGA:
        if not getattr(self, "_fga", None):
            self._fga = FGA(self._http_client)
        return self._fga

    @property
    def organizations(self) -> Organizations:
        if not getattr(self, "_organizations", None):
            self._organizations = Organizations(self._http_client)
        return self._organizations

    @property
    def passwordless(self) -> Passwordless:
        if not getattr(self, "_passwordless", None):
            self._passwordless = Passwordless(self._http_client)
        return self._passwordless

    @property
    def portal(self) -> Portal:
        if not getattr(self, "_portal", None):
            self._portal = Portal(self._http_client)
        return self._portal

    @property
    def webhooks(self) -> Webhooks:
        if not getattr(self, "_webhooks", None):
            self._webhooks = Webhooks()
        return self._webhooks

    @property
    def mfa(self) -> Mfa:
        if not getattr(self, "_mfa", None):
            self._mfa = Mfa(self._http_client)
        return self._mfa

    @property
    def user_management(self) -> UserManagement:
        if not getattr(self, "_user_management", None):
            self._user_management = UserManagement(
                http_client=self._http_client, client_configuration=self
            )
        return self._user_management

    @property
    def widgets(self) -> Widgets:
        if not getattr(self, "_widgets", None):
            self._widgets = Widgets(http_client=self._http_client)
        return self._widgets
