from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from .contracts import (
    EVIDENCE_DIMENSIONS,
    CandidateReadinessResult,
    MvpProductReadinessDecision,
    MvpProductReadinessRegistry,
    ProductReadinessEvidence,
    digest,
    utc_time,
)


def _candidate_result(
    candidate_id: str,
    evidence: tuple[ProductReadinessEvidence, ...],
    as_of_time: datetime,
) -> CandidateReadinessResult:
    by_dimension: dict[str, list[ProductReadinessEvidence]] = defaultdict(list)
    for item in evidence:
        if item.candidate_id == candidate_id:
            by_dimension[item.dimension].append(item)

    missing = []
    stale = []
    blocked = []
    conflicts = []
    not_yet_available = []
    used_ids = []
    for dimension in EVIDENCE_DIMENSIONS:
        items = sorted(by_dimension.get(dimension, ()), key=lambda item: item.evidence_id)
        if not items:
            missing.append(dimension)
            continue
        used_ids.extend(item.evidence_id for item in items)
        if len(items) != 1:
            conflicts.append(dimension)
            continue
        item = items[0]
        if item.available_at > as_of_time:
            not_yet_available.append(dimension)
        elif item.expires_at <= as_of_time:
            stale.append(dimension)
        elif item.state == "BLOCKED":
            blocked.append(dimension)

    state = "READY_FOR_OPERATOR_DECISION"
    if blocked:
        state = "BLOCKED"
    elif missing or stale or conflicts or not_yet_available:
        state = "NEEDS_EVIDENCE"
    payload = {
        "blocked_dimensions": tuple(blocked),
        "candidate_id": candidate_id,
        "conflict_dimensions": tuple(conflicts),
        "evidence_ids": tuple(sorted(used_ids)),
        "missing_dimensions": tuple(missing),
        "not_yet_available_dimensions": tuple(not_yet_available),
        "stale_dimensions": tuple(stale),
        "state": state,
    }
    return CandidateReadinessResult(
        candidate_id=candidate_id,
        state=state,
        evidence_ids=payload["evidence_ids"],
        missing_dimensions=payload["missing_dimensions"],
        stale_dimensions=payload["stale_dimensions"],
        blocked_dimensions=payload["blocked_dimensions"],
        conflict_dimensions=payload["conflict_dimensions"],
        not_yet_available_dimensions=payload["not_yet_available_dimensions"],
        readiness_hash=digest(payload),
    )


def evaluate_mvp_product_readiness(
    registry: MvpProductReadinessRegistry,
    as_of_time: datetime,
) -> MvpProductReadinessDecision:
    as_of_time = utc_time(as_of_time, "as_of_time")
    results = tuple(
        _candidate_result(candidate.candidate_id, registry.evidence, as_of_time)
        for candidate in registry.candidates
    )
    ready_ids = tuple(
        item.candidate_id
        for item in results
        if item.state == "READY_FOR_OPERATOR_DECISION"
    )
    state = "READY_FOR_OPERATOR_DECISION" if ready_ids else "ABSTAIN"
    payload = {
        "as_of_time": as_of_time.isoformat(),
        "automatic_ranking_applied": False,
        "candidate_readiness_hashes": tuple(item.readiness_hash for item in results),
        "operator_review_required": True,
        "production_gap_closure_claimed": False,
        "ready_candidate_ids": ready_ids,
        "registry_hash": registry.registry_hash,
        "selected_market_id": None,
        "state": state,
    }
    return MvpProductReadinessDecision(
        state=state,
        as_of_time=as_of_time,
        registry_hash=registry.registry_hash,
        candidate_results=results,
        ready_candidate_ids=ready_ids,
        selected_market_id=None,
        operator_review_required=True,
        automatic_ranking_applied=False,
        production_gap_closure_claimed=False,
        decision_hash=digest(payload),
    )
