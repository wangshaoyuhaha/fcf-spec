from backtest_review_app.risk_summary import (
    STAGE_ID,
    backtest_risk_summary_schema,
    build_backtest_risk_item,
    build_backtest_risk_summary,
    is_valid_backtest_risk_item,
    is_valid_backtest_risk_summary,
    validate_backtest_risk_item,
    validate_backtest_risk_summary,
)


def _risk_item_payload():
    return build_backtest_risk_item(
        risk_id="risk-001",
        review_id="review-001",
        result_packet_id="packet-001",
        risk_category="sample_size",
        risk_level="HIGH",
        description="Sample size is limited and requires paper-only review.",
        evidence_metric_ids=["metric-001"],
        mitigation_note="Escalate to operator review before downstream use.",
    ).to_dict()


def test_backtest_risk_summary_schema_identity_and_safety_flags():
    schema = backtest_risk_summary_schema()
    flags = schema["safety_flags"]

    assert schema["stage_id"] == STAGE_ID
    assert schema["schema_name"] == "backtest_risk_summary"
    assert flags["paper_only"] is True
    assert flags["local_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["real_execution_allowed"] is False
    assert flags["automatic_position_sizing_allowed"] is False
    assert flags["automatic_portfolio_action_allowed"] is False


def test_build_valid_backtest_risk_item():
    item = build_backtest_risk_item(
        risk_id="risk-001",
        review_id="review-001",
        result_packet_id="packet-001",
        risk_category="data_quality",
        risk_level="MEDIUM",
        description="Data quality is limited and requires review.",
        evidence_metric_ids=["metric-001"],
        mitigation_note="Use paper-only operator review.",
    )

    assert is_valid_backtest_risk_item(item) is True
    assert item.operator_review_required is True
    assert item.risk_item_as_trade_instruction is False
    assert item.risk_item_as_profit_guarantee is False
    assert item.real_execution_allowed is False


def test_invalid_backtest_risk_item_is_rejected():
    item = build_backtest_risk_item(
        risk_id="",
        review_id="",
        result_packet_id="",
        risk_category="trade_signal",
        risk_level="EXTREME",
        description="Buy now for guaranteed profit.",
        evidence_metric_ids=[],
        mitigation_note="Place order.",
    )

    errors = validate_backtest_risk_item(item)

    assert "risk_id_required" in errors
    assert "review_id_required" in errors
    assert "result_packet_id_required" in errors
    assert "invalid_risk_category" in errors
    assert "invalid_risk_level" in errors
    assert "evidence_metric_ids_required" in errors
    assert "description_must_not_be_trade_or_guarantee_text" in errors
    assert "mitigation_note_must_not_be_trade_or_guarantee_text" in errors


def test_build_valid_backtest_risk_summary():
    summary = build_backtest_risk_summary(
        summary_id="summary-001",
        review_id="review-001",
        result_packet_id="packet-001",
        overall_risk_level="HIGH",
        risk_items=[_risk_item_payload()],
        risk_flags=["SAMPLE_LIMITED", "OPERATOR_REVIEW_REQUIRED"],
        limitations=["Paper-only local replay, not a future prediction."],
        generated_at_utc="2026-01-01T00:00:00+00:00",
        notes="Operator review required.",
    )

    assert is_valid_backtest_risk_summary(summary) is True
    assert summary.stage_id == STAGE_ID
    assert summary.operator_review_required is True
    assert summary.safety_flags["risk_summary_as_trade_instruction"] is False
    assert summary.safety_flags["real_execution_allowed"] is False


def test_backtest_risk_summary_serializable_dict():
    summary = build_backtest_risk_summary(
        summary_id="summary-002",
        review_id="review-002",
        result_packet_id="packet-002",
        overall_risk_level="MEDIUM",
        risk_items=[_risk_item_payload()],
        risk_flags=["DATA_LIMITED"],
        limitations=["Review only."],
        generated_at_utc="2026-01-01T00:00:00+00:00",
    )

    payload = summary.to_dict()
    assert payload["summary_id"] == "summary-002"
    assert payload["stage_id"] == STAGE_ID
    assert payload["safety_flags"]["order_ticket_allowed"] is False


def test_backtest_risk_summary_requires_sections():
    summary = build_backtest_risk_summary(
        summary_id="summary-003",
        review_id="review-003",
        result_packet_id="packet-003",
        overall_risk_level="HIGH",
        risk_items=[],
        risk_flags=[],
        limitations=[],
    )

    errors = validate_backtest_risk_summary(summary)

    assert "risk_items_required" in errors
    assert "risk_flags_required" in errors
    assert "limitations_required" in errors


def test_backtest_risk_summary_rejects_trade_or_guarantee_text():
    summary = build_backtest_risk_summary(
        summary_id="summary-004",
        review_id="review-004",
        result_packet_id="packet-004",
        overall_risk_level="HIGH",
        risk_items=[_risk_item_payload()],
        risk_flags=["BUY NOW"],
        limitations=["Review only."],
        notes="Guaranteed return.",
    )

    assert "summary_text_must_not_be_trade_or_guarantee_text" in validate_backtest_risk_summary(summary)
