from workos.resources.sso import ConnectionWithDomains


class ConnectionPayloadWithLegacyFields(ConnectionWithDomains):
    external_key: str