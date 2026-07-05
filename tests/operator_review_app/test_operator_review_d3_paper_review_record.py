import json

from operator_review_app import (
    PAPER_DECISION_LABEL_UNDECIDED,
    REVIEW_STATUS_PENDING,
    build_paper_review_record_from_ui_source,
    load_ui_app_source_payload,
    validate_paper_review_record,
)


def test_operator_review_d3_builds_paper_review_record_from_ui_source(tmp_path):
    source_file = tmp_path / "ui_handoff.json"
    source_file.write_text(
        json.dumps(
            {
                "report_id": "UI-REPORT-002",
                "stage_id": "UI-APP-D6",
                "candidate_count": 3,
                "operator_review_required": True,
            }
        ),
        encoding="utf-8",
    )

    source = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_workflow_handoff",
    )
    record = build_paper_review_record_from_ui_source(
        source,
        review_record_id="REVIEW-001",
    )

    assert record.review_record_id == "REVIEW-001"
    assert record.source_report_id == "UI-REPORT-002"
    assert record.source_stage_id == "UI-APP-D6"
    assert record.candidate_count == 3
    assert record.review_status == REVIEW_STATUS_PENDING
    assert record.paper_decision_label == PAPER_DECISION_LABEL_UNDECIDED
    assert record.operator_review_required is True
    assert validate_paper_review_record(record) == []


def test_operator_review_d3_record_forbids_trade_and_execution_flags(tmp_path):
    source_file = tmp_path / "ui_report.json"
    source_file.write_text(
        json.dumps({"report_id": "UI-REPORT-003", "stage_id": "UI-APP-D6"}),
        encoding="utf-8",
    )

    source = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_local_report_artifact",
    )
    record = build_paper_review_record_from_ui_source(
        source,
        review_record_id="REVIEW-002",
        paper_decision_label="PAPER_WATCH_ONLY",
    )

    assert record.review_status_is_trade_action is False
    assert record.paper_decision_label_is_trade_action is False
    assert record.real_execution_allowed is False
    assert record.trade_action_enabled is False
    assert record.buy_button_enabled is False
    assert record.sell_button_enabled is False
    assert record.order_button_enabled is False
    assert record.broker_connection_allowed is False
    assert record.exchange_connection_allowed is False
    assert record.core_mutation_allowed is False
    assert record.p48_core_expansion_allowed is False
    assert validate_paper_review_record(record) == []


def test_operator_review_d3_rejects_disallowed_status_and_label(tmp_path):
    source_file = tmp_path / "ui_report.json"
    source_file.write_text(
        json.dumps({"report_id": "UI-REPORT-004", "stage_id": "UI-APP-D6"}),
        encoding="utf-8",
    )

    source = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_local_report_artifact",
    )
    record = build_paper_review_record_from_ui_source(
        source,
        review_record_id="REVIEW-003",
        review_status="BUY_NOW",
        paper_decision_label="EXECUTE_ORDER",
    )

    errors = validate_paper_review_record(record)
    assert "review_status is not allowed" in errors
    assert "paper_decision_label is not allowed" in errors
