from workos.types.sso import ConnectionWithDomains


class ConnectionPayloadWithLegacyFields(ConnectionWithDomains):
    external_key: str
