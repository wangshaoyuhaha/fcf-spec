from backtest_review_app.schema import (
    STAGE_ID,
    backtest_review_schema,
    build_backtest_metric_definition,
    build_backtest_review_definition,
    is_valid_backtest_metric_definition,
    is_valid_backtest_review_definition,
    validate_backtest_metric_definition,
    validate_backtest_review_definition,
)


def test_backtest_review_schema_identity_and_safety_flags():
    schema = backtest_review_schema()
    flags = schema["safety_flags"]

    assert schema["stage_id"] == STAGE_ID
    assert schema["schema_name"] == "backtest_review_definition"
    assert flags["paper_only"] is True
    assert flags["local_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["trade_instruction_allowed"] is False
    assert flags["profit_guarantee_allowed"] is False
    assert flags["real_execution_allowed"] is False
    assert flags["real_account_access_allowed"] is False


def test_build_valid_backtest_review_definition():
    definition = build_backtest_review_definition(
        review_id="review-001",
        review_label="Paper-only scenario replay review",
        review_type="scenario_outcome_review",
        market_scope="cross_asset",
        asset_classes=["stock", "btc", "futures"],
        replay_window="historical_window_local_only",
        source_metadata_ids=["source-a", "source-b"],
        scenario_ids=["scenario-001"],
        data_quality_state="PASS_LIMITED",
        confidence_level="MEDIUM",
        notes="Review only.",
    )

    assert is_valid_backtest_review_definition(definition) is True
    assert definition.operator_review_required is True
    assert definition.trade_instruction_allowed is False
    assert definition.profit_guarantee_allowed is False
    assert definition.real_execution_allowed is False


def test_backtest_review_definition_serializable_dict():
    definition = build_backtest_review_definition(
        review_id="review-002",
        review_label="Archive replay review",
        review_type="archive_replay",
        market_scope="portfolio_context",
        asset_classes=["stock"],
        replay_window="local_archive_window",
        source_metadata_ids=["source-x"],
        data_quality_state="PASS_STRICT",
        confidence_level="HIGH",
    )

    payload = definition.to_dict()
    assert payload["review_id"] == "review-002"
    assert payload["review_status"] == "OPERATOR_REVIEW_REQUIRED"
    assert payload["future_return_prediction_allowed"] is False


def test_invalid_backtest_review_definition_is_rejected():
    definition = build_backtest_review_definition(
        review_id="",
        review_label="Buy now guaranteed profit",
        review_type="trade_signal",
        market_scope="broker_account",
        asset_classes=[],
        replay_window="",
        source_metadata_ids=[],
        data_quality_state="BAD",
        confidence_level="CERTAIN",
        notes="Future return is guaranteed.",
    )

    errors = validate_backtest_review_definition(definition)

    assert "review_id_required" in errors
    assert "invalid_review_type" in errors
    assert "invalid_market_scope" in errors
    assert "asset_classes_required" in errors
    assert "replay_window_required" in errors
    assert "source_metadata_ids_required" in errors
    assert "invalid_data_quality_state" in errors
    assert "invalid_confidence_level" in errors
    assert "review_label_must_not_be_trade_or_guarantee_text" in errors
    assert "notes_must_not_be_trade_or_guarantee_text" in errors


def test_build_valid_backtest_metric_definition():
    metric = build_backtest_metric_definition(
        metric_id="metric-001",
        review_id="review-001",
        metric_name="paper_replay_sample_count",
        metric_value=25.0,
        metric_unit="count",
        sample_size=25,
        interpretation_note="Metric is for paper-only operator review.",
    )

    assert is_valid_backtest_metric_definition(metric) is True
    assert metric.metric_as_trade_instruction is False
    assert metric.metric_as_profit_guarantee is False
    assert metric.operator_review_required is True


def test_invalid_backtest_metric_definition_is_rejected():
    metric = build_backtest_metric_definition(
        metric_id="",
        review_id="",
        metric_name="",
        metric_value=None,
        metric_unit="ratio",
        sample_size=-1,
        interpretation_note="Guaranteed return and buy now.",
    )

    errors = validate_backtest_metric_definition(metric)

    assert "metric_id_required" in errors
    assert "review_id_required" in errors
    assert "metric_name_required" in errors
    assert "sample_size_must_not_be_negative" in errors
    assert "interpretation_note_must_not_be_trade_or_guarantee_text" in errors


def test_backtest_metric_serializable_dict():
    metric = build_backtest_metric_definition(
        metric_id="metric-002",
        review_id="review-002",
        metric_name="paper_replay_drawdown_review",
        metric_value=None,
        metric_unit="review_only",
        sample_size=0,
        interpretation_note="Insufficient sample requires operator review.",
    )

    payload = metric.to_dict()
    assert payload["metric_id"] == "metric-002"
    assert payload["metric_as_trade_instruction"] is False
    assert payload["metric_as_profit_guarantee"] is False
