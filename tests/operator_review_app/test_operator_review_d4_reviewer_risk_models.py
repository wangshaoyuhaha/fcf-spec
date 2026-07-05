import json

from operator_review_app import (
    RISK_ACKNOWLEDGEMENT_PENDING,
    RISK_ACKNOWLEDGEMENT_STATUS,
    build_paper_review_record_from_ui_source,
    build_reviewer_note_record,
    build_risk_acknowledgement_record,
    load_ui_app_source_payload,
    validate_reviewer_note_record,
    validate_risk_acknowledgement_record,
)


def _build_review_record(tmp_path):
    source_file = tmp_path / "ui_report.json"
    source_file.write_text(
        json.dumps(
            {
                "report_id": "UI-REPORT-D4",
                "stage_id": "UI-APP-D6",
                "candidate_count": 4,
                "operator_review_required": True,
            }
        ),
        encoding="utf-8",
    )
    source = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_local_report_artifact",
    )
    return build_paper_review_record_from_ui_source(
        source,
        review_record_id="REVIEW-D4-001",
    )


def test_operator_review_d4_builds_reviewer_note_record(tmp_path):
    review_record = _build_review_record(tmp_path)

    note = build_reviewer_note_record(
        review_record,
        reviewer_note="Reviewed on paper only. Needs more source confirmation.",
    )

    assert note.review_record_id == "REVIEW-D4-001"
    assert note.reviewer_note == "Reviewed on paper only. Needs more source confirmation."
    assert note.paper_only is True
    assert note.local_only is True
    assert note.read_only is True
    assert note.note_is_trade_instruction is False
    assert note.trade_action_enabled is False
    assert note.real_execution_allowed is False
    assert validate_reviewer_note_record(note) == []


def test_operator_review_d4_builds_risk_acknowledgement_record(tmp_path):
    review_record = _build_review_record(tmp_path)

    acknowledgement = build_risk_acknowledgement_record(
        review_record,
        acknowledged_risk_flags=["DATA_LIMITED", "HIGH_VOLATILITY"],
        risk_acknowledgement=True,
    )

    assert acknowledgement.review_record_id == "REVIEW-D4-001"
    assert acknowledgement.risk_acknowledgement is True
    assert acknowledgement.acknowledgement_status == RISK_ACKNOWLEDGEMENT_STATUS
    assert acknowledgement.acknowledged_risk_flags == ("DATA_LIMITED", "HIGH_VOLATILITY")
    assert acknowledgement.acknowledgement_is_trade_instruction is False
    assert acknowledgement.trade_action_enabled is False
    assert acknowledgement.real_execution_allowed is False
    assert acknowledgement.operator_review_bypass_allowed is False
    assert validate_risk_acknowledgement_record(acknowledgement) == []


def test_operator_review_d4_supports_pending_risk_acknowledgement(tmp_path):
    review_record = _build_review_record(tmp_path)

    acknowledgement = build_risk_acknowledgement_record(
        review_record,
        acknowledged_risk_flags=[],
        risk_acknowledgement=False,
    )

    assert acknowledgement.risk_acknowledgement is False
    assert acknowledgement.acknowledgement_status == RISK_ACKNOWLEDGEMENT_PENDING
    assert acknowledgement.acknowledged_risk_flags == ()
    assert validate_risk_acknowledgement_record(acknowledgement) == []


def test_operator_review_d4_rejects_note_that_becomes_trade_instruction(tmp_path):
    review_record = _build_review_record(tmp_path)
    note = build_reviewer_note_record(review_record, reviewer_note="paper note")

    unsafe_note = note.__class__(
        review_record_id=note.review_record_id,
        reviewer_note=note.reviewer_note,
        note_is_trade_instruction=True,
    )

    assert "note_is_trade_instruction must be false" in validate_reviewer_note_record(unsafe_note)
