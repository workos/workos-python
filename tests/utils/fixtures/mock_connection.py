import datetime
from workos.types.sso import (
    ConnectionDomain,
    ConnectionWithDomains,
    SamlConnectionOptions,
)


class MockConnection(ConnectionWithDomains):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="connection",
            id=id,
            organization_id="org_id_" + id,
            connection_type="OktaSAML",
            name="Foo Corporation",
            state="active",
            created_at=now,
            updated_at=now,
            options=SamlConnectionOptions(signing_cert="signing_cert"),
            domains=[
                ConnectionDomain(
                    id="connection_domain_abc123",
                    object="connection_domain",
                    domain="domain1.com",
                )
            ],
        )
