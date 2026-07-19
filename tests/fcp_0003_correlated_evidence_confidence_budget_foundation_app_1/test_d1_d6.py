from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.fcp_0003_correlated_evidence_confidence_budget_foundation_app_1 import (
    FCP_0003_BOUNDARY,
    ConfidenceBudgetPolicy,
    CorrelatedEvidenceConfidenceBudgetBoundary,
    RegisteredDependenceGroup,
    RegisteredEvidenceClaim,
    RegisteredEvidenceDependenceRegistry,
    build_confidence_budget_review_packet,
    evaluate_confidence_budget,
    validate_confidence_budget_acceptance,
)


H1, H2, H3 = "a" * 64, "b" * 64, "c" * 64


def _claim(
    claim_id: str,
    group_id: str,
    *,
    scope: str = "MACRO",
    stance: str = "SUPPORTING",
    usability: str = "USABLE",
    requested: int = 6_000,
    hashes: tuple[str, ...] = (H1,),
    taxonomies: tuple[str, ...] = ("taxonomy-a",),
) -> RegisteredEvidenceClaim:
    return RegisteredEvidenceClaim(
        claim_id=claim_id,
        scope=scope,
        stance=stance,
        usability=usability,
        requested_confidence_bps=requested,
        dependence_group_id=group_id,
        taxonomy_ids=taxonomies,
        source_artifact_hashes=hashes,
        reason_codes=("registered-reason",),
        observed_at_utc="2026-07-19T10:00:00Z",
        available_at_utc="2026-07-19T10:01:00Z",
    )


def _policy(**changes: int) -> ConfidenceBudgetPolicy:
    values = {
        "global_cap_bps": 7_000,
        "minimum_usable_bps": 1_000,
        "conflict_abstention_ratio_bps": 9_000,
    }
    values.update(changes)
    return ConfidenceBudgetPolicy("policy-a", **values)


def _registry() -> RegisteredEvidenceDependenceRegistry:
    claims = (
        _claim("claim-a", "group-shared", hashes=(H1,)),
        _claim(
            "claim-b",
            "group-shared",
            scope="SECTOR",
            hashes=(H1, H2),
        ),
        _claim(
            "claim-c",
            "group-independent",
            scope="INSTRUMENT",
            stance="OPPOSING",
            requested=2_000,
            hashes=(H3,),
        ),
    )
    groups = (
        RegisteredDependenceGroup(
            "group-shared",
            "SHARED_SOURCE",
            ("claim-a", "claim-b"),
            6_000,
            "policy-a",
            (H1, H2),
        ),
        RegisteredDependenceGroup(
            "group-independent",
            "INDEPENDENT",
            ("claim-c",),
            3_000,
            "policy-a",
            (H3,),
        ),
    )
    return RegisteredEvidenceDependenceRegistry(
        claims, groups, _policy(), "2026-07-19T10:02:00Z"
    )


def test_d1_boundary_is_fail_closed() -> None:
    assert FCP_0003_BOUNDARY.read_only is True
    assert FCP_0003_BOUNDARY.automatic_scoring_allowed is False
    with pytest.raises(ValueError, match="fail-closed"):
        CorrelatedEvidenceConfidenceBudgetBoundary(automatic_scoring_allowed=True)


def test_d1_claim_hash_is_deterministic_and_registered() -> None:
    left = _claim("claim-a", "group-a")
    right = _claim("claim-a", "group-a")
    assert left.claim_hash == right.claim_hash
    with pytest.raises(ValueError, match="Operator registration"):
        replace(left, operator_registered=False)


def test_d1_missing_evidence_cannot_request_confidence() -> None:
    with pytest.raises(ValueError, match="missing evidence"):
        _claim("claim-missing", "group-missing", usability="MISSING", hashes=())


def test_d2_registry_requires_exact_one_group_membership() -> None:
    registry = _registry()
    with pytest.raises(ValueError, match="exactly one group"):
        RegisteredEvidenceDependenceRegistry(
            registry.claims,
            (registry.groups[0],),
            registry.policy,
            registry.evaluated_at_utc,
        )


def test_d2_shared_source_cannot_cross_groups() -> None:
    first = _claim("claim-a", "group-a", hashes=(H1,))
    second = _claim("claim-b", "group-b", hashes=(H1,))
    groups = (
        RegisteredDependenceGroup("group-a", "INDEPENDENT", ("claim-a",), 5_000, "policy-a", (H1,)),
        RegisteredDependenceGroup("group-b", "INDEPENDENT", ("claim-b",), 5_000, "policy-a", (H1,)),
    )
    with pytest.raises(ValueError, match="shared source evidence"):
        RegisteredEvidenceDependenceRegistry(
            (first, second), groups, _policy(), "2026-07-19T10:02:00Z"
        )


