from workos.audit_trail import AuditTrail
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


client = Client()
