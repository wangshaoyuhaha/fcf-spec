from __future__ import annotations

import hashlib
import socket
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS,
    REQUIRED_RUNTIME_HARDENING_THREAT_IDS,
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    RuntimeFaultCode,
    RuntimeFaultLedger,
    RuntimeLifecycleState,
    assess_runtime_request,
    build_evidence_audit_explorer_integration_acceptance,
    build_research_workspace_integration_acceptance,
    create_hardened_loopback_server,
    host_header_is_valid,
    normalize_loopback_host_authority,
    normalize_registered_relative_path,
    read_runtime_artifact_snapshot,
)


def _model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-runtime-hardening-d6-final",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )


def _application() -> BrowserProductConsoleApplication:
    return BrowserProductConsoleApplication(_model())


def _reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


def _create_server():
    last_error = None

    for _ in range(10):
        try:
            return create_hardened_loopback_server(
                "127.0.0.1",
                _reserve_port(),
                _NoopHandler,
            )
        except RuntimeError as exc:
            last_error = exc

    raise AssertionError(
        "unable to reserve a loopback test port"
    ) from last_error


class _NoopHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def test_d6_hardening_contract_and_threat_registry_are_final():
    contract = BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT
    boundary = BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY
    limits = BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS

    assert contract.status == "IMPLEMENTED"
    assert contract.allowed_http_methods == ("GET", "HEAD")
    assert contract.successor_phase == (
        "BROWSER-PRODUCT-CONSOLE-INTEGRATION-ACCEPTANCE-APP-1"
    )
    assert tuple(
        control.threat_id
        for control in BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS
    ) == REQUIRED_RUNTIME_HARDENING_THREAT_IDS
    assert {
        control.detection_stage
        for control in BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS
    } == {"D2", "D3", "D4", "D5"}

    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.read_only_presentation is True
    assert boundary.operator_review_required is True
    assert boundary.fail_closed_required is True
    assert boundary.command_dispatch_allowed is False
    assert boundary.workflow_dispatch_allowed is False
    assert boundary.external_network_binding_allowed is False
    assert boundary.real_execution_allowed is False
    assert boundary.automatic_approval_allowed is False

    assert limits.request_body_max_bytes == 0
    assert limits.max_concurrent_requests >= 1
    assert limits.artifact_max_bytes >= 1024


def test_d6_host_and_http_boundaries_fail_closed():
    limits = BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    host_values = ("127.0.0.1:8765",)
    valid_headers = (("Host", "127.0.0.1:8765"),)

    assert normalize_loopback_host_authority(
        "127.0.0.1:8765",
        8765,
    ) == "127.0.0.1:8765"
    assert normalize_loopback_host_authority(
        "localhost:8765",
        8765,
    ) == "localhost:8765"
    assert host_header_is_valid(host_values, 8765) is True
    assert host_header_is_valid(
        ("0.0.0.0:8765",),
        8765,
    ) is False

    accepted = assess_runtime_request(
        "GET",
        "/evidence",
        valid_headers,
        limits,
    )
    assert accepted.accepted is True
    assert accepted.status == 200

    method_rejected = assess_runtime_request(
        "POST",
        "/evidence",
        valid_headers,
        limits,
    )
    assert method_rejected.accepted is False
    assert method_rejected.status == 405
    assert method_rejected.reason_code == "UNSUPPORTED_HTTP_METHOD"

    body_rejected = assess_runtime_request(
        "GET",
        "/evidence",
        (
            ("Host", "127.0.0.1:8765"),
            ("Content-Length", "1"),
        ),
        limits,
    )
    assert body_rejected.accepted is False
    assert body_rejected.status == 413
    assert body_rejected.reason_code == "REQUEST_BODY_PRESENT"

    oversized = "/" + (
        "a" * limits.request_target_max_bytes
    )
    target_rejected = assess_runtime_request(
        "GET",
        oversized,
        valid_headers,
        limits,
    )
    assert target_rejected.accepted is False
    assert target_rejected.status == 414


