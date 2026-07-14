from __future__ import annotations

import socket
import time
from http.client import HTTPConnection
from threading import Thread
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    ConsoleRuntimeConfig,
    HardenedLoopbackHTTPServer,
    RuntimeLifecycleSnapshot,
    RuntimeLifecycleState,
    create_hardened_loopback_server,
    create_loopback_server,
    host_header_is_valid,
    normalize_loopback_host_authority,
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
        correlation_id="corr-runtime-hardening-d2",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )

    return BrowserProductConsoleApplication(model)


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
        "server did not reach state "
        f"{expected.value}; "
        f"actual={server.lifecycle_state.value}"
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


def _shutdown_server(server, thread):
    server.shutdown()
    thread.join(timeout=3.0)

    assert not thread.is_alive()
    assert (
        server.lifecycle_state
        is RuntimeLifecycleState.STOPPED
    )


def _request(
    port,
    *,
    method="GET",
    path="/health",
    host_headers=(),
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

        for value in host_headers:
            connection.putheader(
                "Host",
                value,
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


@pytest.mark.parametrize(
    "authority",
    (
        "127.0.0.1",
        "127.0.0.1:8765",
        "localhost",
        "LOCALHOST:8765",
    ),
)
def test_d2_loopback_host_authority_is_normalized(
    authority,
):
    normalized = normalize_loopback_host_authority(
        authority,
        8765,
    )

    assert normalized in {
        "127.0.0.1:8765",
        "localhost:8765",
    }


@pytest.mark.parametrize(
    "authority",
    (
        "",
        " ",
        " localhost",
        "localhost ",
        "localhost:8766",
        "localhost:http",
        "example.com",
        "0.0.0.0",
        "127.0.0.2",
        "127.0.0.1,example.com",
        "user@127.0.0.1",
        "127.0.0.1/path",
        "[::1]",
        "::1",
    ),
)
def test_d2_invalid_host_authority_is_rejected(
    authority,
):
    with pytest.raises(ValueError):
        normalize_loopback_host_authority(
            authority,
            8765,
        )


def test_d2_host_header_requires_exactly_one_value():
    assert host_header_is_valid(
        ("127.0.0.1:8765",),
        8765,
    )

    assert not host_header_is_valid(
        (),
        8765,
    )

    assert not host_header_is_valid(
        (
            "127.0.0.1:8765",
            "localhost:8765",
        ),
        8765,
    )

    assert not host_header_is_valid(
        "127.0.0.1:8765",
        8765,
    )


def test_d2_lifecycle_snapshot_is_strict():
    snapshot = RuntimeLifecycleSnapshot(
        state=RuntimeLifecycleState.READY,
        host="127.0.0.1",
        port=8765,
    )

    assert snapshot.state is RuntimeLifecycleState.READY
    assert snapshot.host == "127.0.0.1"
    assert snapshot.port == 8765

    with pytest.raises(ValueError):
        RuntimeLifecycleSnapshot(
            state="READY",
            host="127.0.0.1",
            port=8765,
        )


def test_d2_server_binds_exact_loopback_and_closes(
    tmp_path,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )

    try:
        assert isinstance(
            server,
            HardenedLoopbackHTTPServer,
        )
        assert server.server_address == (
            "127.0.0.1",
            port,
        )
        assert (
            server.lifecycle_state
            is RuntimeLifecycleState.READY
        )

        snapshot = server.lifecycle_snapshot()

        assert snapshot.state is RuntimeLifecycleState.READY
        assert snapshot.host == "127.0.0.1"
        assert snapshot.port == port
    finally:
        server.server_close()

    assert (
        server.lifecycle_state
        is RuntimeLifecycleState.CLOSED
    )


@pytest.mark.parametrize(
    "host_factory",
    (
        lambda port: f"127.0.0.1:{port}",
        lambda port: f"localhost:{port}",
    ),
)
def test_d2_valid_loopback_host_reaches_application(
    tmp_path,
    host_factory,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )
    thread = _start_server(server)

    try:
        status, headers, body = _request(
            port,
            host_headers=(host_factory(port),),
        )

        assert status == 200
        assert b'"status": "ok"' in body
        assert headers["Cache-Control"] == "no-store"
        assert (
            headers["X-Content-Type-Options"]
            == "nosniff"
        )
    finally:
        _shutdown_server(server, thread)
        server.server_close()

    assert (
        server.lifecycle_state
        is RuntimeLifecycleState.CLOSED
    )


@pytest.mark.parametrize(
    "host_value",
    (
        "example.com",
        "0.0.0.0",
        "127.0.0.1:1",
    ),
)
def test_d2_invalid_host_fails_before_dispatch(
    tmp_path,
    host_value,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )
    thread = _start_server(server)

    try:
        status, headers, body = _request(
            port,
            host_headers=(host_value,),
        )

        assert status == 400
        assert body == b"Bad Request"
        assert headers["Cache-Control"] == "no-store"
        assert (
            headers["X-Content-Type-Options"]
            == "nosniff"
        )
        assert headers["Connection"] == "close"
    finally:
        _shutdown_server(server, thread)
        server.server_close()


def test_d2_duplicate_host_headers_fail_closed(
    tmp_path,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )
    thread = _start_server(server)

    try:
        status, _, body = _request(
            port,
            host_headers=(
                f"127.0.0.1:{port}",
                f"localhost:{port}",
            ),
        )

        assert status == 400
        assert body == b"Bad Request"
    finally:
        _shutdown_server(server, thread)
        server.server_close()


def test_d2_invalid_head_has_no_response_body(
    tmp_path,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )
    thread = _start_server(server)

    try:
        status, headers, body = _request(
            port,
            method="HEAD",
            host_headers=("example.com",),
        )

        assert status == 400
        assert body == b""
        assert int(headers["Content-Length"]) == len(
            b"Bad Request"
        )
    finally:
        _shutdown_server(server, thread)
        server.server_close()


def test_d2_port_collision_is_deterministic(
    tmp_path,
):
    port = _reserve_port()
    config = _config(tmp_path, port)

    first = create_loopback_server(
        config,
        _application(),
    )

    try:
        with pytest.raises(
            RuntimeError,
            match="loopback port is unavailable",
        ):
            create_loopback_server(
                config,
                _application(),
            )
    finally:
        first.server_close()


def test_d2_server_supports_controlled_restart(
    tmp_path,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )

    first_thread = _start_server(server)

    status, _, _ = _request(
        port,
        host_headers=(f"127.0.0.1:{port}",),
    )

    assert status == 200

    _shutdown_server(
        server,
        first_thread,
    )

    second_thread = _start_server(server)

    try:
        status, _, _ = _request(
            port,
            host_headers=(f"localhost:{port}",),
        )

        assert status == 200
    finally:
        _shutdown_server(
            server,
            second_thread,
        )
        server.server_close()

    assert (
        server.lifecycle_state
        is RuntimeLifecycleState.CLOSED
    )


def test_d2_shutdown_before_serving_is_rejected(
    tmp_path,
):
    port = _reserve_port()

    server = create_loopback_server(
        _config(tmp_path, port),
        _application(),
    )

    try:
        with pytest.raises(
            RuntimeError,
            match="not serving",
        ):
            server.shutdown()
    finally:
        server.server_close()


def test_d2_factory_rejects_non_loopback_binding():
    class Handler:
        pass

    with pytest.raises(
        ValueError,
        match="exactly 127.0.0.1",
    ):
        create_hardened_loopback_server(
            "0.0.0.0",
            8765,
            Handler,
        )
