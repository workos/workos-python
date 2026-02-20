from workos.types.workos_model import WorkOSModel


class AccessEvaluation(WorkOSModel):
    """Representation of a WorkOS Authorization access check result."""

    authorized: bool
