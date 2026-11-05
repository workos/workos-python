# @oagen-ignore-file
"""Polling delays and retry decisions of the runtime client."""

from __future__ import annotations

from typing import Optional

import pytest

from workos._errors import (
    NotFoundError,
    RateLimitExceededError,
    ServerError,
    WorkOSConnectionError,
    WorkOSError,
    WorkOSTimeoutError,
)
from workos._http import TransportError
from workos.feature_flags.runtime import _policy


@pytest.fixture
def random_value(monkeypatch: pytest.MonkeyPatch) -> "RandomValue":
    value = RandomValue()
    monkeypatch.setattr(_policy.random, "random", lambda: value.value)
    return value


class RandomValue:
    value = 0.5


class TestNextDelay:
    def test_a_healthy_poll_waits_one_interval(self, random_value: RandomValue) -> None:
        assert _policy.next_delay(30, 0, 60) == 30

    @pytest.mark.parametrize("value, expected", [(0.0, 27.0), (1.0, 33.0)])
    def test_jitter_is_ten_percent_either_way(
        self, random_value: RandomValue, value: float, expected: float
    ) -> None:
        random_value.value = value
        assert _policy.next_delay(30, 0, 60) == pytest.approx(expected)

    def test_failures_never_poll_sooner_than_the_interval(
        self, random_value: RandomValue
    ) -> None:
        assert [_policy.next_delay(30, failures, 60) for failures in range(1, 9)] == [
            30,
            30,
            30,
            30,
            30,
            32,
            60,
            60,
        ]

    def test_backoff_is_capped_by_max_retry_delay(
        self, random_value: RandomValue
    ) -> None:
        assert _policy.next_delay(5, 20, 12) == 12
        assert _policy.next_delay(5, 1000, 60) == 60

    def test_delays_have_a_one_second_floor(self, random_value: RandomValue) -> None:
        random_value.value = 0.0
        assert _policy.next_delay(1, 0, 60) == 1.0


class TestAttemptRetryDelay:
    @pytest.mark.parametrize(
        "error",
        [
            ServerError("busy", status_code=503),
            RateLimitExceededError("slow down"),
            WorkOSTimeoutError(),
            WorkOSConnectionError(),
        ],
    )
    def test_transient_failures_are_retried(
        self, random_value: RandomValue, error: Exception
    ) -> None:
        assert _policy.attempt_retry_delay(error, 0, 10, 3) == pytest.approx(0.5)
        assert _policy.attempt_retry_delay(error, 2, 10, 3) == pytest.approx(1.125)

    def test_network_errors_from_the_transport_are_retried(
        self, random_value: RandomValue
    ) -> None:
        error = WorkOSError("Network error")
        error.__cause__ = TransportError("reset")
        assert _policy.attempt_retry_delay(error, 0, 10, 3) is not None

    @pytest.mark.parametrize(
        "error",
        [
            NotFoundError("missing"),
            ServerError("not implemented", status_code=501),
            ValueError("bug"),
        ],
    )
    def test_other_failures_are_not_retried(self, error: Exception) -> None:
        assert _policy.attempt_retry_delay(error, 0, 10, 3) is None

    @pytest.mark.parametrize("max_retries, attempt", [(3, 3), (1, 1), (0, 0)])
    def test_retries_follow_the_clients_max_retries(
        self, max_retries: int, attempt: int
    ) -> None:
        error = ServerError("busy", status_code=503)
        assert _policy.attempt_retry_delay(error, attempt, 10, max_retries) is None
        if attempt:
            assert _policy.attempt_retry_delay(error, attempt - 1, 10, max_retries)

    def test_retry_after_is_honored_when_it_fits(self) -> None:
        error = RateLimitExceededError("slow down", retry_after=2.0)
        assert _policy.attempt_retry_delay(error, 0, 10, 3) == 2.0
        assert _policy.attempt_retry_delay(error, 0, 1.5, 3) is None

    def test_retry_after_is_capped_and_never_negative_inside_a_refresh(self) -> None:
        long_wait = RateLimitExceededError("slow down", retry_after=120.0)
        assert _policy.attempt_retry_delay(long_wait, 0, 300, 3) == 60.0
        negative = RateLimitExceededError("slow down", retry_after=-5.0)
        assert _policy.attempt_retry_delay(negative, 0, 10, 3) == 0.0

    @pytest.mark.parametrize("remaining, expected", [(1.0, 0.5), (0.99, None)])
    def test_a_retry_must_leave_time_for_the_request_itself(
        self, random_value: RandomValue, remaining: float, expected: Optional[float]
    ) -> None:
        assert (
            _policy.attempt_retry_delay(
                ServerError("busy", status_code=503), 0, remaining, 3
            )
            == expected
        )


class TestDurations:
    @pytest.mark.parametrize("value", [True, "10", None])
    def test_non_numbers_are_rejected(self, value: object) -> None:
        with pytest.raises(TypeError):
            _policy.validate_duration(value, "request_timeout")

    def test_the_polling_interval_has_a_five_second_minimum(self) -> None:
        assert _policy.polling_interval(0.5) == 5.0
        assert _policy.polling_interval(45) == 45.0


class TestRetryAfter:
    def test_a_429_asks_the_next_poll_to_wait(self) -> None:
        assert _policy.retry_after(RateLimitExceededError("slow", retry_after=20)) == 20

    def test_the_wait_is_capped_at_sixty_seconds(self) -> None:
        assert (
            _policy.retry_after(RateLimitExceededError("slow", retry_after=600)) == 60
        )

    @pytest.mark.parametrize(
        "error",
        [RateLimitExceededError("slow"), ServerError("busy", status_code=503)],
    )
    def test_other_failures_ask_for_nothing(self, error: Exception) -> None:
        assert _policy.retry_after(error) is None
