from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import (
    EventReactionQualityRecord,
    RegisteredReactionObservation,
    RegisteredReactionWindow,
)
from .registry import LocalEventReactionQualityRegistry


@dataclass(frozen=True)
class EventReactionQualitySnapshot:
    subject_id: str
    market: str
    horizon: str
    evaluated_at_utc: str
    state: str
    window: RegisteredReactionWindow | None
    observation: RegisteredReactionObservation | None
    quality: EventReactionQualityRecord | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {
            "MISSING_WINDOW",
            "IMMATURE",
            "MISSING_OBSERVATION",
            "MISSING_QUALITY",
            "STALE",
            "CONFLICT",
            "RESOLVED",
        }:
            raise ValueError("invalid event reaction quality snapshot state")
        if self.operator_review_required is not True:
            raise ValueError("event reaction snapshot requires Operator review")


def resolve_event_reaction_quality(
    registry: LocalEventReactionQualityRegistry,
    *,
    subject_id: str,
    market: str,
    horizon: str,
    as_of_utc: str,
) -> EventReactionQualitySnapshot:
    subject = identifier(subject_id, "subject_id")
    market_id = identifier(market, "market")
    horizon_id = identifier(horizon, "horizon")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    dimensions = (subject, market_id, horizon_id)
    windows = tuple(
        sorted(
            (
                item
                for item in registry.windows
                if (item.subject_id, item.market, item.horizon) == dimensions
                and instant(item.available_at_utc) <= as_of
            ),
            key=lambda item: (item.first_tradable_at_utc, item.window_id),
        )
    )
    window = windows[-1] if windows else None
    observation = next(
        (
            item
            for item in reversed(registry.observations)
            if window is not None
            and item.window.window_hash == window.window_hash
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    quality = next(
        (
            item
            for item in reversed(registry.quality_records)
            if observation is not None
            and item.observation.observation_hash == observation.observation_hash
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    if window is None:
        state = "MISSING_WINDOW"
        reasons = ["NO_REGISTERED_REACTION_WINDOW_AT_AS_OF"]
    elif as_of < instant(window.matures_at_utc):
        state = "IMMATURE"
        reasons = ["REACTION_OUTCOME_NOT_MATURE_AT_AS_OF"]
    elif observation is None:
        state = "MISSING_OBSERVATION"
        reasons = ["NO_REGISTERED_REACTION_OBSERVATION_AT_AS_OF"]
    elif observation.reaction_state == "STALE":
        state = "STALE"
        reasons = ["REGISTERED_REACTION_OBSERVATION_IS_STALE"]
    elif observation.reaction_state == "CONFLICT":
        state = "CONFLICT"
        reasons = ["REGISTERED_REACTION_OBSERVATION_IS_CONFLICTED"]
    elif observation.reaction_state == "MISSING":
        state = "MISSING_OBSERVATION"
        reasons = ["REGISTERED_REACTION_MEASUREMENTS_ARE_MISSING"]
    elif quality is None:
        state = "MISSING_QUALITY"
        reasons = ["NO_MATURED_REACTION_QUALITY_RECORD_AT_AS_OF"]
    else:
        state = "RESOLVED"
        reasons = ["REGISTERED_REACTION_QUALITY_RESOLVED"]
        if quality.close_location_bps is None:
            reasons.append("ZERO_RANGE_CLOSE_LOCATION_UNAVAILABLE")
        if quality.reaction_label in {
            "FAVORABLE_WEAK_REACTION",
            "UNFAVORABLE_RESILIENT_REACTION",
        }:
            reasons.append("EXPECTATION_AND_REACTION_DIVERGE")
    payload = {
        "evaluated_at_utc": evaluated,
        "horizon": horizon_id,
        "market": market_id,
        "observation_hash": None if observation is None else observation.observation_hash,
        "quality_hash": None if quality is None else quality.quality_hash,
        "reason_codes": reasons,
        "state": state,
        "subject_id": subject,
        "window_hash": None if window is None else window.window_hash,
    }
    snapshot_hash = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
            "ascii"
        )
    ).hexdigest()
    return EventReactionQualitySnapshot(
        subject_id=subject,
        market=market_id,
        horizon=horizon_id,
        evaluated_at_utc=evaluated,
        state=state,
        window=window,
        observation=observation,
        quality=quality,
        reason_codes=tuple(reasons),
        operator_review_required=True,
        snapshot_hash=snapshot_hash,
    )
