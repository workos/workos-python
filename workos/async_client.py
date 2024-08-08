from workos._base_client import BaseClient
from workos.audit_logs import AuditLogsModule
from workos.directory_sync import AsyncDirectorySync
from workos.events import AsyncEvents
from workos.mfa import MFAModule
from workos.organizations import OrganizationsModule
from workos.passwordless import PasswordlessModule
from workos.portal import PortalModule
from workos.sso import AsyncSSO
from workos.user_management import AsyncUserManagement
from workos.utils.http_client import AsyncHTTPClient
from workos.webhooks import WebhooksModule


class AsyncClient(BaseClient):
    """Client for a convenient way to access the WorkOS feature set."""

    _http_client: AsyncHTTPClient

    _audit_logs: AuditLogsModule
    _directory_sync: AsyncDirectorySync
    _events: AsyncEvents
    _mfa: MFAModule
    _organizations: OrganizationsModule
    _passwordless: PasswordlessModule
    _portal: PortalModule
    _sso: AsyncSSO
    _user_management: AsyncUserManagement
    _webhooks: WebhooksModule

    def __init__(self, *, base_url: str, version: str, timeout: int):
        self._http_client = AsyncHTTPClient(
            base_url=base_url, version=version, timeout=timeout
        )

    @property
    def sso(self) -> AsyncSSO:
        if not getattr(self, "_sso", None):
            self._sso = AsyncSSO(self._http_client)
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
    def organizations(self) -> OrganizationsModule:
        raise NotImplementedError(
            "Organizations APIs are not yet supported in the async client."
        )

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
            self._user_management = AsyncUserManagement(self._http_client)
        return self._user_management