def test_d6_registered_artifact_integrity_fails_closed(
    tmp_path: Path,
):
    root = tmp_path / "registered"
    root.mkdir()
    artifact = root / "artifact.json"
    content = b'{"paper_only":true}'
    artifact.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()

    assert normalize_registered_relative_path(
        "evidence/artifact.json"
    ) == "evidence/artifact.json"

    with pytest.raises(
        ValueError,
        match="outside the allowed root",
    ):
        normalize_registered_relative_path(
            "../artifact.json"
        )

    snapshot = read_runtime_artifact_snapshot(
        artifact,
        root,
        expected_sha256=digest,
    )
    assert snapshot.content == content
    assert snapshot.content_sha256 == digest
    assert snapshot.size_bytes == len(content)

    with pytest.raises(
        ValueError,
        match="SHA-256 mismatch",
    ):
        read_runtime_artifact_snapshot(
            artifact,
            root,
            expected_sha256="0" * 64,
        )

    outside = tmp_path / "outside.json"
    outside.write_bytes(content)

    with pytest.raises(
        ValueError,
        match="outside the allowed root",
    ):
        read_runtime_artifact_snapshot(
            outside,
            root,
        )


def test_d6_diagnostics_are_bounded_and_sanitized():
    ledger = RuntimeFaultLedger(capacity=2)

    ledger.record(
        RuntimeFaultCode.APPLICATION_DISPATCH_FAILURE,
        "SERVING",
    )
    ledger.record(
        RuntimeFaultCode.REQUEST_HANDLER_FAILURE,
        "SERVING",
    )
    ledger.record(
        RuntimeFaultCode.SHUTDOWN_FAILURE,
        "STOPPING",
    )

    snapshot = ledger.snapshot(
        lifecycle_state="FAILED",
        host="127.0.0.1",
        port=8765,
        active_request_count=0,
        rejected_request_count=1,
    )

    assert snapshot.fault_count == 3
    assert len(snapshot.recent_faults) == 2
    assert tuple(
        record.sequence
        for record in snapshot.recent_faults
    ) == (2, 3)
    assert tuple(
        record.code
        for record in snapshot.recent_faults
    ) == (
        RuntimeFaultCode.REQUEST_HANDLER_FAILURE,
        RuntimeFaultCode.SHUTDOWN_FAILURE,
    )
    assert all(
        "Traceback" not in record.message
        and "\\" not in record.message
        for record in snapshot.recent_faults
    )
    assert snapshot.paper_only is True
    assert snapshot.local_only is True
    assert snapshot.loopback_only is True
    assert snapshot.read_only is True
    assert snapshot.operator_review_required is True


def test_d6_lifecycle_failure_is_recorded_without_serving():
    server = _create_server()

    try:
        assert server.lifecycle_state is RuntimeLifecycleState.READY

        with pytest.raises(
            RuntimeError,
            match="not serving",
        ):
            server.shutdown()

        failed_snapshot = server.diagnostics_snapshot()
        assert failed_snapshot.fault_count == 1
        assert failed_snapshot.recent_faults[-1].code is (
            RuntimeFaultCode.SHUTDOWN_FAILURE
        )
    finally:
        server.server_close()

    closed_snapshot = server.diagnostics_snapshot()
    assert closed_snapshot.lifecycle_state == "CLOSED"
    assert closed_snapshot.host == "127.0.0.1"


def test_d6_product_acceptances_remain_passed():
    application = _application()

    research = build_research_workspace_integration_acceptance(
        application
    )
    evidence = (
        build_evidence_audit_explorer_integration_acceptance(
            application
        )
    )

    assert research.status == "PASSED"
    assert research.ok is True
    assert all(research.checks.values())
    assert evidence.status == "PASSED"
    assert evidence.ok is True
    assert all(evidence.checks.values())


def test_d6_runtime_surface_remains_read_only_and_local():
    application = _application()

    health = application.dispatch("GET", "/health")
    body = health.body.decode("utf-8")

    assert health.status == 200
    assert '"mode": "paper-only"' in body
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body

    assert application.dispatch("POST", "/").status == 405
    assert application.dispatch("PUT", "/evidence").status == 405
    assert application.dispatch("GET", "/../audit").status == 404
    assert application.dispatch(
        "GET",
        "/%2e%2e/audit",
    ).status == 404
