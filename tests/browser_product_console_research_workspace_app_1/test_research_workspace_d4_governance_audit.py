from types import MappingProxyType

from apps.browser_product_console_runtime_app_1 import (
    AuditHistoryItem,
    BrowserProductConsoleApplication,
    ConsoleArtifactRecord,
    ConsoleReadModel,
    GovernanceWorkspaceItem,
    RegisteredConsoleArtifact,
    build_audit_history_workspace_model,
    build_governance_workspace_model,
    build_overview_workspace_model,
)


def _record(
    artifact_id: str,
    artifact_type: str,
    payload: dict,
) -> ConsoleArtifactRecord:
    return ConsoleArtifactRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        relative_path=f"registered/{artifact_id}.json",
        content_sha256="2" * 64,
        payload=payload,
    )


def _model(
    records: tuple[ConsoleArtifactRecord, ...],
) -> ConsoleReadModel:
    sections = {}
    for record in records:
        sections.setdefault(record.artifact_type, []).append(
            dict(record.payload)
        )
    return ConsoleReadModel(
        correlation_id="corr-d4",
        candidates=(),
        sections=MappingProxyType(
            {
                key: tuple(value)
                for key, value in sorted(sections.items())
            }
        ),
        source_artifact_ids=tuple(
            record.artifact_id for record in records
        ),
        artifact_records=records,
    )


def test_d4_artifact_index_accepts_governance_and_audit_types():
    for artifact_type in (
        "model_governance",
        "policy_snapshot",
        "audit_receipt",
        "manifest",
    ):
        artifact = RegisteredConsoleArtifact(
            artifact_id=f"{artifact_type}-1",
            artifact_type=artifact_type,
            correlation_id="corr-d4",
            relative_path=f"{artifact_type}.json",
            content_sha256="3" * 64,
        )
        assert artifact.artifact_type == artifact_type


def test_d4_overview_reports_all_workspaces_available():
    overview = build_overview_workspace_model(_model(()))

    assert overview.available_workspace_paths == (
        "/",
        "/data",
        "/stocks",
        "/runs",
        "/ai-comparison",
        "/risk",
        "/validation",
        "/review",
        "/reports",
        "/governance",
        "/audit",
    )
    assert overview.planned_workspace_paths == ()


def test_d4_governance_available_with_model_and_policy():
    workspace = build_governance_workspace_model(
        _model(
            (
                _record(
                    "model-1",
                    "model_governance",
                    {
                        "model_name": "deterministic-engine",
                        "model_version": "v1",
                        "governance_status": "APPROVED_FOR_PAPER_REVIEW",
                    },
                ),
                _record(
                    "policy-1",
                    "policy_snapshot",
                    {
                        "policy_name": "paper-boundary",
                        "policy_version": "v3",
                        "policy_status": "ACTIVE",
                    },
                ),
            )
        )
    )

    assert workspace.state == "AVAILABLE"
    assert tuple(item.subject for item in workspace.items) == (
        "deterministic-engine",
        "paper-boundary",
    )
    assert tuple(item.decision for item in workspace.items) == (
        "APPROVED_FOR_PAPER_REVIEW",
        "ACTIVE",
    )


def test_d4_governance_explicit_incomplete_and_empty_states():
    incomplete = build_governance_workspace_model(
        _model(
            (
                _record(
                    "policy-1",
                    "policy_snapshot",
                    {"policy_name": "paper-boundary"},
                ),
            )
        )
    )
    empty = build_governance_workspace_model(_model(()))

    assert incomplete.state == "INCOMPLETE"
    assert empty.state == "NO_REGISTERED_GOVERNANCE"


def test_d4_governance_item_rejects_non_governance_type():
    try:
        GovernanceWorkspaceItem(
            artifact_id="run-1",
            artifact_type="research_run",
            relative_path="run.json",
            content_sha256="4" * 64,
            subject="run",
            version="v1",
            decision="PASS",
            payload={},
        )
    except ValueError as error:
        assert "unsupported Governance artifact type" in str(error)
    else:
        raise AssertionError("non-governance artifact type was accepted")


