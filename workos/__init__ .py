from .client import client
from .utils.settings import (
    set_setting, API_KEY_SETTING_KEY, BASE_API_URL_SETTING_KEY,
    PROJECT_ID_SETTING_KEY,
)

def init(api_key, project_id=None, base_api_url=None):
    set_setting(API_KEY_SETTING_KEY, api_key)

    if project_id is not None:
        set_setting(PROJECT_ID_SETTING_KEY, project_id)
    
    if base_api_url is not None:
        set_setting(BASE_API_URL_SETTING_KEY, base_api_url)