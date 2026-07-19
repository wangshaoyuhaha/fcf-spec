from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import (
    ClaimBudgetAllocation,
    ConfidenceBudgetEvaluation,
    ConfidenceBudgetPolicy,
    DependenceGroupFinding,
    RegisteredDependenceGroup,
    RegisteredEvidenceClaim,
    _digest,
)
from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc


@dataclass(frozen=True)
class RegisteredEvidenceDependenceRegistry:
    claims: tuple[RegisteredEvidenceClaim, ...]
    groups: tuple[RegisteredDependenceGroup, ...]
    policy: ConfidenceBudgetPolicy
    evaluated_at_utc: str
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        claims = tuple(sorted(self.claims, key=lambda item: item.claim_id))
        groups = tuple(sorted(self.groups, key=lambda item: item.group_id))
        if not claims or not all(isinstance(item, RegisteredEvidenceClaim) for item in claims):
            raise ValueError("dependence registry requires registered evidence claims")
        if not groups or not all(isinstance(item, RegisteredDependenceGroup) for item in groups):
            raise ValueError("dependence registry requires registered groups")
        if not isinstance(self.policy, ConfidenceBudgetPolicy):
            raise ValueError("dependence registry requires a confidence budget policy")
        evaluated = utc(self.evaluated_at_utc, "evaluated_at_utc")
        if any(instant(item.available_at_utc) > instant(evaluated) for item in claims):
            raise ValueError("confidence budget cannot use future-available evidence")
        if len({item.claim_id for item in claims}) != len(claims):
            raise ValueError("duplicate evidence claim id is prohibited")
        if len({item.group_id for item in groups}) != len(groups):
            raise ValueError("duplicate dependence group id is prohibited")
        if any(item.policy_id != self.policy.policy_id for item in groups):
            raise ValueError("dependence group policy mismatch")
        claim_map = {item.claim_id: item for item in claims}
        memberships = [claim_id for group in groups for claim_id in group.claim_ids]
        if sorted(memberships) != sorted(claim_map):
            raise ValueError("each evidence claim must belong to exactly one group")
        for group in groups:
            group_claims = tuple(claim_map[claim_id] for claim_id in group.claim_ids)
            if any(item.dependence_group_id != group.group_id for item in group_claims):
                raise ValueError("claim dependence group mismatch")
            source_hashes = tuple(
                sorted({value for item in group_claims for value in item.source_artifact_hashes})
            )
            if source_hashes != group.registered_evidence_hashes:
                raise ValueError("dependence group evidence lineage must be exact")
        source_groups: dict[str, set[str]] = {}
        for claim in claims:
            for source_hash in claim.source_artifact_hashes:
                source_groups.setdefault(source_hash, set()).add(claim.dependence_group_id)
        if any(len(group_ids) > 1 for group_ids in source_groups.values()):
            raise ValueError("shared source evidence must remain in one dependence group")
        group_map = {item.group_id: item for item in groups}
        for source_hash, group_ids in source_groups.items():
            group_id = next(iter(group_ids))
            linked_claims = sum(source_hash in item.source_artifact_hashes for item in claims)
            if linked_claims > 1 and group_map[group_id].dependence_type == "INDEPENDENT":
                raise ValueError("shared source evidence cannot be independent")
        object.__setattr__(self, "claims", claims)
        object.__setattr__(self, "groups", groups)
        object.__setattr__(self, "evaluated_at_utc", evaluated)
        object.__setattr__(
            self,
            "registry_hash",
            _digest(
                {
                    "claim_hashes": [item.claim_hash for item in claims],
                    "evaluated_at_utc": evaluated,
                    "group_hashes": [item.group_hash for item in groups],
                    "policy_hash": self.policy.policy_hash,
                }
            ),
        )


def _allocate_largest_remainder(
    requests: tuple[tuple[str, int], ...],
    cap: int,
) -> dict[str, int]:
    total = sum(value for _, value in requests)
    if total == 0:
        return {item_id: 0 for item_id, _ in requests}
    applied = min(total, cap)
    rows = []
    allocated = 0
    for item_id, value in requests:
        floor, remainder = divmod(value * applied, total)
        rows.append((item_id, floor, remainder))
        allocated += floor
    winners = {
        item_id
        for item_id, _, _ in sorted(rows, key=lambda row: (-row[2], row[0]))[
            : applied - allocated
        ]
    }
    return {
        item_id: floor + (1 if item_id in winners else 0)
        for item_id, floor, _ in rows
    }


