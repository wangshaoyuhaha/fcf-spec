from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import EquitySupplyPressureRecord, RegisteredEquitySupplyObservation
from .registry import LocalEquitySupplyPressureRegistry


@dataclass(frozen=True)
class EquitySupplyPressureSnapshot:
    subject_id: str
    market: str
    evaluated_at_utc: str
    state: str
    observation: RegisteredEquitySupplyObservation | None
    record: EquitySupplyPressureRecord | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"MISSING_OBSERVATION", "MISSING", "STALE", "CONFLICT", "MISSING_METRICS", "RESOLVED"}:
            raise ValueError("invalid equity supply snapshot state")
        if self.operator_review_required is not True:
            raise ValueError("equity supply snapshot requires Operator review")


def resolve_equity_supply_pressure(
    registry: LocalEquitySupplyPressureRegistry,
    *,
    subject_id: str,
    market: str,
    as_of_utc: str,
) -> EquitySupplyPressureSnapshot:
    subject = identifier(subject_id, "subject_id")
    market_id = identifier(market, "market")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    observations = tuple(
        sorted(
            (
                item for item in registry.observations
                if item.supply_event.subject_id == subject
                and item.supply_event.market == market_id
                and instant(item.available_at_utc) <= as_of
            ),
            key=lambda item: (item.observed_at_utc, item.observation_id),
        )
    )
    observation = observations[-1] if observations else None
    record = next(
        (
            item for item in reversed(registry.records)
            if observation is not None
            and item.observation.observation_hash == observation.observation_hash
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    if observation is None:
        state, reasons = "MISSING_OBSERVATION", ["NO_REGISTERED_SUPPLY_OBSERVATION_AT_AS_OF"]
    elif observation.observation_state == "MISSING":
        state, reasons = "MISSING", ["REGISTERED_SUPPLY_EVIDENCE_IS_MISSING"]
    elif observation.observation_state == "STALE":
        state, reasons = "STALE", ["REGISTERED_SUPPLY_EVIDENCE_IS_STALE"]
    elif observation.observation_state == "CONFLICT":
        state, reasons = "CONFLICT", ["REGISTERED_SUPPLY_EVIDENCE_IS_CONFLICTED"]
    elif record is None:
        state, reasons = "MISSING_METRICS", ["NO_REGISTERED_SUPPLY_METRICS_AT_AS_OF"]
    else:
        state, reasons = "RESOLVED", [
            "REGISTERED_SUPPLY_METRICS_RESOLVED",
            "UNLOCK_DOES_NOT_IMPLY_SALE",
            "NO_FORCED_SALE_OR_HOLDER_INTENT_CLAIM",
        ]
    payload = {
        "evaluated_at_utc": evaluated,
        "market": market_id,
        "observation_hash": None if observation is None else observation.observation_hash,
        "reason_codes": reasons,
        "record_hash": None if record is None else record.record_hash,
        "state": state,
        "subject_id": subject,
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return EquitySupplyPressureSnapshot(subject, market_id, evaluated, state, observation, record, tuple(reasons), True, digest)
