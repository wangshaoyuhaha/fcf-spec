from __future__ import annotations

import re
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import MappingProxyType
from typing import Any

from apps.multi_market_adapters_stage_6 import MarketAdapterId


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def utc_time(value: object, field_name: str) -> datetime:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return parsed


def decimal_value(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return result


def digest(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be SHA-256")
    return normalized


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): freeze(item) for key, item in sorted(value.items())}
        )
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("P0-P3 float values must be finite")
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("P0-P3 values must be immutable JSON-compatible values")


class DatasetSplit(str, Enum):
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    FINAL_TEST = "FINAL_TEST"


class BacktestStatus(str, Enum):
    PASS_REVIEW_REQUIRED = "PASS_REVIEW_REQUIRED"
    DEGRADED_REVIEW_REQUIRED = "DEGRADED_REVIEW_REQUIRED"
    BLOCKED_REVIEW_REQUIRED = "BLOCKED_REVIEW_REQUIRED"


class AIReplayMode(str, Enum):
    HISTORICAL_REPRODUCTION = "HISTORICAL_REPRODUCTION"
    COUNTERFACTUAL_CURRENT_MODEL_EVALUATION = (
        "COUNTERFACTUAL_CURRENT_MODEL_EVALUATION"
    )


@dataclass(frozen=True)
class PointInTimeEvidence:
    evidence_id: str
    source_version: str
    event_time_utc: str
    published_at_utc: str
    available_at_utc: str
    ingested_at_utc: str
    as_of_time_utc: str
    retrieval_time_utc: str
    content_sha256: str
    license_id: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field_name in ("evidence_id", "source_version", "license_id"):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        event = utc_time(self.event_time_utc, "event_time_utc")
        published = utc_time(self.published_at_utc, "published_at_utc")
        available = utc_time(self.available_at_utc, "available_at_utc")
        ingested = utc_time(self.ingested_at_utc, "ingested_at_utc")
        as_of = utc_time(self.as_of_time_utc, "as_of_time_utc")
        retrieval = utc_time(self.retrieval_time_utc, "retrieval_time_utc")
        if event > published or published > available:
            raise ValueError("event, publication, and availability order is invalid")
        if available > as_of:
            raise ValueError("available_at must be <= as_of_time")
        if ingested < available or retrieval < available:
            raise ValueError("ingestion and retrieval cannot precede availability")
        object.__setattr__(
            self,
            "content_sha256",
            digest(self.content_sha256, "content_sha256"),
        )
        object.__setattr__(self, "payload", freeze(self.payload))


@dataclass(frozen=True)
class ConfigSnapshot:
    config_snapshot_id: str
    code_commit: str
    deterministic_engine_version: str
    strategy_version: str
    factor_version: str
    portfolio_policy_version: str
    market_adapter_version: str
    universe_version: str
    market_calendar_version: str
    corporate_action_version: str
    benchmark_version: str
    policy_version: str
    output_schema_version: str
    data_source_versions: Mapping[str, str]
    dataset_digests: Mapping[str, str]
    factor_weights: Mapping[str, Decimal]
    assumptions: Mapping[str, Any]
    model_role_assignments: Mapping[str, str]
    prompt_versions: Mapping[str, str]
    random_seed: int
    experiment_variables: Mapping[str, Any]

    def __post_init__(self) -> None:
        scalar_ids = (
            "config_snapshot_id",
            "code_commit",
            "deterministic_engine_version",
            "strategy_version",
            "factor_version",
            "portfolio_policy_version",
            "market_adapter_version",
            "universe_version",
            "market_calendar_version",
            "corporate_action_version",
            "benchmark_version",
            "policy_version",
            "output_schema_version",
        )
        for field_name in scalar_ids:
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        if isinstance(self.random_seed, bool) or self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")
        datasets = {
            identifier(key, "dataset_id"): digest(value, "dataset_digest")
            for key, value in self.dataset_digests.items()
        }
        weights = {
            identifier(key, "factor_id"): decimal_value(value, "factor_weight")
            for key, value in self.factor_weights.items()
        }
        object.__setattr__(self, "data_source_versions", freeze(self.data_source_versions))
        object.__setattr__(self, "dataset_digests", freeze(datasets))
        object.__setattr__(self, "factor_weights", freeze(weights))
        object.__setattr__(self, "assumptions", freeze(self.assumptions))
        object.__setattr__(self, "model_role_assignments", freeze(self.model_role_assignments))
        object.__setattr__(self, "prompt_versions", freeze(self.prompt_versions))
        object.__setattr__(self, "experiment_variables", freeze(self.experiment_variables))