def evaluate_confidence_budget(
    registry: RegisteredEvidenceDependenceRegistry,
) -> ConfidenceBudgetEvaluation:
    claim_map = {item.claim_id: item for item in registry.claims}
    preliminary: dict[str, int] = {}
    requested_by_group: dict[str, int] = {}
    for group in registry.groups:
        requests = tuple(
            (claim_id, claim_map[claim_id].requested_confidence_bps)
            for claim_id in group.claim_ids
            if claim_map[claim_id].usability == "USABLE"
        )
        requested_by_group[group.group_id] = sum(value for _, value in requests)
        preliminary.update(_allocate_largest_remainder(requests, group.group_cap_bps))
        for claim_id in group.claim_ids:
            preliminary.setdefault(claim_id, 0)
    global_allocations = _allocate_largest_remainder(
        tuple(sorted(preliminary.items())), registry.policy.global_cap_bps
    )
    allocations = []
    for claim in registry.claims:
        allocated = global_allocations[claim.claim_id]
        signed = allocated if claim.stance == "SUPPORTING" else -allocated if claim.stance == "OPPOSING" else 0
        suppression = []
        if claim.usability != "USABLE":
            suppression.append(f"EVIDENCE_{claim.usability}_NOT_ALLOCATED")
        if allocated < claim.requested_confidence_bps and claim.usability == "USABLE":
            suppression.append("DEPENDENCE_OR_GLOBAL_BUDGET_APPLIED")
        allocations.append(
            ClaimBudgetAllocation(
                claim.claim_id,
                claim.dependence_group_id,
                claim.requested_confidence_bps,
                allocated,
                signed,
                tuple(suppression),
            )
        )
    allocations_tuple = tuple(allocations)
    allocated_by_group = {
        group.group_id: sum(
            item.allocated_confidence_bps
            for item in allocations_tuple
            if item.group_id == group.group_id
        )
        for group in registry.groups
    }
    findings = tuple(
        DependenceGroupFinding(
            group.group_id,
            group.dependence_type,
            group.claim_ids,
            requested_by_group[group.group_id],
            group.group_cap_bps,
            allocated_by_group[group.group_id],
            group.dependence_type != "INDEPENDENT"
            or requested_by_group[group.group_id] > allocated_by_group[group.group_id],
        )
        for group in registry.groups
    )
    supporting = sum(
        item.allocated_confidence_bps
        for item in allocations_tuple
        if claim_map[item.claim_id].stance == "SUPPORTING"
    )
    opposing = sum(
        item.allocated_confidence_bps
        for item in allocations_tuple
        if claim_map[item.claim_id].stance == "OPPOSING"
    )
    neutral = sum(
        item.allocated_confidence_bps
        for item in allocations_tuple
        if claim_map[item.claim_id].stance == "NEUTRAL"
    )
    gross_allocated = supporting + opposing + neutral
    reasons = []
    if any(item.usability == "AMBIGUOUS" for item in registry.claims):
        reasons.append("AMBIGUOUS_TAXONOMY_REQUIRES_ABSTENTION")
    if any(item.usability == "MISSING" for item in registry.claims):
        reasons.append("MISSING_EVIDENCE_VISIBLE")
    if any(item.usability == "BLOCKED" for item in registry.claims):
        reasons.append("BLOCKED_EVIDENCE_VISIBLE")
    if gross_allocated < registry.policy.minimum_usable_bps:
        reasons.append("INSUFFICIENT_USABLE_CONFIDENCE")
    if supporting and opposing:
        conflict_ratio = min(supporting, opposing) * 10_000 // max(supporting, opposing)
        if conflict_ratio >= registry.policy.conflict_abstention_ratio_bps:
            reasons.append("SUPPORTING_OPPOSING_CONFLICT_REQUIRES_ABSTENTION")
    usable_claims = tuple(item for item in registry.claims if item.usability == "USABLE")
    state = "READY_FOR_OPERATOR_REVIEW"
    if not usable_claims or gross_allocated == 0:
        state = "BLOCKED"
    elif reasons:
        state = "ABSTAIN"
    payload = {
        "abstention_reasons": reasons,
        "allocations": [item.__dict__ for item in allocations_tuple],
        "gross_allocated_bps": gross_allocated,
        "gross_requested_bps": sum(item.requested_confidence_bps for item in registry.claims),
        "group_findings": [item.__dict__ for item in findings],
        "net_confidence_bps": supporting - opposing,
        "opposing_bps": opposing,
        "operator_review_required": True,
        "policy_id": registry.policy.policy_id,
        "registry_hash": registry.registry_hash,
        "scoring_authority_claimed": False,
        "state": state,
        "supporting_bps": supporting,
        "neutral_bps": neutral,
    }
    return ConfidenceBudgetEvaluation(
        state=state,
        policy_id=registry.policy.policy_id,
        allocations=allocations_tuple,
        group_findings=findings,
        gross_requested_bps=payload["gross_requested_bps"],
        gross_allocated_bps=gross_allocated,
        supporting_bps=supporting,
        opposing_bps=opposing,
        neutral_bps=neutral,
        net_confidence_bps=supporting - opposing,
        abstention_reasons=tuple(reasons),
        operator_review_required=True,
        scoring_authority_claimed=False,
        evaluation_hash=_digest(payload),
    )
