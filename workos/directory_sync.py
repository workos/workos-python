import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET
from workos.utils.validation import DIRECTORY_SYNC_MODULE, validate_settings

RESPONSE_LIMIT = 10


class DirectorySync(object):
    """Offers methods through the WorkOS Directory Sync service."""

    @validate_settings(DIRECTORY_SYNC_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def get_directory_users(
        self, directory_endpoint_id, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        params = {"limit": limit, "before": before, "after": after}
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/users".format(
                directory_endpoint_id=directory_endpoint_id
            ),
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def get_directory_groups(
        self, directory_endpoint_id, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        params = {"limit": limit, "before": before, "after": after}
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/groups".format(
                directory_endpoint_id=directory_endpoint_id
            ),
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def get_directory_user(self, directory_endpoint_id, directory_user_id):
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/users/{directory_user_id}".format(
                directory_endpoint_id=directory_endpoint_id,
                directory_user_id=directory_user_id,
            ),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

    def get_directory_user_groups(self, directory_endpoint_id, directory_user_id):
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/users/{directory_user_id}/groups".format(
                directory_endpoint_id=directory_endpoint_id,
                directory_user_id=directory_user_id,
            ),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )
