from functools import wraps

import workos
from workos.exceptions import ConfigurationException


def validate_api_key_and_project_id(module_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            required_settings = [
                "api_key",
                "project_id",
            ]

            missing_settings = []
            for setting in required_settings:
                if not getattr(workos, setting, None):
                    missing_settings.append(setting)

            if missing_settings:
                raise ConfigurationException(
                    "The following settings are missing for {}: {}".format(
                        ", ".join(missing_settings), module_name
                    )
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