def test_d4_governance_route_renders_and_escapes_payloads():
    application = BrowserProductConsoleApplication(
        _model(
            (
                _record(
                    "model-1",
                    "model_governance",
                    {
                        "model_name": "deterministic-engine",
                        "model_version": "v1",
                        "governance_status": "REVIEW_REQUIRED",
                        "unsafe": "<script>alert(1)</script>",
                    },
                ),
                _record(
                    "policy-1",
                    "policy_snapshot",
                    {
                        "policy_name": "paper-boundary",
                        "policy_version": "v3",
                        "policy_status": "ACTIVE",
                    },
                ),
            )
        )
    )

    response = application.dispatch("GET", "/governance")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "Governance" in body
    assert "AVAILABLE" in body
    assert "deterministic-engine" in body
    assert "paper-boundary" in body
    assert "<script>" not in body
    assert "&lt;script&gt;" in body


def test_d4_audit_history_available_with_receipt_and_manifest():
    workspace = build_audit_history_workspace_model(
        _model(
            (
                _record(
                    "receipt-1",
                    "audit_receipt",
                    {
                        "receipt_id": "receipt-event-1",
                        "created_at_utc": "2026-07-14T00:00:00Z",
                        "action": "OPERATOR_REVIEW_RECORDED",
                        "actor": "operator-1",
                    },
                ),
                _record(
                    "manifest-1",
                    "manifest",
                    {
                        "manifest_id": "manifest-event-1",
                        "timestamp_utc": "2026-07-14T00:01:00Z",
                        "status": "ARCHIVED",
                        "producer": "archive-sidecar",
                    },
                ),
            )
        )
    )

    assert workspace.state == "AVAILABLE"
    assert tuple(item.event_id for item in workspace.items) == (
        "receipt-event-1",
        "manifest-event-1",
    )
    assert tuple(item.actor for item in workspace.items) == (
        "operator-1",
        "archive-sidecar",
    )


def test_d4_audit_history_explicit_incomplete_and_empty_states():
    incomplete = build_audit_history_workspace_model(
        _model(
            (
                _record(
                    "receipt-1",
                    "audit_receipt",
                    {"receipt_id": "receipt-event-1"},
                ),
            )
        )
    )
    empty = build_audit_history_workspace_model(_model(()))

    assert incomplete.state == "INCOMPLETE"
    assert empty.state == "NO_REGISTERED_AUDIT_HISTORY"


def test_d4_audit_item_rejects_non_audit_type():
    try:
        AuditHistoryItem(
            artifact_id="policy-1",
            artifact_type="policy_snapshot",
            relative_path="policy.json",
            content_sha256="5" * 64,
            event_id="event-1",
            event_time="2026-07-14T00:00:00Z",
            action="ACTIVE",
            actor="policy-sidecar",
            payload={},
        )
    except ValueError as error:
        assert "unsupported Audit History artifact type" in str(error)
    else:
        raise AssertionError("non-audit artifact type was accepted")


def test_d4_audit_route_renders_registered_history():
    application = BrowserProductConsoleApplication(
        _model(
            (
                _record(
                    "receipt-1",
                    "audit_receipt",
                    {
                        "receipt_id": "receipt-event-1",
                        "created_at_utc": "2026-07-14T00:00:00Z",
                        "action": "OPERATOR_REVIEW_RECORDED",
                        "actor": "operator-1",
                    },
                ),
                _record(
                    "manifest-1",
                    "manifest",
                    {
                        "manifest_id": "manifest-event-1",
                        "timestamp_utc": "2026-07-14T00:01:00Z",
                        "status": "ARCHIVED",
                        "producer": "archive-sidecar",
                    },
                ),
            )
        )
    )

    response = application.dispatch("GET", "/audit")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "Audit History" in body
    assert "AVAILABLE" in body
    assert "receipt-event-1" in body
    assert "manifest-event-1" in body
    assert "append-only" in body


def test_d4_new_routes_support_head_without_body():
    application = BrowserProductConsoleApplication(_model(()))

    assert application.dispatch("HEAD", "/governance").body == b""
    assert application.dispatch("HEAD", "/audit").body == b""


def test_d4_new_routes_reject_write_methods():
    application = BrowserProductConsoleApplication(_model(()))

    assert application.dispatch("POST", "/governance").status == 405
    assert application.dispatch("DELETE", "/audit").status == 405
