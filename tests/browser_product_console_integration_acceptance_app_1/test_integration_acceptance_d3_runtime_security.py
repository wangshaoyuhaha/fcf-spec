import socket
import time
from http.client import HTTPConnection
from threading import Thread
from types import MappingProxyType

import pytest

from apps.browser_product_console_integration_acceptance_app_1 import (
    INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY,
    INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX,
)
from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    ConsoleRuntimeConfig,
    RuntimeFaultCode,
    RuntimeFaultLedger,
    RuntimeHardeningLimits,
    RuntimeLifecycleState,
    assess_runtime_request,
    create_loopback_server,
    host_header_is_valid,
)


_SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": (
        "default-src 'self'; style-src 'unsafe-inline'"
    ),
}


def _application() -> BrowserProductConsoleApplication:
    model = ConsoleReadModel(
        correlation_id="corr-d3-runtime-acceptance",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )
    return BrowserProductConsoleApplication(model)


def _reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def _start_server(server):
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.monotonic() + 3.0

    while time.monotonic() < deadline:
        if server.lifecycle_state is RuntimeLifecycleState.SERVING:
            return thread
        time.sleep(0.01)

    raise AssertionError("server did not enter SERVING state")


def _request(port: int, method: str, target: str):
    connection = HTTPConnection("127.0.0.1", port, timeout=3.0)

    try:
        connection.putrequest(
            method,
            target,
            skip_host=True,
            skip_accept_encoding=True,
        )
        connection.putheader("Host", f"127.0.0.1:{port}")
        connection.endheaders()
        response = connection.getresponse()
        body = response.read()
        return response.status, dict(response.getheaders()), body
    finally:
        connection.close()


def test_d3_matrix_and_fixtures_cover_runtime_negative_acceptance():
    rows = tuple(
        row
        for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
        if row.delivery_stage == "D3"
    )

    assert tuple(row.matrix_id for row in rows) == (
        "RUNTIME_SECURITY",
        "RUNTIME_FAULT_ISOLATION",
    )
    assert {
        fixture.fixture_id
        for fixture in INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY
        if fixture.source_kind == "RUNTIME_PROBE"
    } == {
        "NEGATIVE_PATH_FIXTURE",
        "FAULT_ISOLATION_FIXTURE",
    }


@pytest.mark.parametrize(
    ("method", "target", "headers", "status", "reason"),
    (
        (
            "POST",
            "/evidence",
            (("Host", "127.0.0.1:8765"),),
            405,
            "UNSUPPORTED_HTTP_METHOD",
        ),
        (
            "GET",
            "http://example.com/evidence",
            (("Host", "127.0.0.1:8765"),),
            400,
            "ABSOLUTE_REQUEST_TARGET",
        ),
        (
            "GET",
            "/evidence",
            (
                ("Host", "127.0.0.1:8765"),
                ("Content-Length", "1"),
            ),
            413,
            "REQUEST_BODY_PRESENT",
        ),
        (
            "GET",
            "/evidence",
            (
                ("Host", "127.0.0.1:8765"),
                ("Transfer-Encoding", "chunked"),
            ),
            400,
            "UNSUPPORTED_TRANSFER_ENCODING",
        ),
    ),
)
def test_d3_runtime_request_boundaries_fail_closed(
    method,
    target,
    headers,
    status,
    reason,
):
    result = assess_runtime_request(method, target, headers)

    assert result.accepted is False
    assert result.status == status
    assert result.reason_code == reason


def test_d3_loopback_host_authority_remains_exact():
    assert host_header_is_valid(("127.0.0.1:8765",), 8765)
    assert host_header_is_valid(("localhost:8765",), 8765)
    assert not host_header_is_valid(("0.0.0.0:8765",), 8765)
    assert not host_header_is_valid(("example.com:8765",), 8765)
    assert not host_header_is_valid((), 8765)


