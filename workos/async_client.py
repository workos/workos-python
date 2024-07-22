from workos.events import AsyncEvents

from workos.utils.http_client import AsyncHTTPClient


class AsyncClient(object):
    """Client for a convenient way to access the WorkOS feature set."""

    _http_client: AsyncHTTPClient

    def __init__(self, base_url: str, version: str, timeout: int):
        self._http_client = AsyncHTTPClient(
            base_url=base_url, version=version, timeout=timeout
        )

    @property
    def sso(self):
        raise NotImplementedError("SSO APIs are not yet supported in the async client.")

    @property
    def audit_logs(self):
        raise NotImplementedError(
            "Audit logs APIs are not yet supported in the async client."
        )

    @property
    def directory_sync(self):
        raise NotImplementedError(
            "Directory Sync APIs are not yet supported in the async client."
        )

    @property
    def events(self):
        if not getattr(self, "_events", None):
            self._events = AsyncEvents(self._http_client)
        return self._events

    @property
    def organizations(self):
        raise NotImplementedError(
            "Organizations APIs are not yet supported in the async client."
        )

    @property
    def passwordless(self):
        raise NotImplementedError(
            "Passwordless APIs are not yet supported in the async client."
        )

    @property
    def portal(self):
        raise NotImplementedError(
            "Portal APIs are not yet supported in the async client."
        )

    @property
    def webhooks(self):
        raise NotImplementedError("Webhooks are not yet supported in the async client.")

    @property
    def mfa(self):
        raise NotImplementedError("MFA APIs are not yet supported in the async client.")

    @property
    def user_management(self):
        raise NotImplementedError(
            "User Management APIs are not yet supported in the async client."
        )
