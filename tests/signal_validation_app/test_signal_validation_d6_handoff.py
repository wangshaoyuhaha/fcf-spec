"""Tests for SIGNAL-VALIDATION-D6 final handoff."""

from __future__ import annotations

from apps.signal_validation_app.handoff import (
    COMPLETED_SIGNAL_VALIDATION_STAGES,
    FINAL_SAFETY_BOUNDARY,
    NEXT_RECOMMENDED_SIDECAR_SEQUENCE,
    build_signal_validation_final_handoff,
    summarize_signal_validation_final_handoff,
    validate_signal_validation_final_handoff,
)


def test_signal_validation_d6_builds_final_handoff_packet() -> None:
    packet = build_signal_validation_final_handoff(validation_baseline="1369 passed")

    assert packet["app_id"] == "SIGNAL-VALIDATION-APP-1"
    assert packet["stage_id"] == "SIGNAL-VALIDATION-D6"
    assert packet["branch_name"] == "sidecar-signal-validation-app-1"
    assert packet["validation_baseline"] == "1369 passed"
    assert packet["completed_stages"] == COMPLETED_SIGNAL_VALIDATION_STAGES
    assert packet["operator_review_required"] is True
    assert packet["operator_review_bypass_allowed"] is False


def test_signal_validation_d6_final_boundary_blocks_execution_and_trading() -> None:
    packet = build_signal_validation_final_handoff()
    boundary = packet["safety_boundary"]

    assert boundary["paper_only"] is True
    assert boundary["local_only"] is True
    assert boundary["read_only"] is True
    assert boundary["sidecar_only"] is True
    assert boundary["real_trading_allowed"] is False
    assert boundary["real_execution_allowed"] is False
    assert boundary["trade_action_enabled"] is False
    assert boundary["buy_button_enabled"] is False
    assert boundary["sell_button_enabled"] is False
    assert boundary["order_button_enabled"] is False


def test_signal_validation_d6_final_boundary_blocks_position_and_claims() -> None:
    packet = build_signal_validation_final_handoff()
    boundary = packet["safety_boundary"]

    assert boundary["automatic_position_sizing_allowed"] is False
    assert boundary["automatic_portfolio_action_allowed"] is False
    assert boundary["future_return_prediction_allowed"] is False
    assert boundary["guaranteed_performance_claim_allowed"] is False


def test_signal_validation_d6_final_boundary_blocks_core_and_source_mutation() -> None:
    packet = build_signal_validation_final_handoff()
    boundary = packet["safety_boundary"]

    assert boundary["p1_p47_core_mutation_allowed"] is False
    assert boundary["p48_core_expansion_allowed"] is False
    assert boundary["source_content_mutation_allowed"] is False
    assert boundary["source_deletion_allowed"] is False
    assert boundary["source_overwrite_allowed"] is False


def test_signal_validation_d6_final_boundary_blocks_release_actions() -> None:
    packet = build_signal_validation_final_handoff()

    assert packet["merge_policy"]["auto_merge_allowed"] is False
    assert packet["merge_policy"]["merge_requires_user_confirmation"] is True
    assert packet["release_policy"]["tag_allowed"] is False
    assert packet["release_policy"]["release_allowed"] is False
    assert packet["release_policy"]["deploy_allowed"] is False


def test_signal_validation_d6_validation_accepts_safe_packet() -> None:
    packet = build_signal_validation_final_handoff()
    validation = validate_signal_validation_final_handoff(packet)

    assert validation["is_valid"] is True
    assert validation["missing_fields"] == []
    assert validation["unsafe_true_fields"] == []
    assert validation["missing_stages"] == []
    assert validation["operator_review_required"] is True
    assert validation["auto_merge_allowed"] is False
    assert validation["tag_allowed"] is False
    assert validation["release_allowed"] is False
    assert validation["deploy_allowed"] is False


def test_signal_validation_d6_validation_rejects_unsafe_packet() -> None:
    packet = build_signal_validation_final_handoff()
    packet["safety_boundary"]["real_execution_allowed"] = True

    validation = validate_signal_validation_final_handoff(packet)

    assert validation["is_valid"] is False
    assert validation["unsafe_true_fields"] == ["real_execution_allowed"]


def test_signal_validation_d6_summary_is_safe_and_ordered() -> None:
    packet = build_signal_validation_final_handoff()
    summary = summarize_signal_validation_final_handoff(packet)

    assert summary["completed_stage_count"] == 6
    assert summary["output_count"] == 6
    assert summary["next_recommended_sidecar_sequence"] == NEXT_RECOMMENDED_SIDECAR_SEQUENCE
    assert summary["operator_review_required"] is True
    assert summary["auto_merge_allowed"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False


def test_signal_validation_d6_safety_boundary_has_required_keys() -> None:
    required_keys = {
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
        "real_execution_allowed",
        "trade_action_enabled",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
    }

    assert required_keys.issubset(set(FINAL_SAFETY_BOUNDARY))
