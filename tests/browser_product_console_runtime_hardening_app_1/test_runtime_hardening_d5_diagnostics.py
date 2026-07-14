from __future__ import annotations

import socket
import time
from http.client import HTTPConnection
from threading import Thread

import pytest

from apps.browser_product_console_runtime_app_1 import (
    ConsoleResponse,
    ConsoleRuntimeConfig,
    RuntimeDiagnosticsSnapshot,
    RuntimeFaultCode,
    RuntimeFaultLedger,
    RuntimeFaultRecord,
    RuntimeLifecycleState,
    create_loopback_server,
)


def _reserve_port() -> int:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as handle:
        handle.bind(("127.0.0.1", 0))
        port = int(handle.getsockname()[1])

    assert 1024 <= port <= 65535
    return port


def _config(tmp_path, port):
    return ConsoleRuntimeConfig(
        allowed_root=tmp_path,
        host="127.0.0.1",
        port=port,
    )


def _wait_for_state(
    server,
    expected,
    timeout=3.0,
):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if server.lifecycle_state is expected:
            return
        time.sleep(0.01)

    raise AssertionError(
        f"server state did not reach {expected.value}"
    )


def _wait_for_quiet(
    server,
    timeout=3.0,
):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if server.active_request_count == 0:
            return
        time.sleep(0.01)

    raise AssertionError(
        "server active request count did not return to zero"
    )


def _start_server(server):
    thread = Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()
    _wait_for_state(
        server,
        RuntimeLifecycleState.SERVING,
    )
    return thread


def _stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=3.0)
    assert not thread.is_alive()
    server.server_close()


def _request(
    port,
    *,
    method="GET",
    path="/health",
):
    connection = HTTPConnection(
        "127.0.0.1",
        port,
        timeout=3.0,
    )

    try:
        connection.putrequest(
            method,
            path,
            skip_host=True,
            skip_accept_encoding=True,
        )
        connection.putheader(
            "Host",
            f"127.0.0.1:{port}",
        )
        connection.endheaders()

        response = connection.getresponse()
        body = response.read()

        return (
            response.status,
            dict(response.getheaders()),
            body,
        )
    finally:
        connection.close()


class _FlakyApplication:
    def __init__(self) -> None:
        self.calls = 0

    def dispatch(
        self,
        method,
        target,
    ):
        self.calls += 1

        if self.calls == 1:
            raise RuntimeError(
                "sensitive internal failure detail"
            )

        return ConsoleResponse(
            status=200,
            content_type="text/plain; charset=utf-8",
            body=b"recovered",
        )


def test_d5_fault_ledger_is_bounded_and_ordered():
    ledger = RuntimeFaultLedger(capacity=2)

    first = ledger.record(
        RuntimeFaultCode.CAPACITY_REJECTED,
        "SERVING",
    )
    second = ledger.record(
        RuntimeFaultCode.APPLICATION_DISPATCH_FAILURE,
        "SERVING",
    )
    third = ledger.record(
        RuntimeFaultCode.REQUEST_HANDLER_FAILURE,
        "SERVING",
    )

    snapshot = ledger.snapshot(
        lifecycle_state="SERVING",
        host="127.0.0.1",
        port=8765,
        active_request_count=0,
        rejected_request_count=1,
    )

    assert first.sequence == 1
    assert second.sequence == 2
    assert third.sequence == 3
    assert snapshot.fault_count == 3
    assert tuple(
        item.sequence
        for item in snapshot.recent_faults
    ) == (
        2,
        3,
    )


@pytest.mark.parametrize(
    "capacity",
    (
        0,
        129,
        True,
        1.5,
    ),
)
def test_d5_fault_ledger_rejects_invalid_capacity(
    capacity,
):
    with pytest.raises(ValueError):
        RuntimeFaultLedger(capacity=capacity)


def test_d5_fault_record_message_is_deterministic():
    with pytest.raises(
        ValueError,
        match="deterministic code",
    ):
        RuntimeFaultRecord(
            sequence=1,
            code=RuntimeFaultCode.SERVER_LOOP_FAILURE,
            lifecycle_state="FAILED",
            message="raw exception detail",
        )


