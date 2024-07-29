from workos.resources.workos_model import WorkOSModel


class Impersonator(WorkOSModel):
    """Representation of a WorkOS Dashboard member impersonating a user"""

    email: str
    reason: str
