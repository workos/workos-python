import os

from workos.__about__ import __version__
from workos.client import client
from workos.resources.directory_sync import UntypedValue
from workos.resources.directory_sync import is_untyped_value
api_key = os.getenv("WORKOS_API_KEY")
client_id = os.getenv("WORKOS_CLIENT_ID")
base_api_url = "https://api.workos.com/"
request_timeout = 25
