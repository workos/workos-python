import datetime

from workos.types.connect import ConnectApplication


class MockConnectApplication(ConnectApplication):
    def __init__(self, id: str, application_type: str = "m2m"):
        now = datetime.datetime.now().isoformat()
        kwargs = {
            "object": "connect_application",
            "id": id,
            "client_id": f"client_{id}",
            "name": "Test Application",
            "application_type": application_type,
            "scopes": ["read", "write"],
            "created_at": now,
            "updated_at": now,
        }
        if application_type == "m2m":
            kwargs["organization_id"] = "org_01ABC"
        elif application_type == "oauth":
            kwargs["redirect_uris"] = [
                {"uri": "https://example.com/callback", "default": True}
            ]
            kwargs["uses_pkce"] = True
            kwargs["is_first_party"] = True
            kwargs["was_dynamically_registered"] = False
        super().__init__(**kwargs)
