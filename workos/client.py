from workos._base_client import BaseClient
from workos.audit_logs import AuditLogs
from workos.directory_sync import DirectorySync
from workos.organizations import Organizations
from workos.passwordless import Passwordless
from workos.portal import Portal
from workos.sso import SSO
from workos.webhooks import Webhooks
from workos.mfa import Mfa
from workos.events import Events
from workos.user_management import UserManagement
from workos.utils.http_client import SyncHTTPClient


class SyncClient(BaseClient):
    """Client for a convenient way to access the WorkOS feature set."""

    _http_client: SyncHTTPClient

    _audit_logs: AuditLogs
    _directory_sync: DirectorySync
    _events: Events
    _mfa: Mfa
    _organizations: Organizations
    _passwordless: Passwordless
    _portal: Portal
    _sso: SSO
    _user_management: UserManagement
    _webhooks: Webhooks

    def __init__(self, *, base_url: str, version: str, timeout: int):
        self._http_client = SyncHTTPClient(
            base_url=base_url, version=version, timeout=timeout
        )

    @property
    def sso(self) -> SSO:
        if not getattr(self, "_sso", None):
            self._sso = SSO(self._http_client)
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
            self._user_management = UserManagement(self._http_client)
        return self._user_management
