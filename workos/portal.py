import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET
from workos.utils.validation import PORTAL_MODULE, validate_settings

RESPONSE_LIMIT = 10


class Portal(object):
    @validate_settings(PORTAL_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def list_organizations(
        self, domains=None, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Retrieve a list of organizations that have connections configured within your WorkOS dashboard.

        Kwargs:
            domains (list): Filter organizations to only return those that are associated with the provided domains. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization ID. (Optional)

        Returns:
            dict: Organizations response from WorkOS.
        """
        params = {
            "domains": domains,
            "limit": limit,
            "before": before,
            "after": after,
        }
        return self.request_helper.request(
            "organizations",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )
