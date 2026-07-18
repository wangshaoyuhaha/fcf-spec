from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc

from .contracts import CalendarFreshnessPolicy, InstitutionalCalendarEvent


@dataclass(frozen=True)
class InstitutionalCalendarResolution:
    calendar_id: str
    event_id: str
    evaluated_at_utc: str
    state: str
    selected_record_hash: str | None
    revision_number: int | None
    first_tradable_at_utc: str | None
    freshness_age_seconds: int | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"BLOCKED", "MISSING", "RESOLVED"}:
            raise ValueError("invalid calendar resolution state")
        if self.operator_review_required is not True:
            raise ValueError("calendar resolution requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def resolve_institutional_calendar_event(
    records: tuple[InstitutionalCalendarEvent, ...],
    *,
    calendar_id: str,
    event_id: str,
    as_of_utc: str,
    freshness_policy: CalendarFreshnessPolicy,
) -> InstitutionalCalendarResolution:
    evaluated_at_utc = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated_at_utc)
    candidates = tuple(
        record
        for record in records
        if record.calendar_id == calendar_id and record.event_id == event_id
    )
    available = tuple(
        record
        for record in candidates
        if instant(record.first_legally_available_at_utc) <= as_of
        and instant(record.ingested_at_utc) <= as_of
    )
    selected: InstitutionalCalendarEvent | None = None
    state = "MISSING"
    reasons: tuple[str, ...] = ("EVENT_NOT_AVAILABLE_AT_AS_OF",)
    age: int | None = None
    if available:
        selected = max(available, key=lambda record: record.revision_number)
        age = int((as_of - instant(selected.ingested_at_utc)).total_seconds())
        if selected.revision_state == "CANCELLED":
            state = "BLOCKED"
            reasons = ("LATEST_AVAILABLE_REVISION_CANCELLED",)
        elif instant(selected.first_tradable_at_utc) > as_of:
            state = "BLOCKED"
            reasons = ("FIRST_TRADABLE_TIME_NOT_REACHED",)
        elif age > freshness_policy.max_age_seconds:
            state = "BLOCKED"
            reasons = ("REGISTERED_EVIDENCE_STALE",)
        else:
            state = "RESOLVED"
            reasons = ("POINT_IN_TIME_EVENT_RESOLVED",)
    payload = {
        "calendar_id": calendar_id,
        "evaluated_at_utc": evaluated_at_utc,
        "event_id": event_id,
        "first_tradable_at_utc": (
            selected.first_tradable_at_utc if selected is not None else None
        ),
        "freshness_age_seconds": age,
        "max_age_seconds": freshness_policy.max_age_seconds,
        "policy_id": freshness_policy.policy_id,
        "reason_codes": reasons,
        "revision_number": selected.revision_number if selected is not None else None,
        "selected_record_hash": selected.record_hash if selected is not None else None,
        "state": state,
    }
    evidence_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return InstitutionalCalendarResolution(
        calendar_id=calendar_id,
        event_id=event_id,
        evaluated_at_utc=evaluated_at_utc,
        state=state,
        selected_record_hash=(selected.record_hash if selected is not None else None),
        revision_number=(selected.revision_number if selected is not None else None),
        first_tradable_at_utc=(
            selected.first_tradable_at_utc if selected is not None else None
        ),
        freshness_age_seconds=age,
        reason_codes=reasons,
        operator_review_required=True,
        evidence_hash=evidence_hash,
    )
