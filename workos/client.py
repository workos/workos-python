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


class Client(object):
    """Client for a convenient way to access the WorkOS feature set."""

    @property
    def sso(self):
        if not getattr(self, "_sso", None):
            self._sso = SSO()
        return self._sso

    @property
    def audit_logs(self):
        if not getattr(self, "_audit_logs", None):
            self._audit_logs = AuditLogs()
        return self._audit_logs

    @property
    def directory_sync(self):
        if not getattr(self, "_directory_sync", None):
            self._directory_sync = DirectorySync()
        return self._directory_sync

    @property
    def events(self):
        if not getattr(self, "_events", None):
            self._events = Events()
        return self._events

    @property
    def organizations(self):
        if not getattr(self, "_organizations", None):
            self._organizations = Organizations()
        return self._organizations

    @property
    def passwordless(self):
        if not getattr(self, "_passwordless", None):
            self._passwordless = Passwordless()
        return self._passwordless

    @property
    def portal(self):
        if not getattr(self, "_portal", None):
            self._portal = Portal()
        return self._portal

    @property
    def webhooks(self):
        if not getattr(self, "_webhooks", None):
            self._webhooks = Webhooks()
        return self._webhooks

    @property
    def mfa(self):
        if not getattr(self, "_mfa", None):
            self._mfa = Mfa()
        return self._mfa

    @property
    def user_management(self):
        if not getattr(self, "_user_management", None):
            self._user_management = UserManagement()
        return self._user_management


client = Client()