def test_d3_request_size_and_header_limits_are_deterministic():
    limits = RuntimeHardeningLimits(
        request_target_max_bytes=256,
        header_count_max=8,
        header_line_max_bytes=1024,
    )

    target_result = assess_runtime_request(
        "GET",
        "/" + ("x" * 256),
        (("Host", "127.0.0.1:8765"),),
        limits,
    )
    header_count_result = assess_runtime_request(
        "GET",
        "/evidence",
        tuple((f"X-Test-{index}", "v") for index in range(9)),
        limits,
    )
    header_line_result = assess_runtime_request(
        "GET",
        "/evidence",
        (("X-Long", "x" * 1024),),
        limits,
    )

    assert (target_result.status, target_result.reason_code) == (
        414,
        "REQUEST_TARGET_EXCEEDED",
    )
    assert (header_count_result.status, header_count_result.reason_code) == (
        431,
        "HEADER_COUNT_EXCEEDED",
    )
    assert (header_line_result.status, header_line_result.reason_code) == (
        431,
        "HEADER_LINE_EXCEEDED",
    )


@pytest.mark.parametrize(
    ("target", "status"),
    (
        ("/missing", 404),
        ("/../audit", 404),
        ("/%2e%2e/audit", 404),
        ("/evidence?type=%00", 400),
    ),
)
def test_d3_application_negative_paths_fail_closed(target, status):
    response = _application().dispatch("GET", target)

    assert response.status == status
    assert dict(response.headers).get("Cache-Control") == "no-store"


def test_d3_write_methods_remain_unavailable_at_application_boundary():
    application = _application()

    for method in ("POST", "PUT", "PATCH", "DELETE"):
        response = application.dispatch(method, "/evidence")

        assert response.status == 405
        assert dict(response.headers)["Cache-Control"] == "no-store"
        assert response.body == b"Method Not Allowed"


def test_d3_http_runtime_applies_security_headers_to_all_outcomes(tmp_path):
    port = _reserve_port()
    server = create_loopback_server(
        ConsoleRuntimeConfig(
            allowed_root=tmp_path,
            host="127.0.0.1",
            port=port,
        ),
        _application(),
    )
    thread = _start_server(server)

    try:
        for method, target, expected_status in (
            ("GET", "/health", 200),
            ("GET", "/missing", 404),
            ("POST", "/evidence", 405),
        ):
            status, headers, _ = _request(port, method, target)

            assert status == expected_status
            for name, value in _SECURITY_HEADERS.items():
                assert headers[name] == value
    finally:
        server.shutdown()
        thread.join(timeout=3.0)
        server.server_close()

    assert not thread.is_alive()
    assert server.lifecycle_state is RuntimeLifecycleState.CLOSED


def test_d3_fault_diagnostics_are_bounded_and_sanitized():
    ledger = RuntimeFaultLedger(capacity=2)

    for code in (
        RuntimeFaultCode.APPLICATION_DISPATCH_FAILURE,
        RuntimeFaultCode.REQUEST_HANDLER_FAILURE,
        RuntimeFaultCode.SHUTDOWN_FAILURE,
    ):
        ledger.record(code, "SERVING")

    snapshot = ledger.snapshot(
        lifecycle_state="SERVING",
        host="127.0.0.1",
        port=8765,
        active_request_count=0,
        rejected_request_count=1,
    )

    assert snapshot.fault_count == 3
    assert tuple(item.sequence for item in snapshot.recent_faults) == (2, 3)
    assert tuple(item.message for item in snapshot.recent_faults) == (
        "request handler failed",
        "server shutdown failed",
    )
    assert all("Traceback" not in item.message for item in snapshot.recent_faults)
    assert snapshot.paper_only is True
    assert snapshot.local_only is True
    assert snapshot.loopback_only is True
    assert snapshot.read_only is True
    assert snapshot.operator_review_required is True


def test_d3_healthy_probe_remains_available_after_negative_probes():
    application = _application()

    assert application.dispatch("POST", "/health").status == 405
    assert application.dispatch("GET", "/missing").status == 404

    health = application.dispatch("GET", "/health")

    assert health.status == 200
    assert b'"mode": "paper-only"' in health.body
    assert b'"host_scope": "loopback-only"' in health.body
    assert b'"operator_review_required": true' in health.body
