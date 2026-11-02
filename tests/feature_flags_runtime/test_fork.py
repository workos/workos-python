# @oagen-ignore-file
"""A forked worker process resumes polling with its own thread."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

SCRIPT = textwrap.dedent(
    """
    import os
    import threading
    import time
    import warnings

    from workos import WorkOSClient
    from workos.feature_flags.runtime import _policy
    from tests.feature_flags_runtime.helpers import FlagServer, SyncBackend, flag, payload

    _policy.next_delay = lambda interval, failures, max_retry_delay: 0.01
    server = FlagServer()
    server.respond(200, payload(f=flag("f", default_value=True)))

    def reset_server_lock():
        # The parent's poller may hold the fake server's lock at fork time.
        server._condition = threading.Condition()

    os.register_at_fork(after_in_child=reset_server_lock)
    workos = WorkOSClient(api_key="sk_test", base_url="https://api.workos.test", http_client=SyncBackend(server))
    runtime = workos.create_feature_flags_runtime_client()
    runtime.start()
    runtime.wait_until_ready(timeout=5)
    server.wait_for_requests(2)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        pid = os.fork()
    if pid == 0:
        before = len(server.requests)
        time.sleep(0.1)
        idle = len(server.requests) == before
        enabled = runtime.is_enabled("f")
        deadline = time.monotonic() + 5
        while len(server.requests) < before + 3 and time.monotonic() < deadline:
            time.sleep(0.01)
        resumed = len(server.requests) >= before + 3
        runtime.close()
        os._exit(0 if idle and enabled and resumed else 1)
    _, status = os.waitpid(pid, 0)
    runtime.close()
    raise SystemExit(os.waitstatus_to_exitcode(status))
    """
)


@pytest.mark.skipif(not hasattr(os, "fork"), reason="requires os.fork")
def test_a_forked_child_restarts_polling_on_first_use() -> None:
    result = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
