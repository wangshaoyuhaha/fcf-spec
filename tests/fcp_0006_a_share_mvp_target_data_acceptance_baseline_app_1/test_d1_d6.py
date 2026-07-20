from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.fcp_0006_a_share_mvp_target_data_acceptance_baseline_app_1 import (
    DATA_DOMAINS,
    OBLIGATION_CATEGORIES,
    TARGET_FAMILIES,
    AShareMvpBaselineBoundary,
    AShareMvpBaselineRegistry,
    AShareTargetContract,
    AcceptanceEvidenceObligation,
    FCP_0006_BOUNDARY,
    PointInTimeDataRequirement,
    build_a_share_mvp_baseline_packet,
    build_canonical_a_share_mvp_baseline,
    evaluate_a_share_mvp_baseline,
    validate_a_share_mvp_baseline_acceptance,
)


DIGEST = "a" * 64


def target(**updates: object) -> AShareTargetContract:
    values = {
        "target_id": "target-next-session",
        "target_family": "NEXT_SESSION_EXCESS_RETURN",
        "horizon_id": "next-session",
        "benchmark_id": "registered-benchmark",
        "universe_policy_id": "point-in-time-universe",
        "label_maturity_id": "after-next-close",
    }
    values.update(updates)
    return AShareTargetContract(**values)  # type: ignore[arg-type]


def requirement(**updates: object) -> PointInTimeDataRequirement:
    values = {
        "field_id": "close",
        "domain": "OHLCV",
        "source_semantics_id": "session-close-v1",
    }
    values.update(updates)
    return PointInTimeDataRequirement(**values)  # type: ignore[arg-type]


def obligation(**updates: object) -> AcceptanceEvidenceObligation:
    values = {
        "obligation_id": "success-threshold",
        "category": "SUCCESS_THRESHOLD",
        "metric_id": "net-excess-calibration-v1",
    }
    values.update(updates)
    return AcceptanceEvidenceObligation(**values)  # type: ignore[arg-type]


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0006_BOUNDARY.research_priority_allowed is True
    assert FCP_0006_BOUNDARY.product_market_selection_allowed is False
    assert FCP_0006_BOUNDARY.provider_selection_allowed is False
    assert FCP_0006_BOUNDARY.execution_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0006_BOUNDARY.network_allowed = True  # type: ignore[misc]


def test_d1_boundary_rejects_product_market_selection() -> None:
    with pytest.raises(ValueError, match="fail-closed"):
        AShareMvpBaselineBoundary(product_market_selection_allowed=True)


def test_d1_target_is_a_share_specific_and_hashed() -> None:
    item = target()
    assert item.market_id == "A-SHARE"
    assert len(item.target_hash) == 64
    with pytest.raises(FrozenInstanceError):
        item.market_id = "BTC"  # type: ignore[misc]


def test_d1_target_rejects_unknown_family_and_unsafe_id() -> None:
    with pytest.raises(ValueError, match="target family"):
        target(target_family="UNKNOWN")
    with pytest.raises(ValueError, match="safe identifier"):
        target(target_id="target with spaces")


def test_d2_canonical_registry_covers_isolated_target_families() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    assert {item.target_family for item in registry.targets} == set(TARGET_FAMILIES)
    assert len({item.horizon_id for item in registry.targets}) == len(TARGET_FAMILIES)
    assert registry.research_priority_market_id == "A-SHARE"
    assert registry.selected_market_id is None


def test_d2_registry_rejects_duplicate_target_family() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    duplicate = replace(registry.targets[0], target_id="duplicate-target")
    with pytest.raises(ValueError, match="target families"):
        AShareMvpBaselineRegistry(
            registry.targets + (duplicate,),
            registry.data_requirements,
            registry.obligations,
        )


def test_d2_registry_cannot_authorize_product_phase_or_selection() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    with pytest.raises(ValueError, match="product phase"):
        replace(registry, phase_id="V2-R48")
    with pytest.raises(ValueError, match="cannot select"):
        replace(registry, selected_market_id="A-SHARE")


def test_d3_requirement_preserves_point_in_time_without_provider() -> None:
    item = requirement()
    assert item.point_in_time_required is True
    assert item.availability_time_required is True
    assert item.provider_id is None
    assert item.entitlement_approved is False


def test_d3_requirement_rejects_provider_and_entitlement_claims() -> None:
    with pytest.raises(ValueError, match="provider"):
        requirement(provider_id="vendor-a")
    with pytest.raises(ValueError, match="provider"):
        requirement(entitlement_approved=True)


