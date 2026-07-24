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
) -> Mapping[str, object]:
    if not isinstance(snapshot, QmtBridgeBatchSnapshot):
        raise TypeError("snapshot must be exact QMT bridge snapshot")
    if type(observed_at_ms) is not int or observed_at_ms <= 0:
        raise ValueError("observed_at_ms must be a positive integer")
    latest = max(
        snapshot.accepted_events,
        key=lambda item: (
            item.received_at_ms,
            item.event_time_ms,
            item.symbol,
            item.sequence,
        ),
    )
    receive_age_ms = observed_at_ms - latest.received_at_ms
    event_age_ms = observed_at_ms - latest.event_time_ms
    if not (
        -DEFAULT_REGISTRATION.max_future_skew_ms
        <= receive_age_ms
        <= DEFAULT_REGISTRATION.max_event_age_ms
    ):
        raise ValueError("receive clock is outside the live acceptance gate")
    if not (
        -DEFAULT_REGISTRATION.max_future_skew_ms
        <= event_age_ms
        <= DEFAULT_REGISTRATION.max_event_age_ms
    ):
        raise ValueError("market clock is outside the live acceptance gate")
    payload: dict[str, object] = {
        "accepted_event_count": len(snapshot.accepted_events),
        "account_authority": False,
        "bridge_state": snapshot.bridge_state,
        "candidate_status": "OPERATOR_REVIEW_REQUIRED",
        "data_promotion_authority": False,
        "event_age_ms": event_age_ms,
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
        "registration_hash": snapshot.registration_hash,
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
) -> str:
    evidence = build_live_operator_review_evidence(
        snapshot,
        observed_at_ms=observed_at_ms,
    )
    return canonical_bytes(evidence).decode("ascii")
