from workos.audit_trail import AuditTrail
from workos.directory_sync import DirectorySync
from workos.sso import SSO


class Client(object):
    """Client for a convenient way to access the WorkOS feature set."""

    @property
    def sso(self):
        if not getattr(self, "_sso", None):
            self._sso = SSO()
        return self._sso

    @property
    def audit_trail(self):
        if not getattr(self, "_audit_trail", None):
            self._audit_trail = AuditTrail()
        return self._audit_trail

    @property
    def directory_sync(self):
        if not getattr(self, "_directory_sync", None):
            self._directory_sync = DirectorySync()
        return self._directory_sync


client = Client()
