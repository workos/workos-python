import datetime

from workos.resources.organizations import Organization
from workos.types.organizations.organization_domain import OrganizationDomain


class MockOrganization(Organization):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="organization",
            id=id,
            name="Foo Corporation",
            allow_profiles_outside_organization=False,
            created_at=now,
            updated_at=now,
            domains=[
                OrganizationDomain(
                    object="organization_domain",
                    id="org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
                    organization_id="org_12345",
                    domain="example.io",
                )
            ],
        )
