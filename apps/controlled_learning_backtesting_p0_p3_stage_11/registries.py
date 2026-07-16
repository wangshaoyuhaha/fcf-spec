from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from typing import Any, Generic, Mapping, TypeVar

from .contracts import (
    BacktestResult,
    ConfigSnapshot,
    decimal_value,
    digest,
    freeze,
    identifier,
    utc_time,
)


@dataclass(frozen=True)
class DataSourceVersionLock:
    source_id: str
    source_version: str
    content_sha256: str
    locked_at_utc: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(self, "source_version", identifier(self.source_version, "source_version"))
        object.__setattr__(self, "content_sha256", digest(self.content_sha256, "content_sha256"))
        utc_time(self.locked_at_utc, "locked_at_utc")


@dataclass(frozen=True)
class MarketCalendarRecord:
    calendar_id: str
    version: str
    effective_at_utc: str
    session_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "calendar_id", identifier(self.calendar_id, "calendar_id"))
        object.__setattr__(self, "version", identifier(self.version, "version"))
        utc_time(self.effective_at_utc, "effective_at_utc")
        sessions = tuple(sorted({identifier(item, "session_id") for item in self.session_ids}))
        if not sessions:
            raise ValueError("market calendar sessions are required")
        object.__setattr__(self, "session_ids", sessions)


@dataclass(frozen=True)
class CorporateActionRecord:
    action_id: str
    security_id: str
    announced_at_utc: str
    effective_at_utc: str
    action_type: str

    def __post_init__(self) -> None:
        for name in ("action_id", "security_id", "action_type"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        announced = utc_time(self.announced_at_utc, "announced_at_utc")
        effective = utc_time(self.effective_at_utc, "effective_at_utc")
        if announced > effective:
            raise ValueError("corporate action announcement cannot follow effective time")


@dataclass(frozen=True)
class BenchmarkRecord:
    benchmark_id: str
    version: str
    available_at_utc: str
    constituent_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "benchmark_id", identifier(self.benchmark_id, "benchmark_id"))
        object.__setattr__(self, "version", identifier(self.version, "version"))
        utc_time(self.available_at_utc, "available_at_utc")
        constituents = tuple(sorted({identifier(item, "constituent_id") for item in self.constituent_ids}))
        if not constituents:
            raise ValueError("benchmark constituents are required")
        object.__setattr__(self, "constituent_ids", constituents)


