from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from types import MappingProxyType

import pytest

from apps.fcp_0005_mvp_product_readiness_decision_gate_app_1 import (
    EVIDENCE_DIMENSIONS,
    FCP_0005_BOUNDARY,
    MvpMarketCandidate,
    MvpProductReadinessBoundary,
    MvpProductReadinessRegistry,
    ProductReadinessEvidence,
    build_mvp_product_readiness_packet,
    evaluate_mvp_product_readiness,
    validate_mvp_product_readiness_acceptance,
)


NOW = datetime(2026, 7, 20, 1, 0, tzinfo=timezone.utc)
DIGEST = "a" * 64


def candidate(candidate_id: str = "candidate-a-share", market_id: str = "A-SHARE") -> MvpMarketCandidate:
    return MvpMarketCandidate(
        candidate_id=candidate_id,
        market_id=market_id,
        adapter_id=f"adapter-{candidate_id}",
        horizon_id=f"horizon-{candidate_id}",
        target_id=f"target-{candidate_id}",
    )


def evidence(
    candidate_id: str,
    dimension: str,
    *,
    suffix: str = "primary",
    state: str = "READY",
    available_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> ProductReadinessEvidence:
    available = available_at or NOW - timedelta(days=1)
    expires = expires_at or NOW + timedelta(days=30)
    dimension_id = dimension.lower().replace("_", "-")
    return ProductReadinessEvidence(
        evidence_id=f"evidence-{candidate_id}-{dimension_id}-{suffix}",
        candidate_id=candidate_id,
        dimension=dimension,
        artifact_id=f"artifact-{candidate_id}-{dimension_id}-{suffix}",
        available_at=available,
        expires_at=expires,
        state=state,
        evidence_digest=DIGEST,
    )


def complete_evidence(candidate_id: str) -> tuple[ProductReadinessEvidence, ...]:
    return tuple(evidence(candidate_id, dimension) for dimension in EVIDENCE_DIMENSIONS)


def registry(
    candidates: tuple[MvpMarketCandidate, ...] | None = None,
    evidence_rows: tuple[ProductReadinessEvidence, ...] | None = None,
) -> MvpProductReadinessRegistry:
    rows = candidates or (candidate(),)
    evidence_values = evidence_rows
    if evidence_values is None:
        evidence_values = complete_evidence(rows[0].candidate_id)
    return MvpProductReadinessRegistry(rows, evidence_values)


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0005_BOUNDARY.read_only is True
    assert FCP_0005_BOUNDARY.market_selection_allowed is False
    assert FCP_0005_BOUNDARY.phase_authorization_allowed is False
    assert FCP_0005_BOUNDARY.execution_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0005_BOUNDARY.network_allowed = True  # type: ignore[misc]


def test_d1_boundary_rejects_market_selection() -> None:
    with pytest.raises(ValueError, match="fail-closed"):
        MvpProductReadinessBoundary(market_selection_allowed=True)


def test_d1_candidate_is_immutable_and_hashed() -> None:
    item = candidate()
    assert len(item.candidate_hash) == 64
    with pytest.raises(FrozenInstanceError):
        item.market_id = "BTC"  # type: ignore[misc]


def test_d1_candidate_rejects_unsafe_identifier() -> None:
    with pytest.raises(ValueError, match="safe identifier"):
        candidate("candidate with spaces")


def test_d2_evidence_rejects_non_utc_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware UTC"):
        evidence("candidate-a-share", EVIDENCE_DIMENSIONS[0], available_at=datetime(2026, 7, 1))


def test_d2_evidence_rejects_bad_expiry() -> None:
    with pytest.raises(ValueError, match="expiry"):
        evidence(
            "candidate-a-share",
            EVIDENCE_DIMENSIONS[0],
            available_at=NOW,
            expires_at=NOW,
        )


def test_d2_evidence_rejects_unregistered_dimension() -> None:
    with pytest.raises(ValueError, match="dimension"):
        evidence("candidate-a-share", "UNKNOWN_DIMENSION")


def test_d2_registry_rejects_duplicate_market() -> None:
    with pytest.raises(ValueError, match="one candidate per market"):
        registry(
            candidates=(candidate(), candidate("candidate-second", "A-SHARE")),
            evidence_rows=(),
        )


def test_d2_registry_rejects_unknown_candidate_evidence() -> None:
    with pytest.raises(ValueError, match="unknown candidate"):
        registry(
            evidence_rows=(evidence("candidate-btc", EVIDENCE_DIMENSIONS[0]),),
        )


def test_d2_registry_cannot_authorize_phase() -> None:
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(registry(), phase_id="V2-R48")


def test_d3_complete_candidate_is_ready_for_operator_decision() -> None:
    result = evaluate_mvp_product_readiness(registry(), NOW)
    assert result.state == "READY_FOR_OPERATOR_DECISION"
    assert result.ready_candidate_ids == ("candidate-a-share",)
    assert result.selected_market_id is None
    assert result.automatic_ranking_applied is False


def test_d3_missing_dimension_abstains() -> None:
    rows = complete_evidence("candidate-a-share")[:-1]
    result = evaluate_mvp_product_readiness(registry(evidence_rows=rows), NOW)
    assert result.state == "ABSTAIN"
    assert result.candidate_results[0].state == "NEEDS_EVIDENCE"
    assert result.candidate_results[0].missing_dimensions == (EVIDENCE_DIMENSIONS[-1],)


def test_d3_stale_dimension_abstains() -> None:
    rows = list(complete_evidence("candidate-a-share"))
    rows[0] = evidence(
        "candidate-a-share",
        EVIDENCE_DIMENSIONS[0],
        expires_at=NOW,
    )
    result = evaluate_mvp_product_readiness(registry(evidence_rows=tuple(rows)), NOW)
    assert result.candidate_results[0].stale_dimensions == (EVIDENCE_DIMENSIONS[0],)
    assert result.state == "ABSTAIN"


def test_d3_future_available_dimension_abstains() -> None:
    rows = list(complete_evidence("candidate-a-share"))
    rows[0] = evidence(
        "candidate-a-share",
        EVIDENCE_DIMENSIONS[0],
        available_at=NOW + timedelta(days=1),
        expires_at=NOW + timedelta(days=2),
    )
    result = evaluate_mvp_product_readiness(registry(evidence_rows=tuple(rows)), NOW)
    assert result.candidate_results[0].not_yet_available_dimensions == (EVIDENCE_DIMENSIONS[0],)


def test_d3_blocked_dimension_blocks_candidate() -> None:
    rows = list(complete_evidence("candidate-a-share"))
    rows[0] = evidence("candidate-a-share", EVIDENCE_DIMENSIONS[0], state="BLOCKED")
    result = evaluate_mvp_product_readiness(registry(evidence_rows=tuple(rows)), NOW)
    assert result.candidate_results[0].state == "BLOCKED"
    assert result.candidate_results[0].blocked_dimensions == (EVIDENCE_DIMENSIONS[0],)


def test_d3_duplicate_dimension_is_visible_conflict() -> None:
    rows = complete_evidence("candidate-a-share") + (
        evidence("candidate-a-share", EVIDENCE_DIMENSIONS[0], suffix="conflict"),
    )
    result = evaluate_mvp_product_readiness(registry(evidence_rows=rows), NOW)
    assert result.candidate_results[0].conflict_dimensions == (EVIDENCE_DIMENSIONS[0],)
    assert result.state == "ABSTAIN"


def test_d4_two_ready_candidates_are_not_ranked_or_selected() -> None:
    candidates = (
        candidate(),
        candidate("candidate-btc", "BTC"),
    )
    rows = complete_evidence("candidate-a-share") + complete_evidence("candidate-btc")
    result = evaluate_mvp_product_readiness(registry(candidates, rows), NOW)
    assert result.ready_candidate_ids == ("candidate-a-share", "candidate-btc")
    assert result.selected_market_id is None
    assert result.automatic_ranking_applied is False


def test_d4_decision_is_deterministic() -> None:
    left = evaluate_mvp_product_readiness(registry(), NOW)
    right = evaluate_mvp_product_readiness(registry(), NOW)
    assert left == right
    assert left.decision_hash == right.decision_hash


def test_d5_packet_is_deeply_read_only_at_mapping_boundaries() -> None:
    packet = build_mvp_product_readiness_packet(evaluate_mvp_product_readiness(registry(), NOW))
    assert isinstance(packet.payload, MappingProxyType)
    assert isinstance(packet.payload["candidate_results"][0], MappingProxyType)
    with pytest.raises(TypeError):
        packet.payload["selected_market_id"] = "A-SHARE"  # type: ignore[index]


def test_d5_acceptance_preserves_authority() -> None:
    packet = build_mvp_product_readiness_packet(evaluate_mvp_product_readiness(registry(), NOW))
    checks = validate_mvp_product_readiness_acceptance(packet)
    assert all(checks.values())
    assert packet.payload["proposal_status"] == "NEEDS_RESEARCH"
    assert packet.payload["operator_decision"] == "PENDING"


def test_d6_packet_cannot_be_replaced_with_phase_authority() -> None:
    packet = build_mvp_product_readiness_packet(evaluate_mvp_product_readiness(registry(), NOW))
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(packet, phase_authorization_allowed=True)
