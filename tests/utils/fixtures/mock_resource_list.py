from typing import Optional, Sequence

from workos.types.authorization.authorization_resource import AuthorizationResource
from workos.types.list_resource import ListMetadata, ListPage


class MockAuthorizationResourceList(ListPage[AuthorizationResource]):
    def __init__(
        self,
        data: Optional[Sequence[AuthorizationResource]] = None,
        before: Optional[str] = None,
        after: Optional[str] = "authz_resource_01HXYZ123ABC456DEF789DEF",
    ):
        if data is None:
            data = [
                AuthorizationResource(
                    object="authorization_resource",
                    id="authz_resource_01HXYZ123ABC456DEF789ABC",
                    external_id="doc-12345678",
                    name="Q5 Budget Report",
                    description="Financial report for Q5 2025",
                    resource_type_slug="document",
                    organization_id="org_01HXYZ123ABC456DEF789ABC",
                    parent_resource_id="authz_resource_01HXYZ123ABC456DEF789XYZ",
                    created_at="2024-01-15T09:30:00.000Z",
                    updated_at="2024-01-15T09:30:00.000Z",
                ),
                AuthorizationResource(
                    object="authorization_resource",
                    id="authz_resource_01HXYZ123ABC456DEF789DEF",
                    external_id="folder-123",
                    name="Finance Folder",
                    description=None,
                    resource_type_slug="folder",
                    organization_id="org_01HXYZ123ABC456DEF789ABC",
                    parent_resource_id=None,
                    created_at="2024-01-14T08:00:00.000Z",
                    updated_at="2024-01-14T08:00:00.000Z",
                ),
            ]
        super().__init__(
            object="list",
            data=data,
            list_metadata=ListMetadata(before=before, after=after),
        )
