from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import MappingProxyType
from typing import Any


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")


def require_identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def require_text(value: object, field_name: str, maximum: int = 4000) -> str:
    normalized = str(value).strip()
    if not normalized or len(normalized) > maximum:
        raise ValueError(f"{field_name} must be non-empty bounded text")
    if any(ord(character) < 32 and character not in "\n\t" for character in normalized):
        raise ValueError(f"{field_name} contains a control character")
    return normalized


def require_utc_timestamp(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return parsed.isoformat().replace("+00:00", "Z")


def parse_utc_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def require_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return result


def normalize_identifiers(
    values: tuple[str, ...],
    field_name: str,
    *,
    required: bool = False,
) -> tuple[str, ...]:
    normalized = tuple(
        sorted({require_identifier(value, field_name) for value in values})
    )
    if required and not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): freeze_json(item)
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            }
        )
    if isinstance(value, (list, tuple)):
        return tuple(freeze_json(item) for item in value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("Decimal values must be finite")
        return value
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("float values must be finite")
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("values must be immutable JSON-compatible data")


class FactorLifecycle(str, Enum):
    DRAFT = "DRAFT"
    RESEARCH = "RESEARCH"
    CHALLENGER = "CHALLENGER"
    QUALIFIED = "QUALIFIED"
    CHAMPION = "CHAMPION"
    DEGRADED = "DEGRADED"
    RETIRED = "RETIRED"


class ValidationStatus(str, Enum):
    DRAFT = "DRAFT"
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    VALIDATED = "VALIDATED"


class ChampionChallengerStatus(str, Enum):
    UNASSIGNED = "UNASSIGNED"
    CHALLENGER = "CHALLENGER"
    CHAMPION = "CHAMPION"


class ForecastTargetType(str, Enum):
    RETURN = "RETURN"
    VOLATILITY = "VOLATILITY"
    DRAWDOWN = "DRAWDOWN"
    LIQUIDITY = "LIQUIDITY"
    ANOMALY = "ANOMALY"


class TargetBasis(str, Enum):
    ABSOLUTE = "ABSOLUTE"
    BENCHMARK_RELATIVE = "BENCHMARK_RELATIVE"


@dataclass(frozen=True)
class FactorDefinition:
    factor_id: str
    factor_name: str
    factor_family: str
    financial_hypothesis: str
    asset_class: str
    market: str
    instrument_scope: str
    research_horizon: str
    input_frequency: str
    output_frequency: str
    formula: str
    formula_version: str
    parameter_schema: Mapping[str, Any]
    parameter_version: str
    input_fields: tuple[str, ...]
    source_requirements: tuple[str, ...]
    point_in_time_required: bool
    lookback_window: str
    minimum_history: int
    normalization_method: str
    winsorization_method: str
    missing_value_policy: str
    outlier_policy: str
    neutralization_policy: str
    expected_direction: str
    valid_market_regimes: tuple[str, ...]
    invalid_market_regimes: tuple[str, ...]
    risk_flags: tuple[str, ...]
    known_failure_modes: tuple[str, ...]
    validation_status: ValidationStatus
    champion_challenger_status: ChampionChallengerStatus
    approved_by: str
    evidence_refs: tuple[str, ...]
    correlation_id: str
    effective_at_utc: str
    retired_at_utc: str | None
    owner: str
    dependency_factor_ids: tuple[str, ...]
    dependency_data_fields: tuple[str, ...]
    calculation_unit: str
    output_range: tuple[object, object]
    deterministic_test_vectors: tuple[Mapping[str, Any], ...]
    reference_implementation_version: str
    compute_cost_class: str
    revision_policy: str
    backfill_policy: str
    replacement_factor_id: str | None
    lifecycle: FactorLifecycle = FactorLifecycle.DRAFT

    def __post_init__(self) -> None:
        identifier_fields = (
            "factor_id",
            "factor_family",
            "asset_class",
            "market",
            "instrument_scope",
            "research_horizon",
            "input_frequency",
            "output_frequency",
            "formula_version",
            "parameter_version",
            "lookback_window",
            "normalization_method",
            "winsorization_method",
            "missing_value_policy",
            "outlier_policy",
            "neutralization_policy",
            "expected_direction",
            "approved_by",
            "correlation_id",
            "owner",
            "calculation_unit",
            "reference_implementation_version",
            "compute_cost_class",
            "revision_policy",
            "backfill_policy",
        )
        for field_name in identifier_fields:
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(self, "factor_name", require_text(self.factor_name, "factor_name", 200))
        object.__setattr__(
            self,
            "financial_hypothesis",
            require_text(self.financial_hypothesis, "financial_hypothesis"),
        )
        object.__setattr__(self, "formula", require_text(self.formula, "formula"))
        try:
            object.__setattr__(self, "lifecycle", FactorLifecycle(self.lifecycle))
            object.__setattr__(
                self, "validation_status", ValidationStatus(self.validation_status)
            )
            object.__setattr__(
                self,
                "champion_challenger_status",
                ChampionChallengerStatus(self.champion_challenger_status),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("factor status value is invalid") from exc
        if self.point_in_time_required is not True:
            raise ValueError("point_in_time_required must be true")
        if isinstance(self.minimum_history, bool) or self.minimum_history <= 0:
            raise ValueError("minimum_history must be positive")
        for field_name, required in (
            ("input_fields", True),
            ("source_requirements", True),
            ("valid_market_regimes", True),
            ("invalid_market_regimes", False),
            ("risk_flags", False),
            ("known_failure_modes", True),
            ("evidence_refs", True),
            ("dependency_factor_ids", False),
            ("dependency_data_fields", True),
        ):
            object.__setattr__(
                self,
                field_name,
                normalize_identifiers(
                    getattr(self, field_name), field_name, required=required
                ),
            )
        if set(self.valid_market_regimes) & set(self.invalid_market_regimes):
            raise ValueError("valid and invalid market regimes must be disjoint")
        if self.factor_id in self.dependency_factor_ids:
            raise ValueError("factor cannot depend on itself")
        effective = require_utc_timestamp(self.effective_at_utc, "effective_at_utc")
        object.__setattr__(self, "effective_at_utc", effective)
        if self.retired_at_utc is not None:
            retired = require_utc_timestamp(self.retired_at_utc, "retired_at_utc")
            if parse_utc_timestamp(retired) < parse_utc_timestamp(effective):
                raise ValueError("retired_at_utc cannot precede effective_at_utc")
            object.__setattr__(self, "retired_at_utc", retired)
        if self.lifecycle is FactorLifecycle.RETIRED and self.retired_at_utc is None:
            raise ValueError("retired factor requires retired_at_utc")
        if self.lifecycle is not FactorLifecycle.RETIRED and self.retired_at_utc is not None:
            raise ValueError("non-retired factor cannot have retired_at_utc")
        if self.replacement_factor_id is not None:
            replacement = require_identifier(
                self.replacement_factor_id, "replacement_factor_id"
            )
            if replacement == self.factor_id:
                raise ValueError("replacement_factor_id cannot equal factor_id")
            object.__setattr__(self, "replacement_factor_id", replacement)
        if self.lifecycle is FactorLifecycle.CHAMPION and (
            self.champion_challenger_status is not ChampionChallengerStatus.CHAMPION
        ):
            raise ValueError("Champion lifecycle requires Champion status")
        if self.champion_challenger_status is ChampionChallengerStatus.CHAMPION and (
            self.lifecycle is not FactorLifecycle.CHAMPION
        ):
            raise ValueError("Champion status requires Champion lifecycle")
        if self.lifecycle in (FactorLifecycle.QUALIFIED, FactorLifecycle.CHAMPION) and (
            self.approved_by == "NONE"
            or self.validation_status is not ValidationStatus.VALIDATED
        ):
            raise ValueError("qualified factor requires approval and validation")
        if not isinstance(self.parameter_schema, Mapping) or not self.parameter_schema:
            raise ValueError("parameter_schema must be a non-empty mapping")
        object.__setattr__(self, "parameter_schema", freeze_json(self.parameter_schema))
        if len(self.output_range) != 2:
            raise ValueError("output_range requires lower and upper bounds")
        lower = require_decimal(self.output_range[0], "output_range_lower")
        upper = require_decimal(self.output_range[1], "output_range_upper")
        if lower >= upper:
            raise ValueError("output_range lower must be less than upper")
        object.__setattr__(self, "output_range", (lower, upper))
        vectors = tuple(self.deterministic_test_vectors)
        if not vectors or not all(isinstance(item, Mapping) for item in vectors):
            raise ValueError("deterministic_test_vectors must contain mappings")
        object.__setattr__(
            self,
            "deterministic_test_vectors",
            tuple(freeze_json(item) for item in vectors),
        )


@dataclass(frozen=True)
class ForecastTargetDefinition:
    target_id: str
    target_version: str
    asset_class: str
    market: str
    instrument_scope: str
    decision_time_basis: str
    forecast_horizon: str
    maturity_rule: str
    target_type: ForecastTargetType
    formula: str
    basis: TargetBasis
    objective: str
    cost_treatment: str
    slippage_treatment: str
    capacity_treatment: str
    label_availability_rule: str
    benchmark_policy: str
    neutralization_policy: str
    missing_behavior: str
    invalid_behavior: str
    censored_behavior: str
    abstention_behavior: str
    evaluation_metrics: tuple[str, ...]
    minimum_sample: int
    evidence_refs: tuple[str, ...]
    owner: str
    effective_at_utc: str

    def __post_init__(self) -> None:
        identifier_fields = (
            "target_id",
            "target_version",
            "asset_class",
            "market",
            "instrument_scope",
            "decision_time_basis",
            "forecast_horizon",
            "maturity_rule",
            "objective",
            "cost_treatment",
            "slippage_treatment",
            "capacity_treatment",
            "label_availability_rule",
            "benchmark_policy",
            "neutralization_policy",
            "missing_behavior",
            "invalid_behavior",
            "censored_behavior",
            "abstention_behavior",
            "owner",
        )
        for field_name in identifier_fields:
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        try:
            object.__setattr__(self, "target_type", ForecastTargetType(self.target_type))
            object.__setattr__(self, "basis", TargetBasis(self.basis))
        except (TypeError, ValueError) as exc:
            raise ValueError("forecast target enum value is invalid") from exc
        object.__setattr__(self, "formula", require_text(self.formula, "formula"))
        object.__setattr__(
            self,
            "evaluation_metrics",
            normalize_identifiers(
                self.evaluation_metrics, "evaluation_metrics", required=True
            ),
        )
        object.__setattr__(
            self,
            "evidence_refs",
            normalize_identifiers(self.evidence_refs, "evidence_refs", required=True),
        )
        if isinstance(self.minimum_sample, bool) or self.minimum_sample <= 0:
            raise ValueError("minimum_sample must be positive")
        object.__setattr__(
            self,
            "effective_at_utc",
            require_utc_timestamp(self.effective_at_utc, "effective_at_utc"),
        )
