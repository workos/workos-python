from typing import Literal
from workos.resources.workos_model import WorkOSModel


class PortalLink(WorkOSModel):
    """Representation of an WorkOS generate portal link response."""

    link: str
