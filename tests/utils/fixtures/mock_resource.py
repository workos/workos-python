import datetime

from workos.types.authorization.resource import Resource


class MockResource(Resource):
    def __init__(
        self,
        id: str = "res_01ABC",
        external_id: str = "ext_123",
        name: str = "Test Resource",
        resource_type_slug: str = "document",
        organization_id: str = "org_01EHT88Z8J8795GZNQ4ZP1J81T",
    ):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="authorization_resource",
            id=id,
            external_id=external_id,
            name=name,
            resource_type_slug=resource_type_slug,
            organization_id=organization_id,
            created_at=now,
            updated_at=now,
        )
