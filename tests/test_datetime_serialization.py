"""Outgoing datetimes serialize as millisecond-precision UTC with a Z suffix.

The API accepts only the Z form for date-time parameters, so every path that
sends a datetime (query strings, JSON bodies, model ``to_dict``) must agree.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from workos._base_client import _BaseWorkOSClient
from workos._types import _format_datetime

UTC_AWARE = datetime(2026, 10, 1, 18, 1, 14, 870587, tzinfo=timezone.utc)
EASTERN = datetime(2026, 10, 1, 14, 1, 14, 870587, tzinfo=timezone(timedelta(hours=-4)))
NAIVE = datetime(2026, 10, 1, 18, 1, 14, 870587)
EXPECTED = "2026-10-01T18:01:14.870Z"


class TestFormatDatetime:
    @pytest.mark.parametrize("value", [UTC_AWARE, EASTERN, NAIVE])
    def test_normalizes_to_utc_z(self, value: datetime) -> None:
        assert _format_datetime(value) == EXPECTED

    def test_never_emits_an_offset(self) -> None:
        # datetime.isoformat() would produce "+00:00" here; the API rejects it.
        assert "+00:00" not in _format_datetime(UTC_AWARE)
        assert "-04:00" not in _format_datetime(EASTERN)


class TestQueryEncoding:
    def test_datetime_values(self) -> None:
        encoded = _BaseWorkOSClient._encode_query(
            {"range_start": UTC_AWARE, "range_end": EASTERN, "naive": NAIVE}
        )
        expected_value = EXPECTED.replace(":", "%3A")
        assert encoded == (
            f"range_start={expected_value}"
            f"&range_end={expected_value}"
            f"&naive={expected_value}"
        )

    def test_datetime_lists_repeat_the_key(self) -> None:
        encoded = _BaseWorkOSClient._encode_query({"at": [UTC_AWARE, EASTERN]})
        expected_value = EXPECTED.replace(":", "%3A")
        assert encoded == f"at={expected_value}&at={expected_value}"

    def test_strings_pass_through_untouched(self) -> None:
        raw = "2026-10-01T18:01:14.870587+00:00"
        encoded = _BaseWorkOSClient._encode_query({"range_start": raw})
        assert encoded == "range_start=2026-10-01T18%3A01%3A14.870587%2B00%3A00"


class TestBodyEncoding:
    def test_datetime_values_anywhere_in_the_body(self) -> None:
        body = _BaseWorkOSClient._encode_body(
            {"range_start": EASTERN, "nested": {"at": UTC_AWARE}, "many": [NAIVE]}
        )
        assert body is not None
        assert json.loads(body) == {
            "range_start": EXPECTED,
            "nested": {"at": EXPECTED},
            "many": [EXPECTED],
        }

    def test_unknown_types_still_raise(self) -> None:
        with pytest.raises(TypeError, match="not JSON serializable"):
            _BaseWorkOSClient._encode_body({"x": object()})