def test_d2_registry_hash_changes_with_policy() -> None:
    registry = _registry()
    changed = RegisteredEvidenceDependenceRegistry(
        registry.claims,
        tuple(replace(item, policy_id="policy-b") for item in registry.groups),
        ConfidenceBudgetPolicy("policy-b", 6_000, 1_000, 9_000),
        registry.evaluated_at_utc,
    )
    assert changed.registry_hash != registry.registry_hash


def test_d3_group_then_global_budget_is_deterministic() -> None:
    left = evaluate_confidence_budget(_registry())
    right = evaluate_confidence_budget(_registry())
    assert left == right
    assert left.gross_requested_bps == 14_000
    assert left.gross_allocated_bps == 7_000
    assert left.supporting_bps == 5_250
    assert left.opposing_bps == 1_750
    assert [item.allocated_confidence_bps for item in left.allocations] == [2_625, 2_625, 1_750]
    assert left.group_findings[1].repeated_confirmation_prevented is True


def test_d3_no_allocation_exceeds_claim_group_or_global_cap() -> None:
    evaluation = evaluate_confidence_budget(_registry())
    assert all(item.allocated_confidence_bps <= item.requested_confidence_bps for item in evaluation.allocations)
    assert all(item.allocated_confidence_bps <= item.group_cap_bps for item in evaluation.group_findings)
    assert evaluation.gross_allocated_bps <= _registry().policy.global_cap_bps


def test_d4_ambiguous_taxonomy_abstains_and_allocates_zero() -> None:
    usable = _claim("claim-a", "group-shared", hashes=(H1,))
    ambiguous = _claim(
        "claim-b",
        "group-shared",
        usability="AMBIGUOUS",
        hashes=(H1, H2),
        taxonomies=("taxonomy-a", "taxonomy-b"),
    )
    group = RegisteredDependenceGroup(
        "group-shared", "SHARED_SOURCE", ("claim-a", "claim-b"), 6_000, "policy-a", (H1, H2)
    )
    result = evaluate_confidence_budget(
        RegisteredEvidenceDependenceRegistry(
            (usable, ambiguous), (group,), _policy(), "2026-07-19T10:02:00Z"
        )
    )
    assert result.state == "ABSTAIN"
    assert result.allocations[1].allocated_confidence_bps == 0
    assert "AMBIGUOUS_TAXONOMY_REQUIRES_ABSTENTION" in result.abstention_reasons


def test_d4_missing_only_registry_is_blocked() -> None:
    claim = _claim(
        "claim-missing",
        "group-missing",
        usability="MISSING",
        requested=0,
        hashes=(),
    )
    group = RegisteredDependenceGroup(
        "group-missing", "INDEPENDENT", ("claim-missing",), 1_000, "policy-a", ()
    )
    result = evaluate_confidence_budget(
        RegisteredEvidenceDependenceRegistry(
            (claim,), (group,), _policy(), "2026-07-19T10:02:00Z"
        )
    )
    assert result.state == "BLOCKED"
    assert result.gross_allocated_bps == 0
    assert "MISSING_EVIDENCE_VISIBLE" in result.abstention_reasons


def test_d4_material_support_opposition_conflict_abstains() -> None:
    support = _claim("claim-support", "group-support", requested=4_000, hashes=(H1,))
    oppose = _claim(
        "claim-oppose", "group-oppose", stance="OPPOSING", requested=4_000, hashes=(H2,)
    )
    groups = (
        RegisteredDependenceGroup("group-support", "INDEPENDENT", ("claim-support",), 4_000, "policy-a", (H1,)),
        RegisteredDependenceGroup("group-oppose", "INDEPENDENT", ("claim-oppose",), 4_000, "policy-a", (H2,)),
    )
    policy = _policy(global_cap_bps=8_000, conflict_abstention_ratio_bps=5_000)
    result = evaluate_confidence_budget(
        RegisteredEvidenceDependenceRegistry(
            (support, oppose), groups, policy, "2026-07-19T10:02:00Z"
        )
    )
    assert result.state == "ABSTAIN"
    assert result.net_confidence_bps == 0
    assert "SUPPORTING_OPPOSING_CONFLICT_REQUIRES_ABSTENTION" in result.abstention_reasons


def test_d5_review_packet_is_immutable_and_research_only() -> None:
    registry = _registry()
    packet = build_confidence_budget_review_packet(
        registry, evaluate_confidence_budget(registry)
    )
    assert isinstance(packet.payload, MappingProxyType)
    assert packet.payload["proposal_status"] == "NEEDS_RESEARCH"
    assert packet.payload["scoring_authority_claimed"] is False
    assert all(validate_confidence_budget_acceptance(packet).values())
    with pytest.raises(TypeError):
        packet.payload["proposal_status"] = "IMPLEMENTED"  # type: ignore[index]


def test_d2_future_available_evidence_is_rejected() -> None:
    registry = _registry()
    with pytest.raises(ValueError, match="future-available evidence"):
        RegisteredEvidenceDependenceRegistry(
            registry.claims,
            registry.groups,
            registry.policy,
            "2026-07-19T10:00:30Z",
        )
