from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0072_btc_perpetual_paper_stress_trigger_result_operator_review_packet_app_1 as fcp_0072
from apps.fcp_0072_btc_perpetual_paper_stress_trigger_result_operator_review_packet_app_1 import (
    BTCPerpetualPaperStressTriggerResultOperatorReviewPacket,
    build_btc_perpetual_paper_stress_trigger_result_operator_review_packet,
)
from tests.fcp_0071_btc_perpetual_paper_stress_trigger_result_review_registry_app_1.test_d1_d6 import (
    _registry,
)


def _packet():
    return build_btc_perpetual_paper_stress_trigger_result_operator_review_packet(
        _registry(),
        packet_created_at_utc="2026-07-22T12:40:00Z",
    )


def test_exact_typed_registry_builds_complete_review_packet():
    packet = _packet()
    assert len(packet.record_hashes) == 8
    assert packet.triggered_count + packet.non_triggered_count == 8
    assert packet.operator_review_state == "OPERATOR_REVIEW_REQUIRED"
    assert packet.packet_only is True
    assert len(packet.packet_hash) == 64


def test_packet_preserves_exact_registry_and_record_order():
    registry = _registry()
    packet = build_btc_perpetual_paper_stress_trigger_result_operator_review_packet(
        registry,
        packet_created_at_utc="2026-07-22T12:40:00Z",
    )
    assert packet.review_registry_hash == registry.registry_hash
    assert packet.record_hashes == tuple(
        item.review_record_hash for item in registry.records
    )
    assert packet.evaluation_snapshot_hash == registry.evaluation_snapshot_hash
    assert packet.scenario_registry_hash == registry.scenario_registry_hash


def test_packet_trigger_groups_copy_exact_registered_boolean_evidence():
    registry = _registry()
    packet = _packet()
    assert packet.triggered_record_hashes == tuple(
        item.review_record_hash for item in registry.records if item.triggered
    )
    assert packet.non_triggered_record_hashes == tuple(
        item.review_record_hash for item in registry.records if not item.triggered
    )


def test_all_non_triggered_records_remain_visible_and_valid():
    registry = _registry()
    records = tuple(replace(item, triggered=False) for item in registry.records)
    registry = replace(registry, records=records)
    packet = build_btc_perpetual_paper_stress_trigger_result_operator_review_packet(
        registry,
        packet_created_at_utc="2026-07-22T12:40:00Z",
    )
    assert packet.triggered_count == 0
    assert packet.non_triggered_count == 8
    assert packet.non_triggered_record_hashes == packet.record_hashes


def test_packet_is_deterministic_for_exact_inputs():
    assert _packet().packet_hash == _packet().packet_hash


def test_packet_hash_changes_with_registered_time_lineage():
    first = _packet()
    second = build_btc_perpetual_paper_stress_trigger_result_operator_review_packet(
        _registry(),
        packet_created_at_utc="2026-07-22T12:40:01Z",
    )
    assert first.packet_hash != second.packet_hash


def test_packet_rejects_untyped_registry():
    with pytest.raises(ValueError, match="exact typed FCP-0071"):
        BTCPerpetualPaperStressTriggerResultOperatorReviewPacket(
            packet_id="review-packet-v1",
            review_registry=object(),
            packet_created_at_utc="2026-07-22T12:40:00Z",
        )


def test_packet_rejects_time_before_registry_evidence():
    with pytest.raises(ValueError, match="cannot precede"):
        build_btc_perpetual_paper_stress_trigger_result_operator_review_packet(
            _registry(),
            packet_created_at_utc="2026-07-22T12:29:59Z",
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("operator_review_state", "APPROVED"),
        ("operator_review_required", False),
        ("packet_only", False),
        ("disposition_assigned", True),
        ("evidence_approved", True),
        ("evidence_rejected", True),
        ("recommendation_allowed", True),
        ("account_state_allowed", True),
        ("margin_calculation_allowed", True),
        ("leverage_calculation_allowed", True),
        ("liquidation_action_allowed", True),
        ("balance_calculation_allowed", True),
        ("position_calculation_allowed", True),
        ("pnl_calculation_allowed", True),
        ("insurance_fund_mutation_allowed", True),
        ("adl_action_allowed", True),
        ("order_allowed", True),
        ("execution_allowed", True),
        ("gap_closed", True),
    ),
)
def test_packet_rejects_review_or_action_authority_escalation(field, value):
    with pytest.raises(ValueError):
        replace(_packet(), **{field: value})


@pytest.mark.parametrize(
    "field,value",
    (
        ("calculation_authority", "AI"),
        ("evidence_authority", "UNREGISTERED"),
        ("ai_role", "DECISION_AUTHORITY"),
    ),
)
def test_packet_rejects_authority_identity_substitution(field, value):
    with pytest.raises(ValueError, match="authority identities"):
        replace(_packet(), **{field: value})


def test_packet_contract_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _packet().packet_id = "changed"


def test_package_exports_only_registered_public_contracts():
    assert fcp_0072.__all__ == [
        "BTCPerpetualPaperStressTriggerResultOperatorReviewPacket",
        "build_btc_perpetual_paper_stress_trigger_result_operator_review_packet",
    ]
