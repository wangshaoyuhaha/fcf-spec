from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, localcontext

from apps.v2_r2_historical_factor_baseline_app_1 import HistoricalBaseline
from apps.v2_r2_historical_factor_baseline_app_1.contracts import decimal_value
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventEnvelope
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import AnomalyRule


_STATES = {"NORMAL", "WATCH", "CONFIRMED", "DEGRADED"}


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def _truthy_negative(value: object) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, (int, Decimal)) and not isinstance(value, bool):
        return decimal_value(value, "negative evidence") != 0
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "none", "clear"}
    return value is True


def _numeric(event: LocalEventEnvelope, field_key: str) -> Decimal:
    if field_key not in event.payload:
        raise ValueError("registered event is missing the anomaly field")
    value = event.payload[field_key]
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ValueError("anomaly field must be an integer or Decimal")
    return decimal_value(value, field_key)


def _direction_passes(z_score: Decimal, rule: AnomalyRule) -> bool:
    if rule.direction == "UP":
        return z_score >= rule.minimum_abs_z
    if rule.direction == "DOWN":
        return z_score <= -rule.minimum_abs_z
    return abs(z_score) >= rule.minimum_abs_z


@dataclass(frozen=True)
class AnomalyEvidence:
    rule_id: str
    rule_version: str
    context_id: str
    stream_id: str
    event_id: str
    state: str
    value: Decimal | None
    z_score: Decimal | None
    velocity_per_second: Decimal | None
    persistence_count: int
    negative_evidence: tuple[str, ...]
    reason_codes: tuple[str, ...]
    observed_at_utc: str
    expires_at_utc: str
    baseline_replay_hash: str
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in _STATES:
            raise ValueError("invalid anomaly research state")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def evaluate_anomaly_window(
    events: tuple[LocalEventEnvelope, ...],
    baseline: HistoricalBaseline,
    rule: AnomalyRule,
    *,
    as_of_utc: str,
) -> AnomalyEvidence:
    window = tuple(events)
    if not window or len(window) > 20:
        raise ValueError("event window must contain between 1 and 20 events")
    if not all(isinstance(event, LocalEventEnvelope) for event in window):
        raise ValueError("event window accepts LocalEventEnvelope only")
    stream_id = window[0].stream_id
    if any(event.stream_id != stream_id for event in window):
        raise ValueError("event window must contain one stream")
    for previous, current in zip(window, window[1:]):
        if current.source_sequence != previous.source_sequence + 1:
            raise ValueError("event window sequence must be contiguous")
        if instant(current.event_at_utc) <= instant(previous.event_at_utc):
            raise ValueError("event time must increase within the window")
    current = window[-1]
    as_of = instant(utc(as_of_utc, "as_of_utc"))
    observed = instant(current.processed_at_utc)
    expires = observed + timedelta(seconds=rule.evidence_ttl_seconds)
    state = "DEGRADED"
    reasons: list[str] = []
    value: Decimal | None = None
    z_score: Decimal | None = None
    velocity: Decimal | None = None
    persistence = 0
    negative = tuple(
        key
        for key in rule.negative_evidence_keys
        if key in current.payload and _truthy_negative(current.payload[key])
    )
    baseline_valid = (
        baseline.status == "READY"
        and baseline.replay_hash == rule.baseline_replay_hash
        and baseline.request.field_id == rule.field_key
    )
    if not baseline_valid:
        reasons.append("BASELINE_BLOCKED")
    elif baseline.standard_deviation == 0:
        reasons.append("ZERO_VARIANCE")
    elif current.clock_quality != "SYNCED":
        reasons.append("CLOCK_DEGRADED")
    elif observed > as_of:
        reasons.append("FUTURE_EVENT")
    elif (as_of - observed).total_seconds() > rule.max_event_age_seconds:
        reasons.append("STALE_EVENT")
    elif negative:
        reasons.append("NEGATIVE_EVIDENCE")
    else:
        values = tuple(_numeric(event, rule.field_key) for event in window)
        value = values[-1]
        z_values: list[Decimal] = []
        for item in values:
            status, standardized = baseline.standardize(item)
            if status != "READY" or standardized is None:
                reasons.append(status)
                break
            z_values.append(standardized)
        if not reasons:
            z_score = z_values[-1]
            for item in reversed(z_values):
                if _direction_passes(item, rule):
                    persistence += 1
                else:
                    break
            if len(values) >= 2:
                elapsed = Decimal(
                    str(
                        (
                            instant(window[-1].event_at_utc)
                            - instant(window[-2].event_at_utc)
                        ).total_seconds()
                    )
                )
                if elapsed <= 0:
                    raise ValueError("event-time velocity requires positive seconds")
                with localcontext() as context:
                    context.prec = 34
                    velocity = abs(values[-1] - values[-2]) / elapsed
            z_gate = _direction_passes(z_score, rule)
            velocity_gate = (
                velocity is not None and velocity >= rule.minimum_abs_velocity
            )
            persistence_gate = persistence >= rule.minimum_persistence
            if z_gate and velocity_gate and persistence_gate:
                state = "CONFIRMED"
                reasons.append("ALL_GATES_CONFIRMED")
            elif z_gate:
                state = "WATCH"
                reasons.append("PERSISTENCE_OR_VELOCITY_PENDING")
            else:
                state = "NORMAL"
                reasons.append("Z_GATE_CLEAR")
    payload = {
        "baseline_replay_hash": rule.baseline_replay_hash,
        "context_id": rule.context_id,
        "event_id": current.event_id,
        "expires_at_utc": expires.isoformat().replace("+00:00", "Z"),
        "negative_evidence": negative,
        "observed_at_utc": current.processed_at_utc,
        "persistence_count": persistence,
        "reasons": tuple(reasons),
        "rule_id": rule.rule_id,
        "rule_version": rule.rule_version,
        "state": state,
        "stream_id": stream_id,
        "value": _decimal_text(value),
        "velocity": _decimal_text(velocity),
        "z_score": _decimal_text(z_score),
    }
    evidence_hash = hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True
        ).encode("ascii")
    ).hexdigest()
    return AnomalyEvidence(
        rule_id=rule.rule_id,
        rule_version=rule.rule_version,
        context_id=rule.context_id,
        stream_id=stream_id,
        event_id=current.event_id,
        state=state,
        value=value,
        z_score=z_score,
        velocity_per_second=velocity,
        persistence_count=persistence,
        negative_evidence=negative,
        reason_codes=tuple(reasons),
        observed_at_utc=current.processed_at_utc,
        expires_at_utc=payload["expires_at_utc"],
        baseline_replay_hash=rule.baseline_replay_hash,
        evidence_hash=evidence_hash,
    )
