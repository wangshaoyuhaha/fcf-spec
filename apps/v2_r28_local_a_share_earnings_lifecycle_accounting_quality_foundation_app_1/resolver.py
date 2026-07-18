from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from .contracts import AccountingQualityChallengeRecord, RegisteredAccountingObservation, RegisteredEarningsLifecycleStage
from .registry import LocalEarningsAccountingQualityRegistry


@dataclass(frozen=True)
class EarningsAccountingQualitySnapshot:
    subject_id: str
    market: str
    horizon: str
    evaluated_at_utc: str
    state: str
    stage: RegisteredEarningsLifecycleStage | None
    observation: RegisteredAccountingObservation | None
    challenge: AccountingQualityChallengeRecord | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"MISSING_STAGE", "IMMATURE", "MISSING_ACCOUNTING", "STALE", "CONFLICT", "MISSING_CHALLENGE", "RESOLVED"}:
            raise ValueError("invalid earnings accounting snapshot state")
        if self.operator_review_required is not True:
            raise ValueError("earnings accounting snapshot requires Operator review")


def resolve_earnings_accounting_quality(registry: LocalEarningsAccountingQualityRegistry, *, subject_id: str, market: str, horizon: str, as_of_utc: str) -> EarningsAccountingQualitySnapshot:
    subject, market_id, horizon_id = identifier(subject_id, "subject_id"), identifier(market, "market"), identifier(horizon, "horizon")
    evaluated, as_of = utc(as_of_utc, "as_of_utc"), instant(utc(as_of_utc, "as_of_utc"))
    stages = tuple(sorted((item for item in registry.stages if (item.subject_id, item.market, item.horizon) == (subject, market_id, horizon_id) and instant(item.available_at_utc) <= as_of), key=lambda item: (item.effective_from_utc, item.stage_id)))
    stage = stages[-1] if stages else None
    observation = next((item for item in reversed(registry.observations) if stage is not None and item.stage.stage_hash == stage.stage_hash and instant(item.available_at_utc) <= as_of), None)
    challenge = next((item for item in reversed(registry.challenges) if observation is not None and item.observation.observation_hash == observation.observation_hash and instant(item.available_at_utc) <= as_of), None)
    if stage is None:
        state, reasons = "MISSING_STAGE", ["NO_REGISTERED_EARNINGS_STAGE_AT_AS_OF"]
    elif as_of < instant(stage.matures_at_utc):
        state, reasons = "IMMATURE", ["EARNINGS_STAGE_NOT_MATURE_AT_AS_OF"]
    elif observation is None or observation.accounting_state == "MISSING":
        state, reasons = "MISSING_ACCOUNTING", ["NO_REGISTERED_ACCOUNTING_EVIDENCE_AT_AS_OF"]
    elif observation.accounting_state == "STALE":
        state, reasons = "STALE", ["REGISTERED_ACCOUNTING_EVIDENCE_IS_STALE"]
    elif observation.accounting_state == "CONFLICT":
        state, reasons = "CONFLICT", ["REGISTERED_ACCOUNTING_EVIDENCE_IS_CONFLICTED"]
    elif challenge is None:
        state, reasons = "MISSING_CHALLENGE", ["NO_MATURED_ACCOUNTING_CHALLENGE_AT_AS_OF"]
    else:
        state, reasons = "RESOLVED", ["REGISTERED_ACCOUNTING_CHALLENGE_RESOLVED", "NO_FRAUD_CONCLUSION"]
    payload = {"challenge_hash": None if challenge is None else challenge.challenge_hash, "evaluated_at_utc": evaluated, "horizon": horizon_id, "market": market_id, "observation_hash": None if observation is None else observation.observation_hash, "reason_codes": reasons, "stage_hash": None if stage is None else stage.stage_hash, "state": state, "subject_id": subject}
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return EarningsAccountingQualitySnapshot(subject, market_id, horizon_id, evaluated, state, stage, observation, challenge, tuple(reasons), True, digest)