def test_d3_canonical_manifest_covers_all_registered_domains() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    assert {item.domain for item in registry.data_requirements} == set(DATA_DOMAINS)
    assert all(item.point_in_time_required for item in registry.data_requirements)
    assert all(item.availability_time_required for item in registry.data_requirements)


def test_d3_missing_data_domain_is_visible() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    rows = tuple(
        item for item in registry.data_requirements if item.domain != "TRADE_PRINT"
    )
    result = evaluate_a_share_mvp_baseline(
        AShareMvpBaselineRegistry(registry.targets, rows, registry.obligations)
    )
    assert result.state == "BASELINE_INCOMPLETE"
    assert result.missing_data_domains == ("TRADE_PRINT",)


def test_d4_obligation_requires_registered_artifact_and_digest() -> None:
    with pytest.raises(ValueError, match="artifact and digest"):
        obligation(evidence_state="REGISTERED")
    registered = obligation(
        evidence_state="REGISTERED",
        evidence_artifact_id="registered-local-success-evidence",
        evidence_digest=DIGEST,
    )
    assert registered.evidence_state == "REGISTERED"


def test_d4_obligation_rejects_empirical_threshold_without_evidence_phase() -> None:
    with pytest.raises(ValueError, match="separate registered evidence"):
        obligation(empirical_threshold=0.5)


def test_d4_canonical_obligations_cover_acceptance_categories() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    assert {item.category for item in registry.obligations} == set(
        OBLIGATION_CATEGORIES
    )
    result = evaluate_a_share_mvp_baseline(registry)
    assert result.state == "READY_FOR_EVIDENCE_COLLECTION"
    assert len(result.evidence_required_obligation_ids) == len(OBLIGATION_CATEGORIES)


def test_d4_missing_obligation_category_is_visible() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    rows = tuple(
        item for item in registry.obligations if item.category != "STOP_RULE"
    )
    result = evaluate_a_share_mvp_baseline(
        AShareMvpBaselineRegistry(registry.targets, registry.data_requirements, rows)
    )
    assert result.state == "BASELINE_INCOMPLETE"
    assert result.missing_obligation_categories == ("STOP_RULE",)


def test_d4_registered_obligations_are_ready_only_for_operator_registration() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    rows = tuple(
        replace(
            item,
            evidence_state="REGISTERED",
            evidence_artifact_id=f"artifact-{item.obligation_id}",
            evidence_digest=DIGEST,
        )
        for item in registry.obligations
    )
    result = evaluate_a_share_mvp_baseline(
        AShareMvpBaselineRegistry(registry.targets, registry.data_requirements, rows)
    )
    assert result.state == "READY_FOR_OPERATOR_EVIDENCE_REGISTRATION"
    assert result.fcp_0005_readiness_claimed is False
    assert result.selected_market_id is None


def test_d5_evaluation_is_deterministic() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    left = evaluate_a_share_mvp_baseline(registry)
    right = evaluate_a_share_mvp_baseline(registry)
    assert left == right
    assert left.result_hash == right.result_hash


def test_d5_packet_is_deeply_read_only_at_mapping_boundaries() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    packet = build_a_share_mvp_baseline_packet(
        registry, evaluate_a_share_mvp_baseline(registry)
    )
    assert isinstance(packet.payload, MappingProxyType)
    assert isinstance(packet.payload["targets"][0], MappingProxyType)
    assert isinstance(packet.payload["data_requirements"][0], MappingProxyType)
    assert isinstance(packet.payload["obligations"][0], MappingProxyType)
    with pytest.raises(TypeError):
        packet.payload["selected_market_id"] = "A-SHARE"  # type: ignore[index]


def test_d5_acceptance_preserves_all_authority_boundaries() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    packet = build_a_share_mvp_baseline_packet(
        registry, evaluate_a_share_mvp_baseline(registry)
    )
    checks = validate_a_share_mvp_baseline_acceptance(packet)
    assert all(checks.values())
    assert packet.payload["proposal_status"] == "ACCEPTED_ARCHITECTURE"
    assert packet.payload["operator_decision"] == "ACCEPTED_ARCHITECTURE"


def test_d6_baseline_never_claims_fcp_0005_or_product_authority() -> None:
    registry = build_canonical_a_share_mvp_baseline()
    result = evaluate_a_share_mvp_baseline(registry)
    assert result.fcp_0005_readiness_claimed is False
    assert result.product_phase_authorized is False
    assert result.production_gap_closure_claimed is False
    assert result.selected_market_id is None
