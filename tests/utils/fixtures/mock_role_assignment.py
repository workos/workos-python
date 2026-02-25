import datetime

from workos.types.authorization.role_assignment import (
    RoleAssignment,
    RoleAssignmentResource,
    RoleAssignmentRole,
)


class MockRoleAssignment(RoleAssignment):
    def __init__(
        self,
        id: str = "ra_01ABC",
        role_slug: str = "admin",
        resource_id: str = "res_01ABC",
        resource_external_id: str = "ext_123",
        resource_type_slug: str = "document",
    ):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="role_assignment",
            id=id,
            role=RoleAssignmentRole(slug=role_slug),
            resource=RoleAssignmentResource(
                id=resource_id,
                external_id=resource_external_id,
                resource_type_slug=resource_type_slug,
            ),
            created_at=now,
            updated_at=now,
        )
