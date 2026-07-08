from sidecars.archive_correlation_rollup_app_1 import (
    classify_artifact_path,
    discover_rollup_source_paths,
    is_rollup_source_path,
)


def test_d2_classifies_control_center():
    assert (
        classify_artifact_path("docs/FCF_PROJECT_CONTROL_CENTER.md")
        == "control_center"
    )


def test_d2_classifies_final_current_state():
    assert (
        classify_artifact_path("FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md")
        == "final_current_state"
    )


def test_d2_classifies_audit_report():
    assert (
        classify_artifact_path("FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md")
        == "archive_report"
    )


def test_d2_rejects_runtime_file_as_source_of_truth():
    assert (
        is_rollup_source_path("runtime/operator_console/ai_learning_audit_report.json")
        is False
    )


def test_d2_discovers_unique_sorted_rollup_sources():
    paths = [
        "runtime/operator_console/ai_learning_audit_report.json",
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    ]

    assert discover_rollup_source_paths(paths) == (
        "FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
    )
