import json
from workos.webhooks import Webhooks
from requests import Response

import pytest

import workos
from workos.webhooks import Webhooks
from workos.utils.request import RESPONSE_TYPE_CODE

class TestWebhooks(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.webhooks = Webhooks()

    @pytest.fixture
    def mock_method_name(self):
        return '{"data":{"id":"directory_user_01FAEAJCR3ZBZ30D8BD1924TVG","state":"active","emails":[{"type":"work","value":"blair@foo-corp.com","primary":true}],"idp_id":"00u1e8mutl6wlH3lL4x7","object":"directory_user","username":"blair@foo-corp.com","last_name":"Lunceford","first_name":"Blair","directory_id":"directory_01F9M7F68PZP8QXP8G7X5QRHS7","raw_attributes":{"name":{"givenName":"Blair","familyName":"Lunceford","middleName":"Elizabeth","honorificPrefix":"Ms."},"title":"Developer Success Engineer","active":true,"emails":[{"type":"work","value":"blair@foo-corp.com","primary":true}],"groups":[],"locale":"en-US","schemas":["urn:ietf:params:scim:schemas:core:2.0:User","urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"],"userName":"blair@foo-corp.com","addresses":[{"region":"CO","primary":true,"locality":"Steamboat Springs","postalCode":"80487"}],"externalId":"00u1e8mutl6wlH3lL4x7","displayName":"Blair Lunceford","urn:ietf:params:scim:schemas:extension:enterprise:2.0:User":{"manager":{"value":"2","displayName":"Kathleen Chung"},"division":"Engineering","department":"Customer Success"}}},"event":"dsync.user.created"}'
    
    def test_print_method_name(self, mock_method_name, mock_request_method):
        mock_request_method("get", mock_method_name, 200)

        name = self.webhooks.print_method_name

        assert name == mock_method_name