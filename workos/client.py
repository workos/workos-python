from .sso import SSO

class Client(object):
    @property
    def sso(self):
        # Exception if not setup
        if not getattr(self, '_sso', None):
            self._sso = SSO()
        return self._sso

client = Client()