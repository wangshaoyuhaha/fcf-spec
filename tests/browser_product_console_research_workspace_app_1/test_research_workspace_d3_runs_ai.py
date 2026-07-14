from types import MappingProxyType

from apps.browser_product_console_runtime_app_1 import (
    AIComparisonItem,
    BrowserProductConsoleApplication,
    ConsoleArtifactRecord,
    ConsoleReadModel,
    RegisteredConsoleArtifact,
    ResearchRunWorkspaceItem,
    build_ai_comparison_workspace_model,
    build_overview_workspace_model,
    build_research_runs_workspace_model,
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
        content_sha256="d" * 64,
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
        correlation_id="corr-d3",
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


def test_d3_artifact_index_accepts_run_and_ai_types():
    for artifact_type in (
        "research_run",
        "workflow_status",
        "ai_evaluation",
    ):
        artifact = RegisteredConsoleArtifact(
            artifact_id=f"{artifact_type}-1",
            artifact_type=artifact_type,
            correlation_id="corr-d3",
            relative_path=f"{artifact_type}.json",
            content_sha256="e" * 64,
        )
        assert artifact.artifact_type == artifact_type


def test_d3_overview_reports_new_routes_available():
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


def test_d3_research_runs_available_with_run_and_status():
    workspace = build_research_runs_workspace_model(
        _model(
            (
                _record(
                    "run-1",
                    "research_run",
                    {
                        "run_id": "paper-run-1",
                        "status": "COMPLETED",
                    },
                ),
                _record(
                    "status-1",
                    "workflow_status",
                    {
                        "workflow_id": "paper-run-1",
                        "workflow_status": "REVIEW_REQUIRED",
                    },
                ),
            )
        )
    )

    assert workspace.state == "AVAILABLE"
    assert tuple(item.run_id for item in workspace.items) == (
        "paper-run-1",
        "paper-run-1",
    )
    assert tuple(item.workflow_state for item in workspace.items) == (
        "COMPLETED",
        "REVIEW_REQUIRED",
    )


def test_d3_research_runs_explicit_incomplete_and_empty_states():
    incomplete = build_research_runs_workspace_model(
        _model(
            (
                _record(
                    "run-1",
                    "research_run",
                    {"run_id": "paper-run-1"},
                ),
            )
        )
    )
    empty = build_research_runs_workspace_model(_model(()))

    assert incomplete.state == "INCOMPLETE"
    assert empty.state == "NO_REGISTERED_RUNS"


def test_d3_research_run_item_rejects_non_run_type():
    try:
        ResearchRunWorkspaceItem(
            artifact_id="quality-1",
            artifact_type="data_quality",
            relative_path="quality.json",
            content_sha256="f" * 64,
            run_id="run-1",
            workflow_state="PASS",
            payload={},
        )
    except ValueError as error:
        assert "unsupported Research Runs artifact type" in str(error)
    else:
        raise AssertionError("non-run artifact type was accepted")


def test_d3_runs_route_renders_and_escapes_registered_payloads():
    application = BrowserProductConsoleApplication(
        _model(
            (
                _record(
                    "run-1",
                    "research_run",
                    {
                        "run_id": "paper-run-1",
                        "status": "COMPLETED",
                        "unsafe": "<script>alert(1)</script>",
                    },
                ),
                _record(
                    "status-1",
                    "workflow_status",
                    {
                        "workflow_id": "paper-run-1",
                        "workflow_status": "REVIEW_REQUIRED",
                    },
                ),
            )
        )
    )

    response = application.dispatch("GET", "/runs")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "Research Runs" in body
    assert "AVAILABLE" in body
    assert "paper-run-1" in body
    assert "REVIEW_REQUIRED" in body
    assert "<script>" not in body
    assert "&lt;script&gt;" in body


def test_d3_ai_comparison_ready_with_explanation_and_evaluation():
    workspace = build_ai_comparison_workspace_model(
        _model(
            (
                _record(
                    "explanation-1",
                    "ai_explanation",
                    {
                        "model_name": "advisory-model-a",
                        "prompt_version": "prompt-v1",
                        "status": "GENERATED",
                    },
                ),
                _record(
                    "evaluation-1",
                    "ai_evaluation",
                    {
                        "evaluator_model": "evaluator-model-b",
                        "prompt_id": "evaluation-prompt-v2",
                        "evaluation_status": "PASS_WITH_REVIEW",
                    },
                ),
            )
        )
    )

    assert workspace.state == "COMPARISON_READY"
    assert tuple(item.model_label for item in workspace.items) == (
        "evaluator-model-b",
        "advisory-model-a",
    )
    assert tuple(item.evaluation_state for item in workspace.items) == (
        "PASS_WITH_REVIEW",
        "GENERATED",
    )


def test_d3_ai_comparison_explicit_incomplete_and_empty_states():
    incomplete = build_ai_comparison_workspace_model(
        _model(
            (
                _record(
                    "explanation-1",
                    "ai_explanation",
                    {"model_name": "advisory-model-a"},
                ),
            )
        )
    )
    empty = build_ai_comparison_workspace_model(_model(()))

    assert incomplete.state == "INCOMPLETE"
    assert empty.state == "NO_REGISTERED_AI_ARTIFACTS"


def test_d3_ai_comparison_item_rejects_non_ai_type():
    try:
        AIComparisonItem(
            artifact_id="run-1",
            artifact_type="research_run",
            relative_path="run.json",
            content_sha256="1" * 64,
            model_label="model-a",
            prompt_version="prompt-v1",
            evaluation_state="PASS",
            payload={},
        )
    except ValueError as error:
        assert "unsupported AI Comparison artifact type" in str(error)
    else:
        raise AssertionError("non-AI artifact type was accepted")


def test_d3_ai_comparison_route_renders_advisory_boundary():
    application = BrowserProductConsoleApplication(
        _model(
            (
                _record(
                    "explanation-1",
                    "ai_explanation",
                    {
                        "model_name": "advisory-model-a",
                        "prompt_version": "prompt-v1",
                        "status": "GENERATED",
                    },
                ),
                _record(
                    "evaluation-1",
                    "ai_evaluation",
                    {
                        "evaluator_model": "evaluator-model-b",
                        "prompt_id": "evaluation-prompt-v2",
                        "evaluation_status": "PASS_WITH_REVIEW",
                    },
                ),
            )
        )
    )

    response = application.dispatch("GET", "/ai-comparison")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "AI Comparison" in body
    assert "COMPARISON_READY" in body
    assert "advisory-model-a" in body
    assert "evaluator-model-b" in body
    assert "advisory-only" in body


def test_d3_new_routes_support_head_without_body():
    application = BrowserProductConsoleApplication(_model(()))

    assert application.dispatch("HEAD", "/runs").body == b""
    assert application.dispatch("HEAD", "/ai-comparison").body == b""


def test_d3_new_routes_reject_write_methods():
    application = BrowserProductConsoleApplication(_model(()))

    assert application.dispatch("POST", "/runs").status == 405
    assert application.dispatch("PATCH", "/ai-comparison").status == 405
