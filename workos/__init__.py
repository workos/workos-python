import os

from workos.__about__ import __version__
from workos.client import client
from workos.typing.untyped_value import UntypedValue, is_untyped_value
from workos.typing.untyped_literal import is_untyped_literal
api_key = os.getenv("WORKOS_API_KEY")
client_id = os.getenv("WORKOS_CLIENT_ID")
base_api_url = "https://api.workos.com/"
request_timeout = 25
