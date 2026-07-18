from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import EvidenceFreshnessPolicy, RegisteredEvidenceArtifact
from .registry import LocalEvidenceIntegrityRegistry


@dataclass(frozen=True)
class EvidenceIntegritySnapshot:
    evidence_series_id: str
    market: str
    evaluated_at_utc: str
    state: str
    record: RegisteredEvidenceArtifact | None
    age_seconds: int | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        states = {
            "MISSING",
            "FUTURE_ONLY",
            "NOT_EFFECTIVE",
            "STALE",
            "RESOLVED_OBSERVED",
            "RESOLVED_INFERRED",
        }
        if self.state not in states or self.operator_review_required is not True:
            raise ValueError("invalid evidence integrity snapshot")


def resolve_evidence_integrity(
    registry: LocalEvidenceIntegrityRegistry,
    *,
    evidence_series_id: str,
    market: str,
    as_of_utc: str,
    freshness_policy: EvidenceFreshnessPolicy,
) -> EvidenceIntegritySnapshot:
    series_id = identifier(evidence_series_id, "evidence_series_id")
    market_id = identifier(market, "market")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    matching = tuple(
        item
        for item in registry.records
        if item.evidence_series_id == series_id and item.market == market_id
    )
    visible = tuple(item for item in matching if instant(item.available_at_utc) <= as_of)
    record = visible[-1] if visible else None
    age: int | None = None
    if record is None:
        state = "FUTURE_ONLY" if matching else "MISSING"
        reasons = (
            "REGISTERED_EVIDENCE_NOT_YET_AVAILABLE"
            if matching
            else "NO_REGISTERED_EVIDENCE_AT_AS_OF",
        )
    else:
        age = int((as_of - instant(record.effective_at_utc)).total_seconds())
        base_reasons = ("DIGEST_VERIFIED", "REVISION_LINEAGE_VERIFIED")
        if age < 0:
            state, reasons = "NOT_EFFECTIVE", (*base_reasons, "EVIDENCE_NOT_YET_EFFECTIVE")
        elif age > freshness_policy.max_age_seconds:
            state, reasons = "STALE", (*base_reasons, "FRESHNESS_LIMIT_EXCEEDED")
        elif record.origin == "OBSERVED":
            state, reasons = "RESOLVED_OBSERVED", (*base_reasons, "OBSERVED_SOURCE_VALUE")
        else:
            state, reasons = "RESOLVED_INFERRED", (*base_reasons, "REGISTERED_INFERENCE")
    payload = {
        "age_seconds": age,
        "evaluated_at_utc": evaluated,
        "market": market_id,
        "policy_id": freshness_policy.policy_id,
        "reasons": list(reasons),
        "record_hash": None if record is None else record.record_hash,
        "series_id": series_id,
        "state": state,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return EvidenceIntegritySnapshot(
        series_id, market_id, evaluated, state, record, age, tuple(reasons), True, digest
    )
