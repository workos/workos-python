# @oagen-ignore-file

import json
from datetime import datetime, timezone

import pytest

from workos.audit_logs.models import (
    AuditLogEvent,
    AuditLogEventActor,
    AuditLogEventContext,
)


def event_from_wire(timestamp: str | None) -> AuditLogEvent:
    data = {
        "action": "user.signed_in",
        "actor": {"id": "user_1", "type": "user"},
        "targets": [],
        "context": {"location": "127.0.0.1"},
    }
    if timestamp is not None:
        data["occurred_at"] = timestamp
    return AuditLogEvent.from_dict(data)


def assert_timestamp(body, timestamp):
    if timestamp is None:
        assert "occurred_at" not in body["event"]
    else:
        assert body["event"]["occurred_at"] == timestamp


@pytest.mark.parametrize("timestamp", [None, "2026-11-03T12:34:56.789Z"])
def test_sync_create_event_omits_or_preserves_timestamp(workos, httpx_mock, timestamp):
    httpx_mock.add_response(json={"success": True})

    workos.audit_logs.create_event(
        organization_id="org_123", event=event_from_wire(timestamp)
    )

    assert_timestamp(json.loads(httpx_mock.get_request().content), timestamp)


@pytest.mark.asyncio
@pytest.mark.parametrize("timestamp", [None, "2026-11-03T12:34:56.789Z"])
async def test_async_create_event_omits_or_preserves_timestamp(
    async_workos, httpx_mock, timestamp
):
    httpx_mock.add_response(json={"success": True})

    await async_workos.audit_logs.create_event(
        organization_id="org_123", event=event_from_wire(timestamp)
    )

    assert_timestamp(json.loads(httpx_mock.get_request().content), timestamp)


def test_existing_positional_constructor_keeps_timestamp_in_its_slot():
    timestamp = datetime(2026, 11, 3, 12, 34, 56, 789000, tzinfo=timezone.utc)
    actor = AuditLogEventActor(id="user_1", type="user")
    context = AuditLogEventContext(location="127.0.0.1")

    event = AuditLogEvent("user.signed_in", timestamp, actor, [], context)

    assert event.to_dict()["occurred_at"] == "2026-11-03T12:34:56.789Z"