@dataclass(frozen=True)
class OutcomeLabelRecord:
    outcome_id: str
    observation_id: str
    observation_time_utc: str
    original_prediction: Decimal
    actual_outcome: Decimal
    source_evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("outcome_id", "observation_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        utc_time(self.observation_time_utc, "observation_time_utc")
        for name in ("original_prediction", "actual_outcome"):
            value = decimal_value(getattr(self, name), name)
            if not Decimal("0") <= value <= Decimal("1"):
                raise ValueError(f"{name} must be between 0 and 1")
            object.__setattr__(self, name, value)
        evidence = tuple(sorted({identifier(item, "source_evidence_id") for item in self.source_evidence_ids}))
        if not evidence:
            raise ValueError("outcome evidence is required")
        object.__setattr__(self, "source_evidence_ids", evidence)


@dataclass(frozen=True)
class AttributionRecord:
    attribution_id: str
    result_id: str
    values: Mapping[str, Decimal]
    source_evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("attribution_id", "result_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        values = {
            identifier(key, "factor_id"): decimal_value(value, "attribution")
            for key, value in self.values.items()
        }
        if not values:
            raise ValueError("attribution values are required")
        object.__setattr__(self, "values", freeze(values))
        evidence = tuple(
            sorted(
                {
                    identifier(item, "source_evidence_id")
                    for item in self.source_evidence_ids
                }
            )
        )
        if not evidence:
            raise ValueError("attribution evidence is required")
        object.__setattr__(self, "source_evidence_ids", evidence)


T = TypeVar("T")


@dataclass(frozen=True)
class AppendOnlyRegistry(Generic[T]):
    records: tuple[T, ...] = ()

    def append(self, record: T, identity_field: str) -> "AppendOnlyRegistry[T]":
        identity = identifier(getattr(record, identity_field), identity_field)
        if any(getattr(item, identity_field) == identity for item in self.records):
            raise ValueError("registered record cannot be overwritten")
        return AppendOnlyRegistry(self.records + (record,))


def _append_unique(records: tuple[T, ...], record: T, identity_field: str) -> tuple[T, ...]:
    identity = identifier(getattr(record, identity_field), identity_field)
    if any(getattr(item, identity_field) == identity for item in records):
        raise ValueError("registered record cannot be overwritten")
    return records + (record,)


@dataclass(frozen=True)
class DataSourceVersionRegistry:
    records: tuple[DataSourceVersionLock, ...] = ()

    def append(self, record: DataSourceVersionLock) -> "DataSourceVersionRegistry":
        return DataSourceVersionRegistry(_append_unique(self.records, record, "source_id"))


@dataclass(frozen=True)
class MarketCalendarRegistry:
    records: tuple[MarketCalendarRecord, ...] = ()

    def append(self, record: MarketCalendarRecord) -> "MarketCalendarRegistry":
        return MarketCalendarRegistry(_append_unique(self.records, record, "calendar_id"))


@dataclass(frozen=True)
class CorporateActionRegistry:
    records: tuple[CorporateActionRecord, ...] = ()

    def append(self, record: CorporateActionRecord) -> "CorporateActionRegistry":
        return CorporateActionRegistry(_append_unique(self.records, record, "action_id"))


@dataclass(frozen=True)
class ConfigSnapshotRegistry:
    records: tuple[ConfigSnapshot, ...] = ()

    def append(self, record: ConfigSnapshot) -> "ConfigSnapshotRegistry":
        return ConfigSnapshotRegistry(_append_unique(self.records, record, "config_snapshot_id"))


@dataclass(frozen=True)
class BenchmarkRegistry:
    records: tuple[BenchmarkRecord, ...] = ()

    def append(self, record: BenchmarkRecord) -> "BenchmarkRegistry":
        return BenchmarkRegistry(_append_unique(self.records, record, "benchmark_id"))


@dataclass(frozen=True)
class OutcomeLabelRegistry:
    records: tuple[OutcomeLabelRecord, ...] = ()

    def append(self, record: OutcomeLabelRecord) -> "OutcomeLabelRegistry":
        return OutcomeLabelRegistry(_append_unique(self.records, record, "outcome_id"))


@dataclass(frozen=True)
class AttributionRegistry:
    records: tuple[AttributionRecord, ...] = ()

    def append(self, record: AttributionRecord) -> "AttributionRegistry":
        return AttributionRegistry(_append_unique(self.records, record, "attribution_id"))


def _derived_id(prefix: str, *parts: str) -> str:
    value = "\x00".join(parts).encode("ascii")
    return f"{prefix}-{sha256(value).hexdigest()}"


def build_outcome_label_registry(result: BacktestResult) -> OutcomeLabelRegistry:
    registry = OutcomeLabelRegistry()
    for label in result.outcome_labels:
        observation_id = identifier(label["observation_id"], "observation_id")
        registry = registry.append(
            OutcomeLabelRecord(
                outcome_id=_derived_id("outcome", result.result_id, observation_id),
                observation_id=observation_id,
                observation_time_utc=str(label["observation_time_utc"]),
                original_prediction=decimal_value(
                    label["original_prediction"],
                    "original_prediction",
                ),
                actual_outcome=decimal_value(
                    label["actual_outcome"],
                    "actual_outcome",
                ),
                source_evidence_ids=result.source_evidence_ids,
            )
        )
    return registry


def build_attribution_registry(result: BacktestResult) -> AttributionRegistry:
    if not result.factor_attribution:
        raise ValueError("backtest result attribution is required")
    return AttributionRegistry().append(
        AttributionRecord(
            attribution_id=_derived_id("attribution", result.result_id),
            result_id=result.result_id,
            values=result.factor_attribution,
            source_evidence_ids=result.source_evidence_ids,
        )
    )
