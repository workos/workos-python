from workos.sso import SSO

class Client(object):
    '''Client for a convenient way to access the WorkOS feature set.'''

    @property
    def sso(self):
        if not getattr(self, '_sso', None):
            self._sso = SSO()
        return self._sso

client = Client()