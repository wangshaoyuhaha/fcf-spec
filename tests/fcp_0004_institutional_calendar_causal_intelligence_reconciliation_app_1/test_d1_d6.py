from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.fcp_0004_institutional_calendar_causal_intelligence_reconciliation_app_1 import (
    EXPECTED_CANDIDATE_IDS,
    EXPECTED_GAP_IDS,
    EXPECTED_OVERLAP_GAP_IDS,
    EXPECTED_RECEIPTS,
    FCP_0004_BOUNDARY,
    FoundationDeliveryReceipt,
    InstitutionalArchitectureReconciliationBoundary,
    InstitutionalArchitectureRegistry,
    build_expected_architecture_registry,
    build_institutional_architecture_reconciliation_packet,
    reconcile_institutional_architecture,
    validate_institutional_architecture_reconciliation_acceptance,
)


ROOT = Path(__file__).resolve().parents[2]


def test_d1_boundary_is_fail_closed() -> None:
    assert FCP_0004_BOUNDARY.read_only is True
    assert FCP_0004_BOUNDARY.duplicate_module_creation_allowed is False
    assert FCP_0004_BOUNDARY.production_gap_closure_allowed is False
    with pytest.raises(ValueError, match="fail-closed"):
        InstitutionalArchitectureReconciliationBoundary(
            duplicate_module_creation_allowed=True
        )


def test_d1_receipt_is_immutable_and_hash_is_deterministic() -> None:
    left = EXPECTED_RECEIPTS[0]
    right = replace(left)
    assert left == right
    assert left.receipt_hash == right.receipt_hash
    with pytest.raises(Exception):
        left.stage_id = "V2-R24"  # type: ignore[misc]


def test_d1_receipt_rejects_unsafe_repository_path() -> None:
    with pytest.raises(ValueError, match="repository relative"):
        replace(EXPECTED_RECEIPTS[0], test_path="tests/../unsafe.py")


def test_d2_expected_delivery_inventory_is_exact() -> None:
    assert tuple(item.stage_id for item in EXPECTED_RECEIPTS) == tuple(
        f"V2-R{number}" for number in range(23, 38)
    )
    assert len({item.app_id for item in EXPECTED_RECEIPTS}) == 15


def test_d2_expected_gap_mapping_is_exact() -> None:
    result = reconcile_institutional_architecture(
        build_expected_architecture_registry()
    )
    assert tuple(gap for gap, _ in result.gap_coverage) == EXPECTED_GAP_IDS
    assert result.missing_gap_ids == ()
    assert result.mapping_mismatch_stage_ids == ()


def test_d2_expected_overlap_is_explicit_and_unique() -> None:
    result = reconcile_institutional_architecture(
        build_expected_architecture_registry()
    )
    coverage = dict(result.gap_coverage)
    assert EXPECTED_OVERLAP_GAP_IDS == ("V2-FR-GAP-084",)
    assert coverage["V2-FR-GAP-084"] == ("V2-R23", "V2-R35")
    assert all(
        len(stages) == 1
        for gap, stages in result.gap_coverage
        if gap != "V2-FR-GAP-084"
    )


def test_d2_registered_delivery_paths_exist() -> None:
    for receipt in EXPECTED_RECEIPTS:
        assert (ROOT / "apps" / receipt.app_id).is_dir()
        assert (ROOT / receipt.final_state_path).is_file()
        assert (ROOT / receipt.guard_path).is_file()
        assert (ROOT / receipt.test_path).is_file()


def test_d3_candidate_inventory_is_exact() -> None:
    assert len(EXPECTED_CANDIDATE_IDS) == 10
    assert "EARNINGS_SURPRISE" in EXPECTED_CANDIDATE_IDS
    assert "CAPITAL_TRANSMISSION_PRESSURE" in EXPECTED_CANDIDATE_IDS


