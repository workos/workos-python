from typing import Protocol

from workos.utils.http_client import BaseHTTPClient
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


class BaseClient(Protocol):
    """Base client for accessing the WorkOS feature set."""

    _http_client: BaseHTTPClient

    @property
    def audit_logs(self) -> AuditLogsModule: ...

    @property
    def directory_sync(self) -> DirectorySyncModule: ...

    @property
    def events(self) -> EventsModule: ...

    @property
    def mfa(self) -> MFAModule: ...

    @property
    def organizations(self) -> OrganizationsModule: ...

    @property
    def passwordless(self) -> PasswordlessModule: ...

    @property
    def portal(self) -> PortalModule: ...

    @property
    def sso(self) -> SSOModule: ...

    @property
    def user_management(self) -> UserManagementModule: ...

    @property
    def webhooks(self) -> WebhooksModule: ...
