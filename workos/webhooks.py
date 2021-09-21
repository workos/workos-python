import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
)
from workos.utils.validation import WEBHOOKS_MODULE, validate_settings


class Webhooks(object):
    """Offers methods through the WorkOS Webhooks service."""

    @validate_settings(WEBHOOKS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    @property
    def print_method_name(self):
        
        return '{"data":{"id":"directory_user_01FAEAJCR3ZBZ30D8BD1924TVG","state":"active","emails":[{"type":"work","value":"blair@foo-corp.com","primary":true}],"idp_id":"00u1e8mutl6wlH3lL4x7","object":"directory_user","username":"blair@foo-corp.com","last_name":"Lunceford","first_name":"Blair","directory_id":"directory_01F9M7F68PZP8QXP8G7X5QRHS7","raw_attributes":{"name":{"givenName":"Blair","familyName":"Lunceford","middleName":"Elizabeth","honorificPrefix":"Ms."},"title":"Developer Success Engineer","active":true,"emails":[{"type":"work","value":"blair@foo-corp.com","primary":true}],"groups":[],"locale":"en-US","schemas":["urn:ietf:params:scim:schemas:core:2.0:User","urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"],"userName":"blair@foo-corp.com","addresses":[{"region":"CO","primary":true,"locality":"Steamboat Springs","postalCode":"80487"}],"externalId":"00u1e8mutl6wlH3lL4x7","displayName":"Blair Lunceford","urn:ietf:params:scim:schemas:extension:enterprise:2.0:User":{"manager":{"value":"2","displayName":"Kathleen Chung"},"division":"Engineering","department":"Customer Success"}}},"event":"dsync.user.created"}'