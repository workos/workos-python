import os

from workos.__about__ import __version__
from workos.client import client

api_key = os.getenv("WORKOS_API_KEY")
base_api_url = "https://api.workos.com/"
