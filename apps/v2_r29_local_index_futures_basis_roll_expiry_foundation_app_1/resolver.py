from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import IndexFuturesBasisRollRecord, RegisteredFuturesCurveObservation
from .registry import LocalIndexFuturesBasisRollExpiryRegistry


@dataclass(frozen=True)
class IndexFuturesBasisRollExpirySnapshot:
    contract_family: str
    market: str
    evaluated_at_utc: str
    state: str
    observation: RegisteredFuturesCurveObservation | None
    record: IndexFuturesBasisRollRecord | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {
            "MISSING_OBSERVATION",
            "MISSING",
            "STALE",
            "CONFLICT",
            "MISSING_METRICS",
            "RESOLVED",
        }:
            raise ValueError("invalid index-futures snapshot state")
        if self.operator_review_required is not True:
            raise ValueError("index-futures snapshot requires Operator review")


def resolve_index_futures_basis_roll_expiry(
    registry: LocalIndexFuturesBasisRollExpiryRegistry,
    *,
    contract_family: str,
    market: str,
    as_of_utc: str,
) -> IndexFuturesBasisRollExpirySnapshot:
    family = identifier(contract_family, "contract_family")
    market_id = identifier(market, "market")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    observations = tuple(
        sorted(
            (
                item
                for item in registry.observations
                if item.front_contract.contract_family == family
                and item.front_contract.market == market_id
                and instant(item.available_at_utc) <= as_of
            ),
            key=lambda item: (item.observed_at_utc, item.observation_id),
        )
    )
    observation = observations[-1] if observations else None
    record = next(
        (
            item
            for item in reversed(registry.records)
            if observation is not None
            and item.observation.observation_hash == observation.observation_hash
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    if observation is None:
        state, reasons = "MISSING_OBSERVATION", ["NO_REGISTERED_CURVE_OBSERVATION_AT_AS_OF"]
    elif observation.observation_state == "MISSING":
        state, reasons = "MISSING", ["REGISTERED_CURVE_EVIDENCE_IS_MISSING"]
    elif observation.observation_state == "STALE":
        state, reasons = "STALE", ["REGISTERED_CURVE_EVIDENCE_IS_STALE"]
    elif observation.observation_state == "CONFLICT":
        state, reasons = "CONFLICT", ["REGISTERED_CURVE_EVIDENCE_IS_CONFLICTED"]
    elif record is None:
        state, reasons = "MISSING_METRICS", ["NO_REGISTERED_BASIS_ROLL_METRICS_AT_AS_OF"]
    else:
        state, reasons = "RESOLVED", [
            "REGISTERED_BASIS_ROLL_METRICS_RESOLVED",
            "NO_BOTTOM_CLAIM",
            "NO_PARTICIPANT_INTENT_CLAIM",
        ]
    payload = {
        "contract_family": family,
        "evaluated_at_utc": evaluated,
        "market": market_id,
        "observation_hash": None if observation is None else observation.observation_hash,
        "reason_codes": reasons,
        "record_hash": None if record is None else record.record_hash,
        "state": state,
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return IndexFuturesBasisRollExpirySnapshot(
        family,
        market_id,
        evaluated,
        state,
        observation,
        record,
        tuple(reasons),
        True,
        digest,
    )
