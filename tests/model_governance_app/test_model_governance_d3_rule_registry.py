"""Tests for MODEL-GOVERNANCE-D3 rule registry."""

from __future__ import annotations

import pytest

from apps.model_governance_app.rule_registry import (
    build_model_rule_record,
    build_model_rule_registry,
    build_scoring_policy_snapshot,
    validate_model_rule_registry_payload,
)


def test_model_governance_d3_builds_rule_record() -> None:
    rule = build_model_rule_record(
        rule_id="rule-001",
        rule_name="Score Breakout Rule",
        rule_category="SCORING",
        source_layer="STOCK-APP-1",
        rule_status="ACTIVE",
        governed_fields=["score_breakdown"],
        reason_codes=["VOLUME_PRICE_CONFIRMATION"],
        risk_flags=["DATA_QUALITY_REVIEW_REQUIRED"],
    )
    payload = rule.to_dict()

    assert payload["rule_id"] == "rule-001"
    assert payload["rule_category"] == "SCORING"
    assert payload["rule_status"] == "ACTIVE"
    assert payload["operator_review_required"] is True
    assert payload["score_mutation_allowed"] is False
    assert payload["real_execution_allowed"] is False


def test_model_governance_d3_rejects_bad_rule_category() -> None:
    with pytest.raises(ValueError):
        build_model_rule_record(
            rule_id="bad",
            rule_name="Bad Rule",
            rule_category="TRADE_ACTION",
            source_layer="UNKNOWN",
        )


def test_model_governance_d3_rejects_bad_rule_status() -> None:
    with pytest.raises(ValueError):
        build_model_rule_record(
            rule_id="bad",
            rule_name="Bad Rule",
            rule_category="SCORING",
            source_layer="STOCK-APP-1",
            rule_status="BUY_NOW",
        )


def test_model_governance_d3_builds_ready_scoring_snapshot() -> None:
    snapshot = build_scoring_policy_snapshot(
        snapshot_id="snapshot-001",
        source_layer="STOCK-APP-1",
        score_fields=["score_breakdown", "limit_up_potential_score"],
        reason_code_fields=["reason_codes"],
        risk_flag_fields=["risk_flags"],
        confidence_fields=["confidence_level"],
        data_quality_fields=["data_quality_state"],
    )
    payload = snapshot.to_dict()

    assert payload["snapshot_status"] == "SNAPSHOT_READY"
    assert payload["score_mutation_allowed"] is False
    assert payload["reason_code_mutation_allowed"] is False
    assert payload["risk_flag_deletion_allowed"] is False
    assert payload["future_return_prediction_allowed"] is False


def test_model_governance_d3_marks_partial_snapshot() -> None:
    snapshot = build_scoring_policy_snapshot(
        snapshot_id="snapshot-002",
        source_layer="STOCK-APP-1",
        score_fields=[],
        reason_code_fields=["reason_codes"],
        risk_flag_fields=["risk_flags"],
    )

    assert snapshot.to_dict()["snapshot_status"] == "SNAPSHOT_PARTIAL"


def test_model_governance_d3_builds_safe_registry() -> None:
    rule = build_model_rule_record(
        rule_id="rule-002",
        rule_name="Signal Validation Conflict Rule",
        rule_category="SIGNAL_VALIDATION",
        source_layer="SIGNAL-VALIDATION-APP-1",
        rule_status="ACTIVE",
    )
    snapshot = build_scoring_policy_snapshot(
        snapshot_id="snapshot-003",
        source_layer="SIGNAL-VALIDATION-APP-1",
        score_fields=["validation_status"],
        reason_code_fields=["conflict_type"],
        risk_flag_fields=["risk_flags"],
    )

    registry = build_model_rule_registry(
        registry_id="registry-001",
        rules=[rule],
        snapshots=[snapshot],
    )
    validation = validate_model_rule_registry_payload(registry)

    assert registry["app_id"] == "MODEL-GOVERNANCE-APP-1"
    assert registry["stage_id"] == "MODEL-GOVERNANCE-D3"
    assert registry["registry_status"] == "GOVERNANCE_READY_FOR_OPERATOR_REVIEW"
    assert registry["operator_review_required"] is True
    assert registry["score_mutation_allowed"] is False
    assert registry["trade_action_enabled"] is False
    assert registry["real_execution_allowed"] is False
    assert validation["is_valid"] is True


def test_model_governance_d3_registry_requires_review_for_observed_rule() -> None:
    rule = build_model_rule_record(
        rule_id="rule-003",
        rule_name="Observed Explanation Rule",
        rule_category="REASON_CODE",
        source_layer="AI-CONTEXT-1",
        rule_status="OBSERVED_ONLY",
    )
    snapshot = build_scoring_policy_snapshot(
        snapshot_id="snapshot-004",
        source_layer="AI-CONTEXT-1",
        score_fields=["explanation_score"],
        reason_code_fields=[],
        risk_flag_fields=["risk_flags"],
    )

    registry = build_model_rule_registry(
        registry_id="registry-002",
        rules=[rule],
        snapshots=[snapshot],
    )

    assert registry["registry_status"] == "GOVERNANCE_REVIEW_REQUIRED"
    assert registry["review_required_rules"] == ["rule-003"]
    assert registry["partial_snapshots"] == ["snapshot-004"]


def test_model_governance_d3_registry_blocks_for_blocked_rule() -> None:
    rule = build_model_rule_record(
        rule_id="rule-004",
        rule_name="Blocked Data Quality Rule",
        rule_category="DATA_QUALITY",
        source_layer="DATA-QUALITY-OPS-APP-1",
        rule_status="BLOCKED",
    )

    registry = build_model_rule_registry(
        registry_id="registry-003",
        rules=[rule],
        snapshots=[],
    )

    assert registry["registry_status"] == "GOVERNANCE_BLOCKED"
    assert registry["blocked_rules"] == ["rule-004"]


def test_model_governance_d3_validation_rejects_unsafe_registry() -> None:
    registry = build_model_rule_registry(
        registry_id="registry-004",
        rules=[],
        snapshots=[],
    )
    registry["score_mutation_allowed"] = True

    validation = validate_model_rule_registry_payload(registry)

    assert validation["is_valid"] is False
    assert validation["unsafe_true_fields"] == ["score_mutation_allowed"]
