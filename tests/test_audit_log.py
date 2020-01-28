from datetime import datetime
import json

import pytest

import workos
from workos.audit_log import AuditLog


class TestSSO(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key_and_project_id):
        self.audit_log = AuditLog()

    def test_create_audit_log_event_succeeds(self):
        event = {
            "group": "Terrace House",
            "location": "1.1.1.1",
            "action": "house.created",
            "action_type": "C",
            "actor_name": "Daiki Miyagi",
            "actor_id": "user_12345",
            "target_name": "Ryota Yamasato",
            "target_id": "user_67890",
            "occurred_at": datetime.utcnow().isoformat(),
            "metadata": {
                "a": "b"
            }
        }
        response = self.audit_log.create_event(event)
        assert response.status_code == 200
    
    def test_create_audit_log_event_fails_with_long_metadata(self):
        with pytest.raises(Exception, match=r"Number of metadata keys exceeds .*"):
            metadata = { str(num): num for num in range(51) }
            event = {
                "group": "Terrace House",
                "location": "1.1.1.1",
                "action": "house.created",
                "action_type": "C",
                "actor_name": "Daiki Miyagi",
                "actor_id": "user_12345",
                "target_name": "Ryota Yamasato",
                "target_id": "user_67890",
                "occurred_at": datetime.utcnow().isoformat(),
                "metadata": metadata
            } 
            self.audit_log.create_event(event)