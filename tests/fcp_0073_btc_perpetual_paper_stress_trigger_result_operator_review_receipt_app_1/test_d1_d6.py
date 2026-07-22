from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0073_btc_perpetual_paper_stress_trigger_result_operator_review_receipt_app_1 as fcp_0073
from apps.fcp_0073_btc_perpetual_paper_stress_trigger_result_operator_review_receipt_app_1 import (
    REVIEW_DISPOSITIONS,
    BTCPerpetualPaperStressTriggerResultOperatorReviewReceipt,
    record_btc_perpetual_paper_stress_trigger_result_operator_review,
)
from tests.fcp_0072_btc_perpetual_paper_stress_trigger_result_operator_review_packet_app_1.test_d1_d6 import (
    _packet,
)


def _receipt(**changes: object):
    values = {
        "review_packet": _packet(),
        "receipt_id": "btc-stress-review-receipt-20260722-001",
        "reviewer_reference": "operator-local-1",
        "reviewed_at_utc": "2026-07-22T13:10:00Z",
        "disposition": "REVIEWED_NO_RESOLUTION",
    }
    values.update(changes)
    return record_btc_perpetual_paper_stress_trigger_result_operator_review(**values)


def test_exact_typed_packet_builds_complete_review_receipt():
    receipt = _receipt()
    assert receipt.operator_review_completed is True
    assert receipt.receipt_only is True
    assert receipt.triggered_count + receipt.non_triggered_count == 8
    assert len(receipt.receipt_hash) == 64


def test_receipt_preserves_exact_packet_lineage_and_order():
    packet = _packet()
    receipt = _receipt(review_packet=packet)
    assert receipt.packet_hash == packet.packet_hash
    assert receipt.review_registry_hash == packet.review_registry_hash
    assert receipt.evaluation_snapshot_hash == packet.evaluation_snapshot_hash
    assert receipt.scenario_registry_hash == packet.scenario_registry_hash
    assert receipt.complete_rule_bundle_hash == packet.complete_rule_bundle_hash
    assert receipt.record_hashes == packet.record_hashes


def test_receipt_preserves_trigger_and_nontrigger_groups():
    packet = _packet()
    receipt = _receipt(review_packet=packet)
    assert receipt.triggered_record_hashes == packet.triggered_record_hashes
    assert receipt.non_triggered_record_hashes == packet.non_triggered_record_hashes
    assert receipt.triggered_count == packet.triggered_count
    assert receipt.non_triggered_count == packet.non_triggered_count


@pytest.mark.parametrize("disposition", REVIEW_DISPOSITIONS)
def test_closed_non_authorizing_dispositions(disposition):
    receipt = _receipt(disposition=disposition)
    assert receipt.disposition == disposition
    assert receipt.evidence_approved is False
    assert receipt.evidence_rejected is False
    assert receipt.result_resolved is False
    assert receipt.gap_closed is False


def test_receipt_is_deterministic_for_exact_inputs():
    assert _receipt().receipt_hash == _receipt().receipt_hash


@pytest.mark.parametrize(
    "field,value",
    (
        ("receipt_id", "receipt has spaces"),
        ("reviewer_reference", "operator has spaces"),
    ),
)
def test_receipt_rejects_unsafe_identifiers(field, value):
    with pytest.raises(ValueError, match="safe identifier"):
        _receipt(**{field: value})


def test_receipt_rejects_untyped_packet():
    with pytest.raises(ValueError, match="exact typed FCP-0072"):
        _receipt(review_packet=object())


def test_receipt_rejects_time_before_packet_evidence():
    with pytest.raises(ValueError, match="cannot precede"):
        _receipt(reviewed_at_utc="2026-07-22T12:39:59Z")


def test_receipt_rejects_non_utc_time():
    with pytest.raises(ValueError, match="must be UTC"):
        _receipt(reviewed_at_utc="2026-07-22T21:10:00+08:00")


def test_receipt_rejects_unregistered_disposition():
    with pytest.raises(ValueError, match="disposition is not registered"):
        _receipt(disposition="EVIDENCE_APPROVED")


@pytest.mark.parametrize(
    "field,value",
    (
        ("operator_review_completed", False),
        ("receipt_only", False),
        ("evidence_approved", True),
        ("evidence_rejected", True),
        ("result_resolved", True),
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
def test_receipt_rejects_authority_escalation(field, value):
    with pytest.raises(ValueError, match="cannot approve, resolve, recommend, act, or close"):
        replace(_receipt(), **{field: value})


@pytest.mark.parametrize(
    "field,value",
    (
        ("calculation_authority", "AI"),
        ("evidence_authority", "UNREGISTERED"),
        ("ai_role", "DECISION_AUTHORITY"),
    ),
)
def test_receipt_rejects_authority_identity_substitution(field, value):
    with pytest.raises(ValueError, match="authority identities"):
        replace(_receipt(), **{field: value})


def test_receipt_hash_changes_with_review_facts():
    baseline = _receipt().receipt_hash
    assert baseline != _receipt(disposition="ESCALATED_FOR_RESEARCH").receipt_hash
    assert baseline != _receipt(reviewer_reference="operator-local-2").receipt_hash
    assert baseline != _receipt(reviewed_at_utc="2026-07-22T13:10:01Z").receipt_hash


def test_receipt_contract_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _receipt().receipt_id = "changed"


def test_package_exports_only_registered_public_contracts():
    assert fcp_0073.__all__ == [
        "REVIEW_DISPOSITIONS",
        "BTCPerpetualPaperStressTriggerResultOperatorReviewReceipt",
        "record_btc_perpetual_paper_stress_trigger_result_operator_review",
    ]
