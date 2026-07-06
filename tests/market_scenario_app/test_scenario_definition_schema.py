from market_scenario_app.schema import (
    STAGE_ID,
    build_scenario_definition,
    is_valid_scenario_definition,
    scenario_definition_schema,
    validate_scenario_definition,
)


def test_scenario_definition_schema_identity_and_required_fields():
    schema = scenario_definition_schema()
    assert schema["stage_id"] == STAGE_ID
    assert schema["schema_name"] == "market_scenario_definition"
    assert "scenario_id" in schema["required_fields"]
    assert "operator_review_required" in schema["required_fields"]


def test_scenario_definition_schema_safety_flags():
    schema = scenario_definition_schema()
    flags = schema["safety_flags"]
    assert flags["paper_only"] is True
    assert flags["local_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["real_execution_allowed"] is False
    assert flags["automatic_position_sizing_allowed"] is False


def test_build_valid_scenario_definition():
    definition = build_scenario_definition(
        scenario_id="scenario-001",
        scenario_label="Risk off liquidity stress review",
        scenario_type="liquidity_stress",
        market_scope="cross_asset",
        asset_classes=["stock", "btc", "futures"],
        time_horizon="paper_review_next_session",
        source_metadata_ids=["source-a", "source-b"],
        data_quality_state="PASS_LIMITED",
        confidence_level="MEDIUM",
        scenario_score=62.5,
        notes="Review only.",
    )

    assert is_valid_scenario_definition(definition) is True
    assert definition.operator_review_required is True
    assert definition.trade_instruction_allowed is False
    assert definition.order_ticket_allowed is False
    assert definition.real_execution_allowed is False


def test_scenario_definition_serializable_dict():
    definition = build_scenario_definition(
        scenario_id="scenario-002",
        scenario_label="Base case paper review",
        scenario_type="base_case",
        market_scope="portfolio_context",
        asset_classes=["stock"],
        time_horizon="local_review",
        source_metadata_ids=["source-x"],
        data_quality_state="PASS_STRICT",
        confidence_level="HIGH",
    )

    payload = definition.to_dict()
    assert payload["scenario_id"] == "scenario-002"
    assert payload["scenario_review_status"] == "OPERATOR_REVIEW_REQUIRED"
    assert payload["real_execution_allowed"] is False


def test_invalid_scenario_type_and_market_scope_are_rejected():
    definition = build_scenario_definition(
        scenario_id="scenario-003",
        scenario_label="Invalid type review",
        scenario_type="trade_signal",
        market_scope="broker_account",
        asset_classes=["stock"],
        time_horizon="local_review",
        source_metadata_ids=["source-x"],
        data_quality_state="PASS_STRICT",
        confidence_level="HIGH",
    )

    errors = validate_scenario_definition(definition)
    assert "invalid_scenario_type" in errors
    assert "invalid_market_scope" in errors


def test_scenario_score_range_is_checked():
    definition = build_scenario_definition(
        scenario_id="scenario-004",
        scenario_label="Score range review",
        scenario_type="risk_off",
        market_scope="theme",
        asset_classes=["stock"],
        time_horizon="local_review",
        source_metadata_ids=["source-x"],
        data_quality_state="PASS_STRICT",
        confidence_level="LOW",
        scenario_score=120.0,
    )

    assert "scenario_score_out_of_range" in validate_scenario_definition(definition)


def test_scenario_label_must_not_be_trade_instruction():
    definition = build_scenario_definition(
        scenario_id="scenario-005",
        scenario_label="Buy now breakout order",
        scenario_type="risk_on",
        market_scope="single_asset",
        asset_classes=["stock"],
        time_horizon="local_review",
        source_metadata_ids=["source-x"],
        data_quality_state="PASS_STRICT",
        confidence_level="LOW",
        scenario_score=10.0,
    )

    assert "scenario_label_must_not_be_trade_instruction" in validate_scenario_definition(definition)
