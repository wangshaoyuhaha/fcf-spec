from backtest_review_app.result_packet import (
    STAGE_ID,
    build_backtest_result_metric,
    build_backtest_result_packet,
    is_valid_backtest_result_metric,
    is_valid_backtest_result_packet,
    validate_backtest_result_metric,
    validate_backtest_result_packet,
)


def _metric_payload():
    return build_backtest_result_metric(
        metric_id="metric-001",
        metric_name="paper_replay_sample_count",
        metric_value=12.0,
        metric_unit="count",
        sample_size=12,
        interpretation_note="Metric is for paper-only operator review.",
    ).to_dict()


def test_build_valid_backtest_result_metric():
    metric = build_backtest_result_metric(
        metric_id="metric-001",
        metric_name="paper_replay_sample_count",
        metric_value=12.0,
        metric_unit="count",
        sample_size=12,
        interpretation_note="Metric is for paper-only operator review.",
    )

    assert is_valid_backtest_result_metric(metric) is True
    assert metric.metric_as_trade_instruction is False
    assert metric.metric_as_profit_guarantee is False
    assert metric.future_return_prediction_allowed is False
    assert metric.operator_review_required is True


def test_invalid_backtest_result_metric_is_rejected():
    metric = build_backtest_result_metric(
        metric_id="",
        metric_name="",
        metric_value=None,
        metric_unit="ratio",
        sample_size=-1,
        interpretation_note="Guaranteed profit and buy now.",
    )

    errors = validate_backtest_result_metric(metric)

    assert "metric_id_required" in errors
    assert "metric_name_required" in errors
    assert "sample_size_must_not_be_negative" in errors
    assert "interpretation_note_must_not_be_trade_or_guarantee_text" in errors


def test_build_valid_backtest_result_packet():
    packet = build_backtest_result_packet(
        packet_id="packet-001",
        review_id="review-001",
        result_type="paper_replay_result",
        replay_window="local_historical_window",
        source_metadata_ids=["source-a"],
        scenario_ids=["scenario-001"],
        metrics=[_metric_payload()],
        findings=["Paper-only replay has limited historical sample."],
        limitations=["Local review only, not a future prediction."],
        data_sources=["local_archive"],
        generated_at_utc="2026-01-01T00:00:00+00:00",
        notes="Operator review required.",
    )

    assert is_valid_backtest_result_packet(packet) is True
    assert packet.stage_id == STAGE_ID
    assert packet.operator_review_required is True
    assert packet.safety_flags["real_execution_allowed"] is False
    assert packet.safety_flags["future_return_prediction_allowed"] is False


def test_backtest_result_packet_serializable_dict():
    packet = build_backtest_result_packet(
        packet_id="packet-002",
        review_id="review-002",
        result_type="scenario_outcome_result",
        replay_window="local_window",
        source_metadata_ids=["source-a"],
        metrics=[_metric_payload()],
        findings=["Paper-only result requires review."],
        limitations=["No real account data included."],
        data_sources=["local_scenario"],
        generated_at_utc="2026-01-01T00:00:00+00:00",
    )

    payload = packet.to_dict()

    assert payload["packet_id"] == "packet-002"
    assert payload["stage_id"] == STAGE_ID
    assert payload["safety_flags"]["order_ticket_allowed"] is False


def test_result_packet_requires_sections():
    packet = build_backtest_result_packet(
        packet_id="packet-003",
        review_id="review-003",
        result_type="paper_replay_result",
        replay_window="local_window",
        source_metadata_ids=[],
        metrics=[],
        findings=[],
        limitations=[],
        data_sources=[],
    )

    errors = validate_backtest_result_packet(packet)

    assert "source_metadata_ids_required" in errors
    assert "metrics_required" in errors
    assert "findings_required" in errors
    assert "limitations_required" in errors
    assert "data_sources_required" in errors


def test_result_packet_rejects_invalid_type_and_status():
    packet = build_backtest_result_packet(
        packet_id="packet-004",
        review_id="review-004",
        result_type="trade_signal_result",
        result_status="EXECUTE_ORDER",
        replay_window="local_window",
        source_metadata_ids=["source-a"],
        metrics=[_metric_payload()],
        findings=["Paper-only finding."],
        limitations=["Paper-only limitation."],
        data_sources=["local"],
    )

    errors = validate_backtest_result_packet(packet)

    assert "invalid_result_type" in errors
    assert "invalid_result_status" in errors


def test_result_packet_text_must_not_be_trade_or_guarantee_text():
    packet = build_backtest_result_packet(
        packet_id="packet-005",
        review_id="review-005",
        result_type="paper_replay_result",
        replay_window="local_window",
        source_metadata_ids=["source-a"],
        metrics=[_metric_payload()],
        findings=["Guaranteed return and buy now."],
        limitations=["Paper-only limitation."],
        data_sources=["local"],
        notes="Place order.",
    )

    assert "packet_text_must_not_be_trade_or_guarantee_text" in validate_backtest_result_packet(packet)