def test_d5_diagnostics_snapshot_preserves_authority():
    snapshot = RuntimeDiagnosticsSnapshot(
        lifecycle_state="READY",
        host="127.0.0.1",
        port=8765,
        active_request_count=0,
        rejected_request_count=0,
        fault_count=0,
        recent_faults=(),
    )

    assert snapshot.paper_only
    assert snapshot.local_only
    assert snapshot.loopback_only
    assert snapshot.read_only
    assert snapshot.operator_review_required


@pytest.mark.parametrize(
    "field_name",
    (
        "paper_only",
        "local_only",
        "loopback_only",
        "read_only",
        "operator_review_required",
    ),
)
def test_d5_diagnostics_snapshot_rejects_disabled_authority(
    field_name,
):
    values = {
        "lifecycle_state": "READY",
        "host": "127.0.0.1",
        "port": 8765,
        "active_request_count": 0,
        "rejected_request_count": 0,
        "fault_count": 0,
        "recent_faults": (),
        field_name: False,
    }

    with pytest.raises(
        ValueError,
        match="authority",
    ):
        RuntimeDiagnosticsSnapshot(**values)


def test_d5_application_fault_isolated_and_recovery_preserved(
    tmp_path,
):
    port = _reserve_port()
    application = _FlakyApplication()
    server = create_loopback_server(
        _config(tmp_path, port),
        application,
    )
    thread = _start_server(server)

    try:
        status, headers, body = _request(port)

        assert status == 500
        assert body == b"Internal Server Error"
        assert (
            b"sensitive internal failure detail"
            not in body
        )
        assert headers["Cache-Control"] == "no-store"
        assert (
            headers["X-Content-Type-Options"]
            == "nosniff"
        )
        assert headers["Connection"] == "close"

        _wait_for_quiet(server)

        diagnostics = server.diagnostics_snapshot()

        assert diagnostics.lifecycle_state == "SERVING"
        assert diagnostics.fault_count == 1
        assert diagnostics.active_request_count == 0
        assert diagnostics.recent_faults[-1].code is (
            RuntimeFaultCode.APPLICATION_DISPATCH_FAILURE
        )
        assert diagnostics.recent_faults[-1].message == (
            "application dispatch failed"
        )

        status, _, body = _request(port)

        assert status == 200
        assert body == b"recovered"
    finally:
        _stop_server(server, thread)


def test_d5_head_fault_response_has_no_body(
    tmp_path,
):
    port = _reserve_port()
    server = create_loopback_server(
        _config(tmp_path, port),
        _FlakyApplication(),
    )
    thread = _start_server(server)

    try:
        status, headers, body = _request(
            port,
            method="HEAD",
        )

        assert status == 500
        assert body == b""
        assert int(headers["Content-Length"]) == len(
            b"Internal Server Error"
        )
    finally:
        _stop_server(server, thread)


def test_d5_invalid_shutdown_is_diagnosed(
    tmp_path,
):
    port = _reserve_port()
    server = create_loopback_server(
        _config(tmp_path, port),
        _FlakyApplication(),
    )

    try:
        with pytest.raises(
            RuntimeError,
            match="not serving",
        ):
            server.shutdown()

        diagnostics = server.diagnostics_snapshot()

        assert diagnostics.fault_count == 1
        assert diagnostics.recent_faults[-1].code is (
            RuntimeFaultCode.SHUTDOWN_FAILURE
        )
        assert diagnostics.lifecycle_state == "READY"
    finally:
        server.server_close()


def test_d5_initial_diagnostics_are_clean(
    tmp_path,
):
    port = _reserve_port()
    server = create_loopback_server(
        _config(tmp_path, port),
        _FlakyApplication(),
    )

    try:
        diagnostics = server.diagnostics_snapshot()

        assert diagnostics.lifecycle_state == "READY"
        assert diagnostics.host == "127.0.0.1"
        assert diagnostics.port == port
        assert diagnostics.active_request_count == 0
        assert diagnostics.rejected_request_count == 0
        assert diagnostics.fault_count == 0
        assert diagnostics.recent_faults == ()
    finally:
        server.server_close()
