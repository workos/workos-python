import os

from workos.__about__ import __version__
from workos.client import SyncClient
from workos.async_client import AsyncClient

api_key = os.getenv("WORKOS_API_KEY")
client_id = os.getenv("WORKOS_CLIENT_ID")
base_api_url = os.getenv("WORKOS_BASE_URL", "https://api.workos.com/")
request_timeout = int(os.getenv("WORKOS_REQUEST_TIMEOUT", "25"))


client = SyncClient(base_url=base_api_url, version=__version__, timeout=request_timeout)
async_client = AsyncClient(
    base_url=base_api_url, version=__version__, timeout=request_timeout
)
