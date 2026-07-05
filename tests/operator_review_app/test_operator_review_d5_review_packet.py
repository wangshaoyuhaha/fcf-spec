import json

from operator_review_app import (
    build_local_review_packet,
    build_no_execution_receipt,
    build_paper_review_record_from_ui_source,
    build_reviewer_note_record,
    build_risk_acknowledgement_record,
    load_ui_app_source_payload,
    validate_local_review_packet,
    validate_no_execution_receipt,
    write_local_review_packet,
)


def _build_packet_parts(tmp_path):
    source_file = tmp_path / "ui_report.json"
    source_file.write_text(
        json.dumps(
            {
                "report_id": "UI-REPORT-D5",
                "stage_id": "UI-APP-D6",
                "candidate_count": 5,
                "operator_review_required": True,
            }
        ),
        encoding="utf-8",
    )
    source = load_ui_app_source_payload(
        source_file,
        source_type="ui_app_local_report_artifact",
    )
    review_record = build_paper_review_record_from_ui_source(
        source,
        review_record_id="REVIEW-D5-001",
    )
    reviewer_note = build_reviewer_note_record(
        review_record,
        reviewer_note="Paper review packet test note.",
    )
    risk_acknowledgement = build_risk_acknowledgement_record(
        review_record,
        acknowledged_risk_flags=["DATA_LIMITED"],
        risk_acknowledgement=True,
    )
    return review_record, reviewer_note, risk_acknowledgement


def test_operator_review_d5_builds_no_execution_receipt(tmp_path):
    review_record, _, _ = _build_packet_parts(tmp_path)

    receipt = build_no_execution_receipt(review_record)

    assert receipt.review_record_id == "REVIEW-D5-001"
    assert receipt.no_execution_receipt is True
    assert receipt.paper_only is True
    assert receipt.local_only is True
    assert receipt.read_only is True
    assert receipt.real_execution_allowed is False
    assert receipt.trade_action_enabled is False
    assert receipt.buy_button_enabled is False
    assert receipt.sell_button_enabled is False
    assert receipt.order_button_enabled is False
    assert receipt.broker_connection_allowed is False
    assert receipt.exchange_connection_allowed is False
    assert receipt.operator_review_bypass_allowed is False
    assert validate_no_execution_receipt(receipt) == []


def test_operator_review_d5_builds_local_review_packet(tmp_path):
    review_record, reviewer_note, risk_acknowledgement = _build_packet_parts(tmp_path)

    packet = build_local_review_packet(
        packet_id="PACKET-D5-001",
        review_record=review_record,
        reviewer_note=reviewer_note,
        risk_acknowledgement=risk_acknowledgement,
    )

    assert packet.packet_id == "PACKET-D5-001"
    assert packet.review_record.review_record_id == "REVIEW-D5-001"
    assert packet.no_execution_receipt.no_execution_receipt is True
    assert packet.paper_only is True
    assert packet.local_only is True
    assert packet.read_only is True
    assert packet.real_execution_allowed is False
    assert packet.trade_action_enabled is False
    assert packet.operator_review_bypass_allowed is False
    assert validate_local_review_packet(packet) == []


def test_operator_review_d5_writes_local_review_packet_json(tmp_path):
    review_record, reviewer_note, risk_acknowledgement = _build_packet_parts(tmp_path)

    packet = build_local_review_packet(
        packet_id="PACKET-D5-002",
        review_record=review_record,
        reviewer_note=reviewer_note,
        risk_acknowledgement=risk_acknowledgement,
    )

    output_path = tmp_path / "operator_review_packet.json"
    written = write_local_review_packet(packet, output_path)

    assert written == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["packet_id"] == "PACKET-D5-002"
    assert loaded["no_execution_receipt"]["no_execution_receipt"] is True
    assert loaded["real_execution_allowed"] is False
    assert loaded["trade_action_enabled"] is False


def test_operator_review_d5_rejects_mismatched_nested_review_ids(tmp_path):
    review_record, reviewer_note, risk_acknowledgement = _build_packet_parts(tmp_path)
    bad_receipt = build_no_execution_receipt(review_record).__class__(
        review_record_id="OTHER-REVIEW-ID"
    )

    packet = build_local_review_packet(
        packet_id="PACKET-D5-003",
        review_record=review_record,
        reviewer_note=reviewer_note,
        risk_acknowledgement=risk_acknowledgement,
        no_execution_receipt=bad_receipt,
    )

    assert "nested review_record_id values must match" in validate_local_review_packet(packet)