@dataclass(frozen=True)
class BacktestObservation:
    observation_id: str
    adapter_id: MarketAdapterId
    split: DatasetSplit
    decision_as_of_utc: str
    feature_available_at_utc: str
    outcome_time_utc: str
    predicted_score: Decimal
    actual_outcome: Decimal
    gross_return: Decimal
    transaction_cost: Decimal
    slippage_cost: Decimal
    capacity_passed: bool
    regime_id: str
    factor_attribution: Mapping[str, Decimal]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "observation_id",
            identifier(self.observation_id, "observation_id"),
        )
        object.__setattr__(self, "adapter_id", MarketAdapterId(self.adapter_id))
        object.__setattr__(self, "split", DatasetSplit(self.split))
        decision = utc_time(self.decision_as_of_utc, "decision_as_of_utc")
        available = utc_time(
            self.feature_available_at_utc,
            "feature_available_at_utc",
        )
        outcome = utc_time(self.outcome_time_utc, "outcome_time_utc")
        if available > decision:
            raise ValueError("feature availability exceeds decision as_of_time")
        if outcome <= decision:
            raise ValueError("outcome must occur after the decision")
        for field_name in (
            "predicted_score",
            "actual_outcome",
            "gross_return",
            "transaction_cost",
            "slippage_cost",
        ):
            object.__setattr__(
                self,
                field_name,
                decimal_value(getattr(self, field_name), field_name),
            )
        if not Decimal("0") <= self.predicted_score <= Decimal("1"):
            raise ValueError("predicted_score must be between 0 and 1")
        if not Decimal("0") <= self.actual_outcome <= Decimal("1"):
            raise ValueError("actual_outcome must be between 0 and 1")
        if self.transaction_cost < 0 or self.slippage_cost < 0:
            raise ValueError("costs must be non-negative")
        object.__setattr__(self, "regime_id", identifier(self.regime_id, "regime_id"))
        object.__setattr__(
            self,
            "factor_attribution",
            freeze(
                {
                    identifier(key, "factor_id"): decimal_value(value, "attribution")
                    for key, value in self.factor_attribution.items()
                }
            ),
        )
        evidence = tuple(
            sorted({identifier(item, "evidence_id") for item in self.evidence_ids})
        )
        if not evidence:
            raise ValueError("observation evidence_ids are required")
        object.__setattr__(self, "evidence_ids", evidence)


@dataclass(frozen=True)
class UnifiedBacktestRequest:
    request_id: str
    correlation_id: str
    operator_trigger_id: str
    config: ConfigSnapshot
    evidence: tuple[PointInTimeEvidence, ...]
    observations: tuple[BacktestObservation, ...]
    embargo_days: int
    purged_validation: bool

    def __post_init__(self) -> None:
        for field_name in ("request_id", "correlation_id", "operator_trigger_id"):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "observations", tuple(self.observations))
        if not self.evidence or not self.observations:
            raise ValueError("backtest requires evidence and observations")
        if self.embargo_days < 0:
            raise ValueError("embargo_days must be non-negative")
        evidence_ids = tuple(item.evidence_id for item in self.evidence)
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("backtest evidence ids must be unique")
        evidence_by_id = {item.evidence_id: item for item in self.evidence}
        for observation in self.observations:
            unknown = set(observation.evidence_ids) - set(evidence_by_id)
            if unknown:
                raise ValueError("observation references unregistered evidence")
            decision = utc_time(observation.decision_as_of_utc, "decision_as_of_utc")
            declared = utc_time(
                observation.feature_available_at_utc,
                "feature_available_at_utc",
            )
            for evidence_id in observation.evidence_ids:
                evidence_as_of = utc_time(
                    evidence_by_id[evidence_id].as_of_time_utc,
                    "as_of_time_utc",
                )
                available = utc_time(
                    evidence_by_id[evidence_id].available_at_utc,
                    "available_at_utc",
                )
                if evidence_as_of > decision:
                    raise ValueError(
                        "observation contains future evidence as_of_time"
                    )
                if available > decision:
                    raise ValueError("observation contains future evidence")
                if declared < available:
                    raise ValueError("feature availability predates evidence availability")


@dataclass(frozen=True)
class BacktestResult:
    result_id: str
    request_id: str
    correlation_id: str
    config_snapshot_id: str
    status: BacktestStatus
    metrics: Mapping[str, Any]
    regime_metrics: Mapping[str, Any]
    factor_attribution: Mapping[str, Decimal]
    failure_codes: tuple[str, ...]
    outcome_labels: tuple[Mapping[str, Any], ...]
    source_evidence_ids: tuple[str, ...]
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "result_id",
            "request_id",
            "correlation_id",
            "config_snapshot_id",
        ):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(self, "status", BacktestStatus(self.status))
        object.__setattr__(self, "metrics", freeze(self.metrics))
        object.__setattr__(self, "regime_metrics", freeze(self.regime_metrics))
        object.__setattr__(self, "factor_attribution", freeze(self.factor_attribution))
        object.__setattr__(self, "failure_codes", tuple(sorted(set(self.failure_codes))))
        object.__setattr__(
            self,
            "outcome_labels",
            tuple(freeze(item) for item in self.outcome_labels),
        )
        object.__setattr__(
            self,
            "source_evidence_ids",
            tuple(sorted(set(self.source_evidence_ids))),
        )
        if not self.operator_review_required or self.automatic_activation_allowed:
            raise ValueError("backtest result authority boundary failed")


@dataclass(frozen=True)
class BacktestResultRegistry:
    results: tuple[BacktestResult, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "results", tuple(self.results))
        ids = tuple(item.result_id for item in self.results)
        if len(set(ids)) != len(ids):
            raise ValueError("backtest result ids must be unique")

    def append(self, result: BacktestResult) -> "BacktestResultRegistry":
        if any(item.result_id == result.result_id for item in self.results):
            raise ValueError("registered backtest result cannot be overwritten")
        return BacktestResultRegistry(self.results + (result,))
