from functools import wraps

import workos
from workos.exceptions import ConfigurationException

AUDIT_TRAIL_MODULE = "AuditTrail"
DIRECTORY_SYNC_MODULE = "DirectorySync"
PASSWORDLESS_MODULE = "Passwordless"
PORTAL_MODULE = "Portal"
SSO_MODULE = "SSO"

REQUIRED_SETTINGS_FOR_MODULE = {
    AUDIT_TRAIL_MODULE: ["api_key",],
    DIRECTORY_SYNC_MODULE: ["api_key",],
    PASSWORDLESS_MODULE: ["api_key",],
    PORTAL_MODULE: ["api_key",],
    SSO_MODULE: ["api_key", "project_id",],
}


def validate_settings(module_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            missing_settings = []
            for setting in REQUIRED_SETTINGS_FOR_MODULE[module_name]:
                if not getattr(workos, setting, None):
                    missing_settings.append(setting)

            if missing_settings:
                raise ConfigurationException(
                    "The following settings are missing for {}: {}".format(
                        module_name, ", ".join(missing_settings)
                    )
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
