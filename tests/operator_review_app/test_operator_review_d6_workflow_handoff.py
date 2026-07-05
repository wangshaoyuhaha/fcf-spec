import json

from operator_review_app import (
    FINAL_CLOSEOUT_STATUS,
    OPERATOR_REVIEW_FINAL_STAGE_ID,
    build_final_operator_review_handoff,
    build_local_review_packet,
    build_operator_review_closeout_summary,
    build_paper_review_record_from_ui_source,
    build_reviewer_note_record,
    build_risk_acknowledgement_record,
    load_ui_app_source_payload,
    validate_final_operator_review_handoff,
    write_final_operator_review_handoff,
)


def _build_local_packet(tmp_path):
    source_file = tmp_path / "ui_report.json"
    source_file.write_text(
        json.dumps(
            {
                "report_id": "UI-REPORT-D6",
                "stage_id": "UI-APP-D6",
                "candidate_count": 6,
                "operator_review_required": True,
            }
        ),
        encoding="utf-8",
    )
    source = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_workflow_handoff",
    )
    review_record = build_paper_review_record_from_ui_source(
        source,
        review_record_id="REVIEW-D6-001",
    )
    reviewer_note = build_reviewer_note_record(
        review_record,
        reviewer_note="Final handoff remains paper-only.",
    )
    risk_acknowledgement = build_risk_acknowledgement_record(
        review_record,
        acknowledged_risk_flags=["DATA_LIMITED", "OPERATOR_REVIEW_REQUIRED"],
        risk_acknowledgement=True,
    )
    return build_local_review_packet(
        packet_id="LOCAL-PACKET-D6-001",
        review_record=review_record,
        reviewer_note=reviewer_note,
        risk_acknowledgement=risk_acknowledgement,
    )


def test_operator_review_d6_builds_final_handoff(tmp_path):
    local_packet = _build_local_packet(tmp_path)

    handoff = build_final_operator_review_handoff(
        handoff_id="FINAL-HANDOFF-D6-001",
        local_review_packet=local_packet,
    )

    assert handoff.handoff_id == "FINAL-HANDOFF-D6-001"
    assert handoff.stage_id == OPERATOR_REVIEW_FINAL_STAGE_ID
    assert handoff.source_packet_id == "LOCAL-PACKET-D6-001"
    assert handoff.closeout_status == FINAL_CLOSEOUT_STATUS
    assert handoff.paper_only is True
    assert handoff.local_only is True
    assert handoff.read_only is True
    assert handoff.sidecar_only is True
    assert handoff.operator_review_required is True
    assert handoff.operator_review_bypass_allowed is False
    assert validate_final_operator_review_handoff(handoff) == []


def test_operator_review_d6_final_handoff_forbids_execution_and_deploy(tmp_path):
    local_packet = _build_local_packet(tmp_path)

    handoff = build_final_operator_review_handoff(
        handoff_id="FINAL-HANDOFF-D6-002",
        local_review_packet=local_packet,
    )

    assert handoff.real_execution_allowed is False
    assert handoff.trade_action_enabled is False
    assert handoff.buy_button_enabled is False
    assert handoff.sell_button_enabled is False
    assert handoff.order_button_enabled is False
    assert handoff.broker_connection_allowed is False
    assert handoff.exchange_connection_allowed is False
    assert handoff.credential_storage_allowed is False
    assert handoff.wallet_private_key_access_allowed is False
    assert handoff.real_account_access_allowed is False
    assert handoff.real_position_access_allowed is False
    assert handoff.core_mutation_allowed is False
    assert handoff.p48_core_expansion_allowed is False
    assert handoff.tag_created is False
    assert handoff.release_created is False
    assert handoff.deployed is False


def test_operator_review_d6_builds_closeout_summary(tmp_path):
    local_packet = _build_local_packet(tmp_path)
    handoff = build_final_operator_review_handoff(
        handoff_id="FINAL-HANDOFF-D6-003",
        local_review_packet=local_packet,
    )

    summary = build_operator_review_closeout_summary(handoff)

    assert summary["app_id"] == "OPERATOR-REVIEW-APP-1"
    assert summary["stage_id"] == "OPERATOR-REVIEW-D6"
    assert summary["closeout_status"] == FINAL_CLOSEOUT_STATUS
    assert summary["completed_stages"] == [
        "OPERATOR-REVIEW-D1",
        "OPERATOR-REVIEW-D2",
        "OPERATOR-REVIEW-D3",
        "OPERATOR-REVIEW-D4",
        "OPERATOR-REVIEW-D5",
        "OPERATOR-REVIEW-D6",
    ]
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
    assert summary["tag_created"] is False
    assert summary["release_created"] is False
    assert summary["deployed"] is False


def test_operator_review_d6_writes_final_handoff_json(tmp_path):
    local_packet = _build_local_packet(tmp_path)
    handoff = build_final_operator_review_handoff(
        handoff_id="FINAL-HANDOFF-D6-004",
        local_review_packet=local_packet,
    )

    output_path = tmp_path / "final_handoff.json"
    written = write_final_operator_review_handoff(handoff, output_path)

    assert written == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["handoff_id"] == "FINAL-HANDOFF-D6-004"
    assert loaded["stage_id"] == "OPERATOR-REVIEW-D6"
    assert loaded["real_execution_allowed"] is False
    assert loaded["trade_action_enabled"] is False
    assert loaded["deployed"] is False
