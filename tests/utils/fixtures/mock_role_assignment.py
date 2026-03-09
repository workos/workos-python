from typing import Optional, Sequence

from workos.types.authorization.role_assignment import (
    RoleAssignment,
    RoleAssignmentResource,
    RoleAssignmentRole,
)
from workos.types.list_resource import ListMetadata, ListPage


class MockRoleAssignment(RoleAssignment):
    def __init__(
        self,
        id: str = "ra_01ABC",
        role_slug: str = "admin",
        resource_id: str = "res_01ABC",
        resource_external_id: str = "ext_123",
        resource_type_slug: str = "document",
        created_at: str = "2024-01-01T00:00:00Z",
        updated_at: str = "2024-01-01T00:00:00Z",
    ):
        super().__init__(
            object="role_assignment",
            id=id,
            role=RoleAssignmentRole(slug=role_slug),
            resource=RoleAssignmentResource(
                id=resource_id,
                external_id=resource_external_id,
                resource_type_slug=resource_type_slug,
            ),
            created_at=created_at,
            updated_at=updated_at,
        )


class MockRoleAssignmentsList(ListPage[RoleAssignment]):
    def __init__(
        self,
        data: Optional[Sequence[RoleAssignment]] = None,
        before: Optional[str] = None,
        after: Optional[str] = "ra_01DEF",
    ):
        if data is None:
            data = [
                MockRoleAssignment(
                    id="ra_01ABC",
                    role_slug="admin",
                    resource_id="res_01ABC",
                    resource_external_id="ext_123",
                    resource_type_slug="document",
                    created_at="2024-01-15T09:30:00.000Z",
                    updated_at="2024-01-15T09:30:00.000Z",
                ),
                MockRoleAssignment(
                    id="ra_01DEF",
                    role_slug="editor",
                    resource_id="res_01XYZ",
                    resource_external_id="ext_456",
                    resource_type_slug="folder",
                    created_at="2024-01-14T08:00:00.000Z",
                    updated_at="2024-01-14T08:00:00.000Z",
                ),
            ]
        super().__init__(
            object="list",
            data=data,
            list_metadata=ListMetadata(before=before, after=after),
        )
