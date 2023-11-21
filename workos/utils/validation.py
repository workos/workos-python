from functools import wraps

import workos
from workos.exceptions import ConfigurationException

AUDIT_LOGS_MODULE = "AuditLogs"
DIRECTORY_SYNC_MODULE = "DirectorySync"
EVENTS_MODULE = "Events"
ORGANIZATIONS_MODULE = "Organizations"
PASSWORDLESS_MODULE = "Passwordless"
PORTAL_MODULE = "Portal"
SSO_MODULE = "SSO"
WEBHOOKS_MODULE = "Webhooks"
MFA_MODULE = "MFA"
USER_MANAGEMENT_MODULE = "UserManagement"

REQUIRED_SETTINGS_FOR_MODULE = {
    AUDIT_LOGS_MODULE: [
        "api_key",
    ],
    DIRECTORY_SYNC_MODULE: [
        "api_key",
    ],
    EVENTS_MODULE: [
        "api_key",
    ],
    ORGANIZATIONS_MODULE: [
        "api_key",
    ],
    PASSWORDLESS_MODULE: [
        "api_key",
    ],
    PORTAL_MODULE: [
        "api_key",
    ],
    SSO_MODULE: [
        "api_key",
        "client_id",
    ],
    WEBHOOKS_MODULE: ["api_key"],
    MFA_MODULE: ["api_key"],
    USER_MANAGEMENT_MODULE: ["client_id", "api_key"],
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
