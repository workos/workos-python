from typing import Literal
from workos.resources.workos_model import WorkOSModel

PortalLinkIntent = Literal["audit_logs", "dsync", "log_streams", "sso"]


class PortalLink(WorkOSModel):
    """Representation of an WorkOS generate portal link response."""

    link: str
