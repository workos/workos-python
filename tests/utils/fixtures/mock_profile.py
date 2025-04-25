from workos.types.sso import Profile


class MockProfile(Profile):

    def __init__(self, id: str):
        super().__init__(
            object="profile",
            id=id or "prof_01DWAS7ZQWM70PV93BFV1V78QV",
            email="demo@workos-okta.com",
            first_name="WorkOS",
            last_name="Demo",
            role={"slug": "admin"},
            groups=["Admins", "Developers"],
            organization_id="org_01FG53X8636WSNW2WEKB2C31ZB",
            connection_id="conn_01EMH8WAK20T42N2NBMNBCYHAG",
            connection_type="OktaSAML",
            idp_id="00u1klkowm8EGah2H357",
            custom_attributes={
                "license": "professional",
            },
            raw_attributes={
                "email": "demo@workos-okta.com",
                "first_name": "WorkOS",
                "last_name": "Demo",
                "groups": ["Admins", "Developers"],
                "license": "professional",
            },
        )
