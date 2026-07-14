from __future__ import annotations

import socket
import time
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler
from threading import Event, Thread
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    ConsoleRuntimeConfig,
    RuntimeHardeningLimits,
    RuntimeLifecycleState,
    RuntimeRequestAssessment,
    assess_runtime_request,
    create_hardened_loopback_server,
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


def _application():
    model = ConsoleReadModel(
        correlation_id="corr-runtime-hardening-d3",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )

    return BrowserProductConsoleApplication(model)


def _start_server(server):
    thread = Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    deadline = time.monotonic() + 3.0

    while time.monotonic() < deadline:
        if (
            server.lifecycle_state
            is RuntimeLifecycleState.SERVING
        ):
            return thread
        time.sleep(0.01)

    raise AssertionError(
        "server did not enter SERVING state"
    )


def _stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=3.0)

    assert not thread.is_alive()

    server.server_close()

    assert (
        server.lifecycle_state
        is RuntimeLifecycleState.CLOSED
    )


def _request(
    port,
    *,
    method="GET",
    path="/health",
    headers=(),
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

        for name, value in headers:
            connection.putheader(name, value)

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


def _valid_headers():
    return (
        (
            "Host",
            "127.0.0.1:8765",
        ),
    )


def test_d3_request_assessment_accepts_get_and_head():
    for method in ("GET", "HEAD"):
        result = assess_runtime_request(
            method,
            "/health?view=summary",
            _valid_headers(),
        )

        assert isinstance(
            result,
            RuntimeRequestAssessment,
        )
        assert result.accepted
        assert result.status == 200
        assert result.reason_code == "ACCEPTED"


@pytest.mark.parametrize(
    "method",
    (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "TRACE",
        "CONNECT",
        "BREW",
    ),
)
def test_d3_unsupported_methods_fail_with_405(
    method,
):
    result = assess_runtime_request(
        method,
        "/health",
        _valid_headers(),
    )

    assert not result.accepted
    assert result.status == 405
    assert result.reason_code == (
        "UNSUPPORTED_HTTP_METHOD"
    )
    assert result.response_headers == (
        (
            "Allow",
            "GET, HEAD",
        ),
    )


@pytest.mark.parametrize(
    "target",
    (
        "",
        " health",
        "http://example.com/health",
        "//example.com/health",
        "/health#fragment",
        "/health\t",
        "/health\x00",
    ),
)
def test_d3_malformed_request_target_fails_closed(
    target,
):
    result = assess_runtime_request(
        "GET",
        target,
        _valid_headers(),
    )

    assert not result.accepted
    assert result.status == 400


def test_d3_oversized_request_target_returns_414():
    limits = RuntimeHardeningLimits(
        request_target_max_bytes=256,
    )

    result = assess_runtime_request(
        "GET",
        "/" + ("a" * 256),
        _valid_headers(),
        limits,
    )

    assert not result.accepted
    assert result.status == 414
    assert result.reason_code == (
        "REQUEST_TARGET_EXCEEDED"
    )


def test_d3_header_count_limit_returns_431():
    limits = RuntimeHardeningLimits(
        header_count_max=8,
    )

    headers = tuple(
        (f"X-Test-{index}", "value")
        for index in range(9)
    )

    result = assess_runtime_request(
        "GET",
        "/health",
        headers,
        limits,
    )

    assert not result.accepted
    assert result.status == 431
    assert result.reason_code == (
        "HEADER_COUNT_EXCEEDED"
    )


def test_d3_header_line_limit_returns_431():
    limits = RuntimeHardeningLimits(
        header_line_max_bytes=1024,
    )

    result = assess_runtime_request(
        "GET",
        "/health",
        (
            (
                "X-Long",
                "x" * 1024,
            ),
        ),
        limits,
    )

    assert not result.accepted
    assert result.status == 431
    assert result.reason_code == (
        "HEADER_LINE_EXCEEDED"
    )


@pytest.mark.parametrize(
    ("headers", "status", "reason_code"),
    (
        (
            (
                ("Host", "127.0.0.1:8765"),
                ("Content-Length", "1"),
            ),
            413,
            "REQUEST_BODY_PRESENT",
        ),
        (
            (
                ("Host", "127.0.0.1:8765"),
                ("Content-Length", "invalid"),
            ),
            400,
            "INVALID_CONTENT_LENGTH",
        ),
        (
            (
                ("Host", "127.0.0.1:8765"),
                ("Content-Length", "0"),
                ("Content-Length", "0"),
            ),
            400,
            "AMBIGUOUS_CONTENT_LENGTH",
        ),
        (
            (
                ("Host", "127.0.0.1:8765"),
                ("Transfer-Encoding", "chunked"),
            ),
            400,
            "UNSUPPORTED_TRANSFER_ENCODING",
        ),
        (
            (
                ("Host", "127.0.0.1:8765"),
                ("Expect", "100-continue"),
            ),
            417,
            "EXPECTATION_NOT_SUPPORTED",
        ),
    ),
)
def test_d3_request_body_boundary_is_fail_closed(
    headers,
    status,
    reason_code,
):
    result = assess_runtime_request(
        "GET",
        "/health",
        headers,
    )

    assert not result.accepted
    assert result.status == status
    assert result.reason_code == reason_code


def test_d3_server_rejects_get_request_body(
    tmp_path,
):
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
        status, headers, body = _request(
            port,
            headers=(
                (
                    "Host",
                    f"127.0.0.1:{port}",
                ),
                (
                    "Content-Length",
                    "1",
                ),
            ),
        )

        assert status == 413
        assert body == b"Payload Too Large"
        assert headers["Cache-Control"] == "no-store"
        assert (
            headers["X-Content-Type-Options"]
            == "nosniff"
        )
        assert headers["Connection"] == "close"
    finally:
        _stop_server(server, thread)


@pytest.mark.parametrize(
    "method",
    (
        "POST",
        "OPTIONS",
        "TRACE",
        "BREW",
    ),
)
def test_d3_server_rejects_any_unsupported_method(
    tmp_path,
    method,
):
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
        status, headers, body = _request(
            port,
            method=method,
            headers=(
                (
                    "Host",
                    f"localhost:{port}",
                ),
            ),
        )

        assert status == 405
        assert body == b"Method Not Allowed"
        assert headers["Allow"] == "GET, HEAD"
        assert headers["Cache-Control"] == "no-store"
        assert headers["Connection"] == "close"
    finally:
        _stop_server(server, thread)


def test_d3_server_applies_socket_timeout():
    observed_timeout = []

    class TimeoutHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            observed_timeout.append(
                self.connection.gettimeout()
            )
            body = b"ok"
            self.send_response(200)
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.send_header(
                "Connection",
                "close",
            )
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def log_message(
            self,
            format,
            *args,
        ):
            return

    port = _reserve_port()
    limits = RuntimeHardeningLimits(
        socket_timeout_seconds=0.5,
    )

    server = create_hardened_loopback_server(
        "127.0.0.1",
        port,
        TimeoutHandler,
        limits=limits,
    )
    thread = _start_server(server)

    try:
        status, _, body = _request(
            port,
            headers=(
                (
                    "Host",
                    f"127.0.0.1:{port}",
                ),
            ),
        )

        assert status == 200
        assert body == b"ok"
        assert observed_timeout == [0.5]

        deadline = time.monotonic() + 3.0

        while time.monotonic() < deadline:
            if server.active_request_count == 0:
                break
            time.sleep(0.01)

        assert server.active_request_count == 0
    finally:
        _stop_server(server, thread)


def test_d3_concurrency_limit_returns_503():
    entered = Event()
    release = Event()

    class BlockingHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            entered.set()

            if not release.wait(timeout=3.0):
                raise RuntimeError(
                    "test handler release timed out"
                )

            body = b"ok"
            self.send_response(200)
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.send_header(
                "Connection",
                "close",
            )
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def log_message(
            self,
            format,
            *args,
        ):
            return

    port = _reserve_port()
    limits = RuntimeHardeningLimits(
        max_concurrent_requests=1,
        socket_timeout_seconds=2.0,
    )

    server = create_hardened_loopback_server(
        "127.0.0.1",
        port,
        BlockingHandler,
        limits=limits,
    )
    thread = _start_server(server)

    first = socket.create_connection(
        ("127.0.0.1", port),
        timeout=3.0,
    )
    second = None

    try:
        first.sendall(
            (
                f"GET / HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{port}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode("ascii")
        )

        assert entered.wait(timeout=3.0)

        second = socket.create_connection(
            ("127.0.0.1", port),
            timeout=3.0,
        )
        second.sendall(
            (
                f"GET / HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{port}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode("ascii")
        )

        response = b""

        while True:
            chunk = second.recv(4096)

            if not chunk:
                break

            response += chunk

        assert (
            b"503 Service Unavailable"
            in response
        )
        assert b"Cache-Control: no-store" in response

        assert server.active_request_count == 1
        assert server.rejected_request_count == 1
        assert server.max_concurrent_requests == 1

        release.set()

        first_response = b""

        while True:
            chunk = first.recv(4096)

            if not chunk:
                break

            first_response += chunk

        assert b"200 OK" in first_response

        deadline = time.monotonic() + 3.0

        while time.monotonic() < deadline:
            if (
                server.active_request_count
                == 0
            ):
                break
            time.sleep(0.01)

        assert (
            server.active_request_count
            == 0
        )
    finally:
        release.set()
        first.close()

        if second is not None:
            second.close()

        _stop_server(server, thread)
