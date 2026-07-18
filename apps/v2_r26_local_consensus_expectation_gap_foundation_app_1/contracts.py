from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1.contracts import (
    sha256_text,
)


SOURCE_KINDS = ("LICENSED", "OFFICIAL")
CONSENSUS_STATES = ("AVAILABLE", "MISSING", "NOT_APPLICABLE", "SOURCE_FAILURE")
FRESHNESS_STATES = ("FRESH", "STALE", "UNKNOWN")
MAX_ABSOLUTE_VALUE = Decimal("1E30")


def _hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def decimal_value(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite decimal")
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a finite decimal") from exc
    if not normalized.is_finite() or abs(normalized) > MAX_ABSOLUTE_VALUE:
        raise ValueError(f"{name} must be a finite bounded decimal")
    return normalized


@dataclass(frozen=True)
class ConsensusProvider:
    provider_id: str
    source_kind: str
    registered_artifact_id: str
    artifact_version: str
    license_id: str
    permitted_use: str
    operator_confirmed: bool = True
    local_artifact_only: bool = True
    network_retrieval_allowed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "provider_id",
            "registered_artifact_id",
            "artifact_version",
            "license_id",
            "permitted_use",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        source_kind = str(self.source_kind).strip().upper()
        if source_kind not in SOURCE_KINDS:
            raise ValueError("source_kind must be OFFICIAL or LICENSED")
        object.__setattr__(self, "source_kind", source_kind)
        if self.operator_confirmed is not True or self.local_artifact_only is not True:
            raise ValueError("consensus provider requires Operator-confirmed local artifact")
        if self.network_retrieval_allowed:
            raise ValueError("consensus provider exceeds registered-local scope")


@dataclass(frozen=True)
class RegisteredConsensusSnapshot:
    snapshot_id: str
    subject_id: str
    metric_id: str
    market: str
    horizon: str
    unit: str
    period_end_utc: str
    consensus_as_of_utc: str
    published_at_utc: str
    first_legally_available_at_utc: str
    retrieved_at_utc: str
    ingested_at_utc: str
    provider: ConsensusProvider
    source_event: InstitutionalCalendarEvent
    estimate_count: int
    coverage_bps: int
    mean_value: Decimal | str | int | None
    median_value: Decimal | str | int | None
    lower_value: Decimal | str | int | None
    upper_value: Decimal | str | int | None
    dispersion_value: Decimal | str | int | None
    consensus_state: str = "AVAILABLE"
    freshness_state: str = "FRESH"
    revision_number: int = 0
    revises_snapshot_hash: str | None = None
    survivorship_included: bool = False
    operator_registered: bool = True
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("snapshot_id", "subject_id", "metric_id", "market", "horizon", "unit"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "period_end_utc",
            "consensus_as_of_utc",
            "published_at_utc",
            "first_legally_available_at_utc",
            "retrieved_at_utc",
            "ingested_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        published = instant(self.published_at_utc)
        legal = instant(self.first_legally_available_at_utc)
        retrieved = instant(self.retrieved_at_utc)
        ingested = instant(self.ingested_at_utc)
        if not published <= legal <= retrieved <= ingested:
            raise ValueError("consensus publication, legal, retrieval, and ingest must be ordered")
        if instant(self.consensus_as_of_utc) > published:
            raise ValueError("consensus as-of cannot follow publication")
        if not isinstance(self.provider, ConsensusProvider):
            raise ValueError("provider must be ConsensusProvider")
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("source_event must be registered R23 evidence")
        if ingested < instant(self.source_event.ingested_at_utc):
            raise ValueError("consensus ingest cannot precede source event ingest")
        for name, allowed in (
            ("consensus_state", CONSENSUS_STATES),
            ("freshness_state", FRESHNESS_STATES),
        ):
            value = str(getattr(self, name)).strip().upper()
            if value not in allowed:
                raise ValueError(f"{name} is not registered")
            object.__setattr__(self, name, value)
        if isinstance(self.estimate_count, bool) or self.estimate_count < 0:
            raise ValueError("estimate_count must be nonnegative")
        if isinstance(self.coverage_bps, bool) or not 0 <= self.coverage_bps <= 10000:
            raise ValueError("coverage_bps must be between zero and 10000")
        numeric_names = (
            "mean_value",
            "median_value",
            "lower_value",
            "upper_value",
            "dispersion_value",
        )
        if self.consensus_state == "AVAILABLE":
            if self.estimate_count <= 0 or self.coverage_bps <= 0:
                raise ValueError("available consensus requires estimates and coverage")
            if any(getattr(self, name) is None for name in numeric_names):
                raise ValueError("available consensus requires complete numeric values")
            for name in numeric_names:
                object.__setattr__(self, name, decimal_value(getattr(self, name), name))
            if not self.lower_value <= self.median_value <= self.upper_value:  # type: ignore[operator]
                raise ValueError("consensus range must contain median")
            if self.dispersion_value < 0:  # type: ignore[operator]
                raise ValueError("consensus dispersion must be nonnegative")
        else:
            if self.estimate_count != 0 or self.coverage_bps != 0:
                raise ValueError("missing consensus requires zero estimates and coverage")
            if any(getattr(self, name) is not None for name in numeric_names):
                raise ValueError("missing consensus cannot contain numeric values")
        if self.freshness_state == "STALE" and self.consensus_state == "AVAILABLE":
            pass
        if isinstance(self.revision_number, bool) or self.revision_number < 0:
            raise ValueError("revision_number must be nonnegative")
        if self.revision_number == 0:
            if self.revises_snapshot_hash is not None:
                raise ValueError("revision zero cannot identify a predecessor")
        else:
            if self.revises_snapshot_hash is None:
                raise ValueError("later revision requires predecessor hash")
            object.__setattr__(
                self,
                "revises_snapshot_hash",
                sha256_text(self.revises_snapshot_hash, "revises_snapshot_hash"),
            )
        if self.survivorship_included:
            raise ValueError("consensus snapshot cannot include survivorship substitution")
        if self.operator_registered is not True:
            raise ValueError("consensus snapshot requires Operator registration")
        payload = {
            name: str(getattr(self, name)) if name in numeric_names and getattr(self, name) is not None else getattr(self, name)
            for name in (
                "snapshot_id", "subject_id", "metric_id", "market", "horizon", "unit",
                "period_end_utc", "consensus_as_of_utc", "published_at_utc",
                "first_legally_available_at_utc", "retrieved_at_utc", "ingested_at_utc",
                "estimate_count", "coverage_bps", *numeric_names, "consensus_state",
                "freshness_state", "revision_number", "revises_snapshot_hash",
                "survivorship_included", "operator_registered",
            )
        }
        payload["provider_id"] = self.provider.provider_id
        payload["source_event_hash"] = self.source_event.record_hash
        object.__setattr__(self, "snapshot_hash", _hash(payload))


@dataclass(frozen=True)
class RegisteredActualObservation:
    observation_id: str
    subject_id: str
    metric_id: str
    market: str
    horizon: str
    unit: str
    value: Decimal | str | int
    observed_at_utc: str
    available_at_utc: str
    source_event: InstitutionalCalendarEvent
    operator_registered: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("observation_id", "subject_id", "metric_id", "market", "horizon", "unit"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "value", decimal_value(self.value, "value"))
        object.__setattr__(self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc"))
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("source_event must be registered R23 evidence")
        if instant(self.available_at_utc) < max(
            instant(self.observed_at_utc), instant(self.source_event.ingested_at_utc)
        ):
            raise ValueError("actual availability cannot precede observation or source ingest")
        if self.operator_registered is not True:
            raise ValueError("actual observation requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "horizon": self.horizon,
            "market": self.market,
            "metric_id": self.metric_id,
            "observation_id": self.observation_id,
            "observed_at_utc": self.observed_at_utc,
            "operator_registered": self.operator_registered,
            "source_event_hash": self.source_event.record_hash,
            "subject_id": self.subject_id,
            "unit": self.unit,
            "value": str(self.value),
        }
        object.__setattr__(self, "observation_hash", _hash(payload))


@dataclass(frozen=True)
class ExpectationGapRecord:
    gap_id: str
    consensus: RegisteredConsensusSnapshot
    actual: RegisteredActualObservation
    available_at_utc: str
    reference_kind: str = "CONSENSUS_MEDIAN"
    factor_activated: bool = False
    operator_registered: bool = True
    gap_value: Decimal = field(init=False)
    standardized_gap: Decimal | None = field(init=False)
    gap_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "gap_id", identifier(self.gap_id, "gap_id"))
        if not isinstance(self.consensus, RegisteredConsensusSnapshot):
            raise ValueError("gap requires registered consensus")
        if not isinstance(self.actual, RegisteredActualObservation):
            raise ValueError("gap requires registered actual observation")
        if self.consensus.consensus_state != "AVAILABLE":
            raise ValueError("missing consensus cannot create an expectation gap")
        dimensions = ("subject_id", "metric_id", "market", "horizon", "unit")
        if any(getattr(self.consensus, name) != getattr(self.actual, name) for name in dimensions):
            raise ValueError("consensus and actual dimensions must match")
        if self.reference_kind != "CONSENSUS_MEDIAN":
            raise ValueError("reference_kind is not registered")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if instant(self.available_at_utc) < max(
            instant(self.consensus.ingested_at_utc), instant(self.actual.available_at_utc)
        ):
            raise ValueError("gap availability cannot precede evidence")
        gap = self.actual.value - self.consensus.median_value  # type: ignore[operator]
        dispersion = self.consensus.dispersion_value
        standardized = None if dispersion == 0 else gap / dispersion  # type: ignore[operator]
        object.__setattr__(self, "gap_value", gap)
        object.__setattr__(self, "standardized_gap", standardized)
        if self.factor_activated:
            raise ValueError("expectation gap cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("expectation gap requires Operator registration")
        payload = {
            "actual_hash": self.actual.observation_hash,
            "available_at_utc": self.available_at_utc,
            "consensus_hash": self.consensus.snapshot_hash,
            "factor_activated": self.factor_activated,
            "gap_id": self.gap_id,
            "gap_value": str(self.gap_value),
            "operator_registered": self.operator_registered,
            "reference_kind": self.reference_kind,
            "standardized_gap": None if standardized is None else str(standardized),
        }
        object.__setattr__(self, "gap_hash", _hash(payload))
