from types import MappingProxyType

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleArtifactRecord,
    ConsoleReadModel,
    DataWorkspaceItem,
    RegisteredConsoleArtifact,
    build_data_workspace_model,
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
        content_sha256="a" * 64,
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
        correlation_id="corr-d2",
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


def test_d2_artifact_index_accepts_registered_data_types():
    for artifact_type in ("data_snapshot", "data_quality"):
        artifact = RegisteredConsoleArtifact(
            artifact_id=f"{artifact_type}-1",
            artifact_type=artifact_type,
            correlation_id="corr-d2",
            relative_path=f"{artifact_type}.json",
            content_sha256="b" * 64,
        )
        assert artifact.artifact_type == artifact_type


def test_d2_overview_counts_are_deterministic():
    model = _model(
        (
            _record(
                "snapshot-1",
                "data_snapshot",
                {"status": "READY"},
            ),
            _record(
                "quality-1",
                "data_quality",
                {"status": "PASS_STRICT"},
            ),
        )
    )

    overview = build_overview_workspace_model(model)

    assert overview.registered_artifact_count == 2
    assert dict(overview.artifact_type_counts) == {
        "data_quality": 1,
        "data_snapshot": 1,
    }
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


def test_d2_data_workspace_available_with_snapshot_and_quality():
    model = _model(
        (
            _record(
                "snapshot-1",
                "data_snapshot",
                {"as_of": "2026-07-14T00:00:00Z"},
            ),
            _record(
                "quality-1",
                "data_quality",
                {"status": "PASS_STRICT"},
            ),
        )
    )

    workspace = build_data_workspace_model(model)

    assert workspace.state == "AVAILABLE"
    assert tuple(item.artifact_id for item in workspace.items) == (
        "snapshot-1",
        "quality-1",
    )
    assert dict(workspace.artifact_type_counts) == {
        "data_quality": 1,
        "data_snapshot": 1,
    }


def test_d2_data_workspace_incomplete_with_one_data_type():
    workspace = build_data_workspace_model(
        _model(
            (
                _record(
                    "snapshot-1",
                    "data_snapshot",
                    {"status": "READY"},
                ),
            )
        )
    )

    assert workspace.state == "INCOMPLETE"


def test_d2_data_workspace_explicit_empty_state():
    workspace = build_data_workspace_model(_model(()))

    assert workspace.state == "NO_REGISTERED_DATA"
    assert workspace.items == ()


def test_d2_data_workspace_item_rejects_non_data_type():
    try:
        DataWorkspaceItem(
            artifact_id="watchlist-1",
            artifact_type="ranked_watchlist",
            relative_path="watchlist.json",
            content_sha256="c" * 64,
            payload={},
        )
    except ValueError as error:
        assert "unsupported Data Workspace artifact type" in str(error)
    else:
        raise AssertionError("non-data artifact type was accepted")


def test_d2_data_route_renders_registered_artifacts():
    application = BrowserProductConsoleApplication(
        _model(
            (
                _record(
                    "snapshot-1",
                    "data_snapshot",
                    {"source": "registered_local_fixture"},
                ),
                _record(
                    "quality-1",
                    "data_quality",
                    {"status": "PASS_STRICT"},
                ),
            )
        )
    )

    response = application.dispatch("GET", "/data")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "Data Workspace" in body
    assert "AVAILABLE" in body
    assert "snapshot-1" in body
    assert "quality-1" in body
    assert "PASS_STRICT" in body
    assert "registered-artifact-only" in body.lower()


def test_d2_data_route_escapes_payload_text():
    application = BrowserProductConsoleApplication(
        _model(
            (
                _record(
                    "snapshot-1",
                    "data_snapshot",
                    {"unsafe": "<script>alert(1)</script>"},
                ),
            )
        )
    )

    body = application.dispatch("GET", "/data").body.decode("utf-8")

    assert "<script>" not in body
    assert "&lt;script&gt;" in body


def test_d2_overview_route_reports_available_and_planned_workspaces():
    application = BrowserProductConsoleApplication(_model(()))

    body = application.dispatch("GET", "/").body.decode("utf-8")

    assert "Available: 11" in body
    assert "Planned: 0" in body
    assert 'href="/data"' in body


def test_d2_write_method_remains_rejected():
    response = BrowserProductConsoleApplication(_model(())).dispatch(
        "POST",
        "/data",
    )

    assert response.status == 405
    assert response.body == b"Method Not Allowed"
