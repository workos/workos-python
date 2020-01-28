from workos.audit_log import AuditLog
from workos.sso import SSO


class Client(object):
    """Client for a convenient way to access the WorkOS feature set."""

    @property
    def sso(self):
        if not getattr(self, "_sso", None):
            self._sso = SSO()
        return self._sso

    @property
    def audit_log(self):
        if not getattr(self, "_audit_log", None):
            self._audit_log = AuditLog()
        return self._audit_log


client = Client()
