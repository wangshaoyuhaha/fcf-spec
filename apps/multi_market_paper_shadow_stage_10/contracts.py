from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import MappingProxyType
from typing import Any

from apps.multi_market_adapters_stage_6 import AdapterStatus, MarketAdapterId


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,127}$")


def identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


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


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): freeze(item) for key, item in sorted(value.items())}
        )
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if isinstance(value, Decimal):
        return value
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("Stage 10 values must be immutable JSON-compatible values")


class ValidationStatus(str, Enum):
    PASS_REVIEW_REQUIRED = "PASS_REVIEW_REQUIRED"
    DEGRADED_REVIEW_REQUIRED = "DEGRADED_REVIEW_REQUIRED"
    BLOCKED_REVIEW_REQUIRED = "BLOCKED_REVIEW_REQUIRED"


class ShadowMaturity(str, Enum):
    PENDING = "PENDING"
    MATURE = "MATURE"


@dataclass(frozen=True)
class PaperMarketValidation:
    adapter_id: MarketAdapterId
    adapter_status: AdapterStatus
    window_id: str
    start_time_utc: str
    end_time_utc: str
    paper_notional: Decimal
    candidate_return: Decimal
    benchmark_return: Decimal
    maximum_loss_fraction: Decimal
    turnover: Decimal
    transaction_cost: Decimal
    exposure_breach_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    currency_context_id: str
    calendar_id: str
    data_quality_state: str = "PASS"
    freshness_state: str = "CURRENT"

    def __post_init__(self) -> None:
        object.__setattr__(self, "adapter_id", MarketAdapterId(self.adapter_id))
        object.__setattr__(self, "adapter_status", AdapterStatus(self.adapter_status))
        for field_name in ("window_id", "currency_context_id", "calendar_id"):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        start = utc_time(self.start_time_utc, "start_time_utc")
        end = utc_time(self.end_time_utc, "end_time_utc")
        if end <= start:
            raise ValueError("Paper validation window must have positive duration")
        for field_name in (
            "paper_notional",
            "candidate_return",
            "benchmark_return",
            "maximum_loss_fraction",
            "turnover",
            "transaction_cost",
        ):
            object.__setattr__(
                self,
                field_name,
                decimal_value(getattr(self, field_name), field_name),
            )
        if self.paper_notional <= 0 or self.transaction_cost < 0:
            raise ValueError("Paper notional and cost inputs are invalid")
        if not Decimal("0") <= self.maximum_loss_fraction <= Decimal("1"):
            raise ValueError("maximum_loss_fraction must be between 0 and 1")
        if not Decimal("0") <= self.turnover <= Decimal("1"):
            raise ValueError("turnover must be between 0 and 1")
        breaches = tuple(
            sorted({identifier(item, "exposure_breach_code") for item in self.exposure_breach_codes})
        )
        evidence = tuple(
            sorted({identifier(item, "evidence_id") for item in self.evidence_ids})
        )
        if not evidence:
            raise ValueError("Paper validation evidence_ids are required")
        object.__setattr__(self, "exposure_breach_codes", breaches)
        object.__setattr__(self, "evidence_ids", evidence)
        if self.data_quality_state not in {"PASS", "DEGRADED", "BLOCKED"}:
            raise ValueError("unsupported data_quality_state")
        if self.freshness_state not in {"CURRENT", "STALE", "UNKNOWN"}:
            raise ValueError("unsupported freshness_state")


@dataclass(frozen=True)
class ShadowMarketObservation:
    adapter_id: MarketAdapterId
    decision_time_utc: str
    observation_time_utc: str
    maturity: ShadowMaturity
    expected_return: Decimal
    observed_return: Decimal | None
    evidence_ids: tuple[str, ...]
    observation_artifact_id: str
    no_execution_observed: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "adapter_id", MarketAdapterId(self.adapter_id))
        decision = utc_time(self.decision_time_utc, "decision_time_utc")
        observation = utc_time(self.observation_time_utc, "observation_time_utc")
        if observation < decision:
            raise ValueError("Shadow observation cannot precede its decision")
        maturity = (
            self.maturity
            if isinstance(self.maturity, ShadowMaturity)
            else ShadowMaturity(self.maturity)
        )
        object.__setattr__(self, "maturity", maturity)
        object.__setattr__(
            self,
            "expected_return",
            decimal_value(self.expected_return, "expected_return"),
        )
        if maturity is ShadowMaturity.MATURE:
            if self.observed_return is None or observation == decision:
                raise ValueError("mature Shadow observation requires a later result")
            object.__setattr__(
                self,
                "observed_return",
                decimal_value(self.observed_return, "observed_return"),
            )
        elif self.observed_return is not None:
            raise ValueError("pending Shadow observation cannot include a result")
        evidence = tuple(
            sorted({identifier(item, "evidence_id") for item in self.evidence_ids})
        )
        if not evidence:
            raise ValueError("Shadow evidence_ids are required")
        object.__setattr__(self, "evidence_ids", evidence)
        object.__setattr__(
            self,
            "observation_artifact_id",
            identifier(self.observation_artifact_id, "observation_artifact_id"),
        )
        if self.no_execution_observed is not True:
            raise ValueError("Shadow observation must contain no execution")


@dataclass(frozen=True)
class MultiMarketValidationRequest:
    request_id: str
    correlation_id: str
    portfolio_artifact_id: str
    benchmark_artifact_id: str
    policy_version: str
    operator_trigger_id: str
    paper_markets: tuple[PaperMarketValidation, ...]
    shadow_markets: tuple[ShadowMarketObservation, ...]
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "request_id",
            "correlation_id",
            "portfolio_artifact_id",
            "benchmark_artifact_id",
            "policy_version",
            "operator_trigger_id",
        ):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(self, "paper_markets", tuple(self.paper_markets))
        object.__setattr__(self, "shadow_markets", tuple(self.shadow_markets))
        paper_ids = tuple(item.adapter_id for item in self.paper_markets)
        shadow_ids = tuple(item.adapter_id for item in self.shadow_markets)
        if len(set(paper_ids)) != len(paper_ids):
            raise ValueError("Paper market adapter ids must be unique")
        if len(set(shadow_ids)) != len(shadow_ids):
            raise ValueError("Shadow market adapter ids must be unique")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")


@dataclass(frozen=True)
class MarketValidationFinding:
    adapter_id: MarketAdapterId
    status: ValidationStatus
    paper_excess_return: Decimal | None
    shadow_error: Decimal | None
    reason_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class MultiMarketValidationOutcome:
    request: MultiMarketValidationRequest
    status: ValidationStatus
    findings: tuple[MarketValidationFinding, ...]
    paper_market_coverage: Decimal
    shadow_market_coverage: Decimal
    mature_shadow_coverage: Decimal
    aggregate_paper_excess_return: Decimal
    aggregate_shadow_error: Decimal | None
    disagreement_visible: bool
    reason_codes: tuple[str, ...]
    operator_review_packet: Mapping[str, Any]
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_learning_allowed: bool = False
    real_execution_used: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ValidationStatus(self.status))
        object.__setattr__(self, "findings", tuple(self.findings))
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))
        object.__setattr__(
            self,
            "operator_review_packet",
            freeze(self.operator_review_packet),
        )
        prohibited = (
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_learning_allowed,
            self.real_execution_used,
        )
        if any(prohibited):
            raise ValueError("validation outcome cannot transition authority")