def test_d3_candidate_gap_is_visible_and_blocks() -> None:
    registry = build_expected_architecture_registry()
    changed = replace(
        registry,
        candidate_ids=registry.candidate_ids[:-1] + ("UNREGISTERED_CANDIDATE",),
    )
    result = reconcile_institutional_architecture(changed)
    assert result.state == "BLOCKED"
    assert result.missing_candidate_ids
    assert result.unexpected_candidate_ids == ("UNREGISTERED_CANDIDATE",)


def test_d4_missing_delivery_and_gap_are_visible() -> None:
    registry = build_expected_architecture_registry()
    changed = replace(
        registry,
        receipts=tuple(item for item in registry.receipts if item.stage_id != "V2-R27"),
    )
    result = reconcile_institutional_architecture(changed)
    assert result.state == "BLOCKED"
    assert result.missing_stage_ids == ("V2-R27",)
    assert result.missing_gap_ids == ("V2-FR-GAP-076",)


def test_d4_mapping_mismatch_is_visible() -> None:
    registry = build_expected_architecture_registry()
    changed_receipts = tuple(
        replace(item, gap_ids=("V2-FR-GAP-071",))
        if item.stage_id == "V2-R23"
        else item
        for item in registry.receipts
    )
    result = reconcile_institutional_architecture(
        replace(registry, receipts=changed_receipts)
    )
    assert result.state == "BLOCKED"
    assert result.mapping_mismatch_stage_ids == ("V2-R23",)


def test_d4_production_authority_overclaim_is_visible() -> None:
    registry = build_expected_architecture_registry()
    changed_receipts = tuple(
        replace(item, production_gap_closed=True)
        if item.stage_id == "V2-R29"
        else item
        for item in registry.receipts
    )
    result = reconcile_institutional_architecture(
        replace(registry, receipts=changed_receipts)
    )
    assert result.state == "BLOCKED"
    assert result.overclaim_stage_ids == ("V2-R29",)
    assert any(
        item.code == "PRODUCTION_AUTHORITY_OVERCLAIM" for item in result.findings
    )


def test_d4_reconciliation_is_deterministic() -> None:
    registry = build_expected_architecture_registry()
    left = reconcile_institutional_architecture(registry)
    right = reconcile_institutional_architecture(registry)
    assert left == right
    assert left.reconciliation_hash == right.reconciliation_hash
    assert left.state == "READY_FOR_OPERATOR_REVIEW"


def test_d5_review_packet_is_immutable_and_read_only() -> None:
    result = reconcile_institutional_architecture(
        build_expected_architecture_registry()
    )
    packet = build_institutional_architecture_reconciliation_packet(result)
    assert isinstance(packet.payload, MappingProxyType)
    assert packet.payload["proposal_status"] == "ACCEPTED_ARCHITECTURE"
    assert packet.payload["production_gap_closure_claimed"] is False
    with pytest.raises(TypeError):
        packet.payload["proposal_status"] = "IMPLEMENTED"  # type: ignore[index]


def test_d5_acceptance_preserves_all_authority_boundaries() -> None:
    result = reconcile_institutional_architecture(
        build_expected_architecture_registry()
    )
    packet = build_institutional_architecture_reconciliation_packet(result)
    assert all(
        validate_institutional_architecture_reconciliation_acceptance(packet).values()
    )


def test_d6_registry_cannot_claim_implementation_or_phase() -> None:
    registry = build_expected_architecture_registry()
    with pytest.raises(ValueError, match="ACCEPTED_ARCHITECTURE"):
        replace(registry, proposal_status="IMPLEMENTED")
    with pytest.raises(ValueError, match="cannot authorize a phase"):
        replace(registry, phase_id="V2-R48")


def test_d6_receipt_rejects_non_registered_stage() -> None:
    receipt = EXPECTED_RECEIPTS[0]
    with pytest.raises(ValueError, match="outside V2-R23 through V2-R37"):
        FoundationDeliveryReceipt(
            stage_id="V2-R48",
            app_id=receipt.app_id,
            final_state_path=receipt.final_state_path,
            guard_path=receipt.guard_path,
            test_path=receipt.test_path,
            gap_ids=receipt.gap_ids,
        )
