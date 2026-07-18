import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)

from .contracts import (
    InstitutionalCrowdingRecord,
    RegisteredInstitutionalHoldingDisclosure,
)
from .registry import LocalInstitutionalCrowdingRegistry


@dataclass(frozen=True)
class InstitutionalCrowdingSnapshot:
    subject_id: str
    market: str
    evaluated_at_utc: str
    state: str
    disclosures: tuple[RegisteredInstitutionalHoldingDisclosure, ...]
    record: InstitutionalCrowdingRecord | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        allowed = {
            "MISSING_DISCLOSURE",
            "MISSING",
            "STALE",
            "CONFLICT",
            "MISSING_METRICS",
            "RESOLVED",
        }
        if self.state not in allowed or self.operator_review_required is not True:
            raise ValueError("invalid institutional crowding snapshot")


def resolve_institutional_crowding(
    registry: LocalInstitutionalCrowdingRegistry,
    *,
    subject_id: str,
    market: str,
    as_of_utc: str,
) -> InstitutionalCrowdingSnapshot:
    subject = identifier(subject_id, "subject_id")
    market_id = identifier(market, "market")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    visible = tuple(
        item
        for item in registry.disclosures
        if item.subject_id == subject
        and item.market == market_id
        and instant(item.available_at_utc) <= as_of
    )
    if visible:
        period = max(item.report_period_end_utc for item in visible)
        disclosures = tuple(
            sorted(
                (item for item in visible if item.report_period_end_utc == period),
                key=lambda item: (item.fund_id, item.disclosure_id),
            )
        )
    else:
        disclosures = ()
    hashes = {item.disclosure_hash for item in disclosures}
    record = next(
        (
            item
            for item in reversed(registry.records)
            if {entry.disclosure_hash for entry in item.disclosures} == hashes
            and hashes
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    states = {item.disclosure_state for item in disclosures}
    if not disclosures:
        state, reasons = "MISSING_DISCLOSURE", [
            "NO_REGISTERED_INSTITUTIONAL_DISCLOSURE_AT_AS_OF"
        ]
    elif "CONFLICT" in states:
        state, reasons = "CONFLICT", ["REGISTERED_DISCLOSURE_IS_CONFLICTED"]
    elif "STALE" in states:
        state, reasons = "STALE", ["REGISTERED_DISCLOSURE_IS_STALE"]
    elif "MISSING" in states:
        state, reasons = "MISSING", ["REGISTERED_DISCLOSURE_IS_MISSING"]
    elif record is None:
        state, reasons = "MISSING_METRICS", [
            "NO_REGISTERED_CROWDING_METRICS_AT_AS_OF"
        ]
    else:
        state, reasons = "RESOLVED", [
            "REGISTERED_INSTITUTIONAL_CROWDING_EVIDENCE_RESOLVED",
            "DISCLOSURE_LATENCY_PRESERVED",
            "NO_CURRENT_MANAGER_ACTION_INFERENCE",
            "NO_QUARTER_END_MOTIVE_INFERENCE",
        ]
    payload = {
        "disclosures": sorted(hashes),
        "evaluated_at_utc": evaluated,
        "market": market_id,
        "reasons": reasons,
        "record": None if record is None else record.record_hash,
        "state": state,
        "subject_id": subject,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return InstitutionalCrowdingSnapshot(
        subject,
        market_id,
        evaluated,
        state,
        disclosures,
        record,
        tuple(reasons),
        True,
        digest,
    )
