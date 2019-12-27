import os

API_KEY_SETTING_KEY = '$WORKOS_API_KEY'
BASE_API_URL_SETTING_KEY = '$WORKOS_BASE_API_URL'
PROJECT_ID_SETTING_KEY = '$WORKOS_PROJECT_ID'

def get_setting(key, default=None):
    return os.environ.get(key, default)

def set_setting(key, value):
    os.environ[key] = value