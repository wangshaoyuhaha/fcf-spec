from market_scenario_app.review_packet import (
    STAGE_ID,
    build_no_execution_receipt,
    build_scenario_review_packet,
    is_valid_scenario_review_packet,
    validate_no_execution_receipt,
    validate_scenario_review_packet,
)


def _definition():
    return {
        "scenario_id": "scenario-001",
        "scenario_label": "Liquidity stress paper review",
        "scenario_type": "liquidity_stress",
        "operator_review_required": True,
        "real_execution_allowed": False,
    }


def _assumption():
    return {
        "assumption_id": "assumption-001",
        "scenario_id": "scenario-001",
        "assumption_type": "liquidity",
        "operator_review_required": True,
        "trade_instruction_allowed": False,
        "real_execution_allowed": False,
    }


def _risk_context():
    return {
        "risk_context_id": "risk-001",
        "scenario_id": "scenario-001",
        "risk_level": "HIGH",
        "risk_flags": ["REVIEW_REQUIRED"],
        "operator_review_required": True,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
    }


def _source_record():
    return {
        "source_id": "source-001",
        "source_kind": "report_archive_outputs",
        "relative_path": "runtime/report_archive_app/archive_packet.json",
        "content_read_allowed": False,
        "source_content_mutation_allowed": False,
    }


def test_no_execution_receipt_forbids_execution_and_trade_ui():
    receipt = build_no_execution_receipt("packet-001").to_dict()

    assert validate_no_execution_receipt(receipt) == []
    assert receipt["operator_review_required"] is True
    assert receipt["trade_action_enabled"] is False
    assert receipt["buy_button_enabled"] is False
    assert receipt["sell_button_enabled"] is False
    assert receipt["order_button_enabled"] is False
    assert receipt["real_execution_allowed"] is False


def test_build_valid_scenario_review_packet():
    packet = build_scenario_review_packet(
        packet_id="packet-001",
        scenario_id="scenario-001",
        scenario_summary="Paper-only liquidity stress review packet.",
        scenario_definitions=[_definition()],
        assumptions=[_assumption()],
        risk_contexts=[_risk_context()],
        source_metadata_records=[_source_record()],
        data_sources=["local_report_archive"],
        notes="Operator review required.",
        generated_at_utc="2026-01-01T00:00:00+00:00",
    )

    assert is_valid_scenario_review_packet(packet) is True
    assert packet.stage_id == STAGE_ID
    assert packet.operator_review_required is True
    assert packet.safety_flags["scenario_packet_as_order_ticket"] is False
    assert packet.safety_flags["real_execution_allowed"] is False


def test_scenario_review_packet_serializable_dict():
    packet = build_scenario_review_packet(
        packet_id="packet-002",
        scenario_id="scenario-002",
        scenario_summary="Paper-only base case review.",
        scenario_definitions=[_definition()],
        assumptions=[_assumption()],
        risk_contexts=[_risk_context()],
        source_metadata_records=[_source_record()],
        data_sources=["local_ops_packet"],
        generated_at_utc="2026-01-01T00:00:00+00:00",
    )

    payload = packet.to_dict()

    assert payload["packet_id"] == "packet-002"
    assert payload["stage_id"] == STAGE_ID
    assert payload["no_execution_receipt"]["real_execution_allowed"] is False


def test_review_packet_requires_operator_review():
    packet = build_scenario_review_packet(
        packet_id="packet-003",
        scenario_id="scenario-003",
        scenario_summary="Paper-only risk review.",
        scenario_definitions=[_definition()],
        assumptions=[_assumption()],
        risk_contexts=[_risk_context()],
        source_metadata_records=[_source_record()],
        data_sources=["local_review"],
    )

    assert packet.packet_status == "OPERATOR_REVIEW_REQUIRED"
    assert packet.operator_review_required is True
    assert packet.no_execution_receipt["operator_review_required"] is True


def test_invalid_packet_missing_required_sections_is_rejected():
    packet = build_scenario_review_packet(
        packet_id="packet-004",
        scenario_id="scenario-004",
        scenario_summary="Paper-only review.",
        scenario_definitions=[],
        assumptions=[],
        risk_contexts=[],
        source_metadata_records=[],
        data_sources=[],
    )

    errors = validate_scenario_review_packet(packet)

    assert "scenario_definitions_required" in errors
    assert "assumptions_required" in errors
    assert "risk_contexts_required" in errors
    assert "source_metadata_records_required" in errors
    assert "data_sources_required" in errors


def test_packet_status_must_be_review_status():
    packet = build_scenario_review_packet(
        packet_id="packet-005",
        scenario_id="scenario-005",
        scenario_summary="Paper-only review.",
        scenario_definitions=[_definition()],
        assumptions=[_assumption()],
        risk_contexts=[_risk_context()],
        source_metadata_records=[_source_record()],
        data_sources=["local"],
        packet_status="EXECUTE_ORDER",
    )

    assert "invalid_packet_status" in validate_scenario_review_packet(packet)


def test_packet_text_must_not_be_trade_instruction():
    packet = build_scenario_review_packet(
        packet_id="packet-006",
        scenario_id="scenario-006",
        scenario_summary="Buy now and place order.",
        scenario_definitions=[_definition()],
        assumptions=[_assumption()],
        risk_contexts=[_risk_context()],
        source_metadata_records=[_source_record()],
        data_sources=["local"],
        notes="Execute order immediately.",
    )

    errors = validate_scenario_review_packet(packet)

    assert "scenario_summary_must_not_be_trade_instruction" in errors
    assert "notes_must_not_be_trade_instruction" in errors
