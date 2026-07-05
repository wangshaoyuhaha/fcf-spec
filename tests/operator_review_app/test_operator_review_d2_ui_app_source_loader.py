import json

from operator_review_app import (
    ALLOWED_UI_SOURCE_TYPES,
    load_ui_app_source_payload,
    summarize_ui_app_source_payload,
)


def test_operator_review_d2_loads_ui_app_local_report_artifact(tmp_path):
    source_file = tmp_path / "ui_report.json"
    source_file.write_text(
        json.dumps(
            {
                "report_id": "UI-REPORT-001",
                "stage_id": "UI-APP-D6",
                "candidate_count": 2,
                "ranked_watchlist": [],
                "risk_flags": ["DATA_LIMITED"],
                "reason_codes": ["VOLUME_PRICE_SIGNAL"],
                "operator_review_required": True,
            }
        ),
        encoding="utf-8",
    )

    loaded = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_local_report_artifact",
    )

    assert loaded.source_exists is True
    assert loaded.load_errors == ()
    assert loaded.paper_only is True
    assert loaded.read_only is True
    assert loaded.trade_action_enabled is False
    assert loaded.real_execution_allowed is False

    summary = summarize_ui_app_source_payload(loaded)
    assert summary["source_report_id"] == "UI-REPORT-001"
    assert summary["source_stage_id"] == "UI-APP-D6"
    assert summary["candidate_count"] == 2
    assert summary["has_ranked_watchlist"] is True
    assert summary["has_risk_flags"] is True
    assert summary["has_reason_codes"] is True
    assert summary["operator_review_required"] is True


def test_operator_review_d2_rejects_unapproved_source_type(tmp_path):
    source_file = tmp_path / "bad.json"
    source_file.write_text("{}", encoding="utf-8")

    loaded = load_ui_app_source_payload(
        source_file,
        source_type="trade_instruction_payload",
    )

    assert loaded.source_exists is True
    assert any("source_type is not allowed" in item for item in loaded.load_errors)
    assert "trade_instruction_payload" not in ALLOWED_UI_SOURCE_TYPES


def test_operator_review_d2_reports_missing_source_without_execution():
    loaded = load_ui_app_source_payload(
        "missing-ui-report.json",
        source_type="ui_app_workflow_handoff",
    )

    assert loaded.source_exists is False
    assert loaded.payload == {}
    assert loaded.trade_action_enabled is False
    assert loaded.real_execution_allowed is False
    assert any("source file does not exist" in item for item in loaded.load_errors)
