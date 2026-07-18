from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import (
    ExpectationGapRecord,
    RegisteredActualObservation,
    RegisteredConsensusSnapshot,
)
from .registry import LocalConsensusExpectationGapRegistry


@dataclass(frozen=True)
class ConsensusExpectationGapSnapshot:
    subject_id: str
    metric_id: str
    market: str
    horizon: str
    observed_at_utc: str
    evaluated_at_utc: str
    state: str
    consensus: RegisteredConsensusSnapshot | None
    actual: RegisteredActualObservation | None
    gap: ExpectationGapRecord | None
    available_revision_hashes: tuple[str, ...]
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {
            "MISSING_CONSENSUS",
            "MISSING_ACTUAL",
            "MISSING_GAP",
            "RESOLVED",
            "STALE_CONSENSUS",
        }:
            raise ValueError("invalid consensus expectation snapshot state")
        if self.operator_review_required is not True:
            raise ValueError("consensus expectation snapshot requires Operator review")


def resolve_consensus_expectation_gap(
    registry: LocalConsensusExpectationGapRegistry,
    *,
    subject_id: str,
    metric_id: str,
    market: str,
    horizon: str,
    observed_at_utc: str,
    as_of_utc: str,
) -> ConsensusExpectationGapSnapshot:
    subject = identifier(subject_id, "subject_id")
    metric = identifier(metric_id, "metric_id")
    market_id = identifier(market, "market")
    horizon_id = identifier(horizon, "horizon")
    observed_text = utc(observed_at_utc, "observed_at_utc")
    evaluated_text = utc(as_of_utc, "as_of_utc")
    observed = instant(observed_text)
    as_of = instant(evaluated_text)
    if observed > as_of:
        raise ValueError("consensus expectation resolution cannot use future observation")
    dimensions = (subject, metric, market_id, horizon_id)
    available_consensus = tuple(
        sorted(
            (
                item
                for item in registry.consensus_snapshots
                if (item.subject_id, item.metric_id, item.market, item.horizon)
                == dimensions
                and instant(item.ingested_at_utc) <= as_of
                and instant(item.consensus_as_of_utc) <= observed
            ),
            key=lambda item: (item.revision_number, item.ingested_at_utc),
        )
    )
    consensus = available_consensus[-1] if available_consensus else None
    available_actuals = tuple(
        sorted(
            (
                item
                for item in registry.actual_observations
                if (item.subject_id, item.metric_id, item.market, item.horizon)
                == dimensions
                and instant(item.available_at_utc) <= as_of
                and instant(item.observed_at_utc) <= observed
            ),
            key=lambda item: (item.available_at_utc, item.observation_id),
        )
    )
    actual = available_actuals[-1] if available_actuals else None
    gap = next(
        (
            item
            for item in reversed(registry.gap_records)
            if consensus is not None
            and actual is not None
            and item.consensus.snapshot_hash == consensus.snapshot_hash
            and item.actual.observation_hash == actual.observation_hash
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    if consensus is None or consensus.consensus_state != "AVAILABLE":
        state = "MISSING_CONSENSUS"
        reasons = ["NO_REGISTERED_AVAILABLE_CONSENSUS_AT_AS_OF"]
    elif consensus.freshness_state == "STALE":
        state = "STALE_CONSENSUS"
        reasons = ["LATEST_AVAILABLE_CONSENSUS_IS_STALE"]
    elif actual is None:
        state = "MISSING_ACTUAL"
        reasons = ["NO_REGISTERED_ACTUAL_AT_AS_OF"]
    elif gap is None:
        state = "MISSING_GAP"
        reasons = ["NO_REGISTERED_EXPECTATION_GAP_AT_AS_OF"]
    else:
        state = "RESOLVED"
        reasons = ["REGISTERED_EXPECTATION_GAP_RESOLVED"]
        if gap.standardized_gap is None:
            reasons.append("ZERO_DISPERSION_STANDARDIZED_GAP_UNAVAILABLE")
    payload = {
        "actual_hash": None if actual is None else actual.observation_hash,
        "available_revision_hashes": [item.snapshot_hash for item in available_consensus],
        "consensus_hash": None if consensus is None else consensus.snapshot_hash,
        "evaluated_at_utc": evaluated_text,
        "gap_hash": None if gap is None else gap.gap_hash,
        "horizon": horizon_id,
        "market": market_id,
        "metric_id": metric,
        "observed_at_utc": observed_text,
        "reason_codes": reasons,
        "state": state,
        "subject_id": subject,
    }
    snapshot_hash = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
            "ascii"
        )
    ).hexdigest()
    return ConsensusExpectationGapSnapshot(
        subject_id=subject,
        metric_id=metric,
        market=market_id,
        horizon=horizon_id,
        observed_at_utc=observed_text,
        evaluated_at_utc=evaluated_text,
        state=state,
        consensus=consensus,
        actual=actual,
        gap=gap,
        available_revision_hashes=tuple(item.snapshot_hash for item in available_consensus),
        reason_codes=tuple(reasons),
        operator_review_required=True,
        snapshot_hash=snapshot_hash,
    )
