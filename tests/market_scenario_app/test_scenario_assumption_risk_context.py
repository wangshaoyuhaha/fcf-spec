from market_scenario_app.risk_context import (
    STAGE_ID,
    assumption_risk_context_schema,
    build_risk_context,
    build_scenario_assumption,
    is_valid_risk_context,
    is_valid_scenario_assumption,
    validate_risk_context,
    validate_scenario_assumption,
)


def test_assumption_risk_context_schema_safety_flags():
    schema = assumption_risk_context_schema()
    flags = schema["safety_flags"]

    assert schema["stage_id"] == STAGE_ID
    assert flags["paper_only"] is True
    assert flags["local_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["trade_instruction_allowed"] is False
    assert flags["automatic_position_sizing_allowed"] is False
    assert flags["automatic_portfolio_action_allowed"] is False
    assert flags["order_ticket_allowed"] is False
    assert flags["real_execution_allowed"] is False


def test_build_valid_scenario_assumption():
    assumption = build_scenario_assumption(
        assumption_id="assumption-001",
        scenario_id="scenario-001",
        assumption_type="liquidity",
        description="Liquidity stress is reviewed as a paper-only context.",
        evidence_source_ids=["source-a"],
        confidence_level="MEDIUM",
        data_quality_state="PASS_LIMITED",
    )

    assert is_valid_scenario_assumption(assumption) is True
    assert assumption.operator_review_required is True
    assert assumption.trade_instruction_allowed is False
    assert assumption.real_execution_allowed is False


def test_invalid_scenario_assumption_is_rejected():
    assumption = build_scenario_assumption(
        assumption_id="",
        scenario_id="scenario-001",
        assumption_type="trade_signal",
        description="Buy now based on scenario.",
        evidence_source_ids=[],
        confidence_level="CERTAIN",
        data_quality_state="BAD",
    )

    errors = validate_scenario_assumption(assumption)

    assert "assumption_id_required" in errors
    assert "invalid_assumption_type" in errors
    assert "evidence_source_ids_required" in errors
    assert "invalid_confidence_level" in errors
    assert "invalid_data_quality_state" in errors
    assert "assumption_description_must_not_be_trade_instruction" in errors


def test_build_valid_risk_context():
    risk_context = build_risk_context(
        risk_context_id="risk-001",
        scenario_id="scenario-001",
        risk_level="HIGH",
        risk_factors=["liquidity_gap", "volatility_expansion"],
        risk_flags=["DATA_LIMITED", "REVIEW_REQUIRED"],
        source_metadata_ids=["source-a", "source-b"],
        mitigation_notes="Escalate for paper-only operator review.",
        scenario_score_adjustment=-15.0,
    )

    assert is_valid_risk_context(risk_context) is True
    assert risk_context.operator_review_required is True
    assert risk_context.scenario_score_as_trade_instruction is False
    assert risk_context.automatic_position_sizing_allowed is False
    assert risk_context.automatic_portfolio_action_allowed is False
    assert risk_context.order_ticket_allowed is False
    assert risk_context.real_execution_allowed is False


def test_invalid_risk_context_is_rejected():
    risk_context = build_risk_context(
        risk_context_id="",
        scenario_id="",
        risk_level="EXTREME",
        risk_factors=[],
        risk_flags=[],
        source_metadata_ids=[],
        mitigation_notes="Place order immediately.",
        scenario_score_adjustment=150.0,
    )

    errors = validate_risk_context(risk_context)

    assert "risk_context_id_required" in errors
    assert "scenario_id_required" in errors
    assert "invalid_risk_level" in errors
    assert "risk_factors_required" in errors
    assert "risk_flags_required" in errors
    assert "source_metadata_ids_required" in errors
    assert "scenario_score_adjustment_out_of_range" in errors
    assert "mitigation_notes_must_not_be_trade_instruction" in errors


def test_assumption_and_risk_context_are_serializable():
    assumption = build_scenario_assumption(
        assumption_id="assumption-002",
        scenario_id="scenario-002",
        assumption_type="data_quality",
        description="Data quality is degraded and requires review.",
        evidence_source_ids=["source-x"],
        confidence_level="LOW",
        data_quality_state="FAIL_QUARANTINE",
    )
    risk_context = build_risk_context(
        risk_context_id="risk-002",
        scenario_id="scenario-002",
        risk_level="CRITICAL",
        risk_factors=["source_quarantine"],
        risk_flags=["FAIL_QUARANTINE"],
        source_metadata_ids=["source-x"],
        mitigation_notes="Do paper-only review before any downstream use.",
    )

    assert assumption.to_dict()["assumption_id"] == "assumption-002"
    assert risk_context.to_dict()["risk_context_id"] == "risk-002"
    assert risk_context.to_dict()["real_execution_allowed"] is False


def test_scenario_score_adjustment_boundary_values():
    low = build_risk_context(
        risk_context_id="risk-low",
        scenario_id="scenario-003",
        risk_level="LOW",
        risk_factors=["factor"],
        risk_flags=["FLAG"],
        source_metadata_ids=["source"],
        mitigation_notes="Review only.",
        scenario_score_adjustment=-100.0,
    )
    high = build_risk_context(
        risk_context_id="risk-high",
        scenario_id="scenario-003",
        risk_level="LOW",
        risk_factors=["factor"],
        risk_flags=["FLAG"],
        source_metadata_ids=["source"],
        mitigation_notes="Review only.",
        scenario_score_adjustment=100.0,
    )

    assert validate_risk_context(low) == []
    assert validate_risk_context(high) == []
