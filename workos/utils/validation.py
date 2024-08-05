from enum import Enum
from typing import Callable, Dict, List, ParamSpec

import workos
from workos.exceptions import ConfigurationException


class Module(Enum):
    AUDIT_LOGS = "AuditLogs"
    DIRECTORY_SYNC = "DirectorySync"
    EVENTS = "Events"
    ORGANIZATIONS = "Organizations"
    PASSWORDLESS = "Passwordless"
    PORTAL = "Portal"
    SSO = "SSO"
    WEBHOOKS = "Webhooks"
    MFA = "MFA"
    USER_MANAGEMENT = "UserManagement"


REQUIRED_SETTINGS_FOR_MODULE: Dict[Module, List[str]] = {
    Module.AUDIT_LOGS: ["api_key"],
    Module.DIRECTORY_SYNC: ["api_key"],
    Module.EVENTS: ["api_key"],
    Module.ORGANIZATIONS: ["api_key"],
    Module.PASSWORDLESS: ["api_key"],
    Module.PORTAL: ["api_key"],
    Module.SSO: ["api_key", "client_id"],
    Module.WEBHOOKS: ["api_key"],
    Module.MFA: ["api_key"],
    Module.USER_MANAGEMENT: ["client_id", "api_key"],
}


P = ParamSpec("P")


def validate_settings(
    module_name: Module,
) -> Callable[[Callable[P, None]], Callable[P, None]]:
    def decorator(fn: Callable[P, None], /) -> Callable[P, None]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
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
