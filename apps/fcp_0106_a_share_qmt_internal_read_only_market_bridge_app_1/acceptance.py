from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from .contracts import (
    DEFAULT_REGISTRATION,
    PHASE_ID,
    QmtBridgeBatchSnapshot,
    canonical_bytes,
    digest,
)


def build_live_operator_review_evidence(
    snapshot: QmtBridgeBatchSnapshot,
    *,
    observed_at_ms: int,
    minimum_event_count: int = 1,
) -> Mapping[str, object]:
    if not isinstance(snapshot, QmtBridgeBatchSnapshot):
        raise TypeError("snapshot must be exact QMT bridge snapshot")
    if snapshot.registration_hash != DEFAULT_REGISTRATION.registration_hash:
        raise ValueError("snapshot registration is not approved for live acceptance")
    if type(observed_at_ms) is not int or observed_at_ms <= 0:
        raise ValueError("observed_at_ms must be a positive integer")
    if type(minimum_event_count) is not int or not 1 <= minimum_event_count <= 100:
        raise ValueError("minimum_event_count is outside the safe range")
    if len(snapshot.accepted_events) < minimum_event_count:
        raise ValueError("snapshot does not meet the minimum event count")
    ordered = tuple(
        sorted(
            snapshot.accepted_events,
            key=lambda item: (
                item.received_at_ms,
                item.symbol,
                item.sequence,
            ),
        )
    )
    symbols = {item.symbol for item in ordered}
    if len(symbols) != 1:
        raise ValueError("live acceptance requires one registered symbol")
    sequences = tuple(item.sequence for item in ordered)
    expected_sequences = tuple(range(sequences[0], sequences[0] + len(sequences)))
    if sequences != expected_sequences:
        raise ValueError("event sequence continuity is incomplete")
    latest = max(
        ordered,
        key=lambda item: (
            item.received_at_ms,
            item.event_time_ms,
            item.symbol,
            item.sequence,
        ),
    )
    receive_age_ms = observed_at_ms - latest.received_at_ms
    event_age_ms = observed_at_ms - latest.event_time_ms
    receive_ages_ms = tuple(
        observed_at_ms - item.received_at_ms for item in ordered
    )
    event_ages_ms = tuple(
        observed_at_ms - item.event_time_ms for item in ordered
    )
    event_to_receive_lags_ms = tuple(
        item.received_at_ms - item.event_time_ms for item in ordered
    )
    if (
        min(receive_ages_ms) < -DEFAULT_REGISTRATION.max_future_skew_ms
        or max(receive_ages_ms) > DEFAULT_REGISTRATION.max_event_age_ms
    ):
        raise ValueError("receive clock is outside the live acceptance gate")
    if (
        min(event_ages_ms) < -DEFAULT_REGISTRATION.max_future_skew_ms
        or max(event_ages_ms) > DEFAULT_REGISTRATION.max_event_age_ms
    ):
        raise ValueError("market clock is outside the live acceptance gate")
    payload: dict[str, object] = {
        "accepted_event_count": len(snapshot.accepted_events),
        "account_authority": False,
        "bridge_state": snapshot.bridge_state,
        "candidate_status": "OPERATOR_REVIEW_REQUIRED",
        "data_promotion_authority": False,
        "event_age_ms": event_age_ms,
        "event_age_max_ms": max(event_ages_ms),
        "event_age_min_ms": min(event_ages_ms),
        "event_to_receive_lag_max_ms": max(event_to_receive_lags_ms),
        "event_to_receive_lag_min_ms": min(event_to_receive_lags_ms),
        "execution_authority": False,
        "latest_event_hash": latest.event_hash,
        "latest_received_at_ms": latest.received_at_ms,
        "market_data_authority": False,
        "observed_at_ms": observed_at_ms,
        "operator_review_required": True,
        "phase_id": PHASE_ID,
        "read_only": True,
        "realtime_gate_passed": True,
        "receive_age_ms": receive_age_ms,
        "receive_age_max_ms": max(receive_ages_ms),
        "receive_age_min_ms": min(receive_ages_ms),
        "registration_hash": snapshot.registration_hash,
        "sequence_first": sequences[0],
        "sequence_gap_count": 0,
        "sequence_last": sequences[-1],
        "session_span_ms": ordered[-1].received_at_ms - ordered[0].received_at_ms,
        "snapshot_hash": snapshot.snapshot_hash,
        "source_kind": latest.source_kind,
        "symbol": latest.symbol,
        "volume_unit": latest.volume_unit,
    }
    payload["evidence_hash"] = digest(payload)
    return MappingProxyType(payload)


def render_live_operator_review_evidence_json(
    snapshot: QmtBridgeBatchSnapshot,
    *,
    observed_at_ms: int,
    minimum_event_count: int = 1,
) -> str:
    evidence = build_live_operator_review_evidence(
        snapshot,
        observed_at_ms=observed_at_ms,
        minimum_event_count=minimum_event_count,
    )
    return canonical_bytes(evidence).decode("ascii")
