from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    AShareDailyObservation,
    canonical_decimal,
    canonical_sha256,
    decimal_value,
    digest,
    identifier,
    instant,
    utc,
)


@dataclass(frozen=True)
class RegisteredCanonicalDailyDataset:
    dataset_id: str
    source_id: str
    observations: tuple[AShareDailyObservation, ...]
    as_of_utc: str
    schema_version: str = "a-share-daily-v1"
    currency: str = "CNY"
    volume_unit: str = "SHARES"
    amount_unit: str = "CNY"
    rights_state: str = "DECLARED_LOCAL_RESEARCH"
    retention_state: str = "LOCAL_DERIVED_ONLY"
    operator_registered: bool = True
    local_only: bool = True
    provider_selected: bool = False
    dataset_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset_id", identifier(self.dataset_id, "dataset_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        observations = tuple(self.observations)
        if not observations or not all(
            isinstance(item, AShareDailyObservation) for item in observations
        ):
            raise ValueError("dataset requires typed A-share daily observations")
        keys = tuple((item.instrument_id, item.trade_date) for item in observations)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("dataset observations must be uniquely and deterministically ordered")
        if self.schema_version != "a-share-daily-v1":
            raise ValueError("schema_version is not registered")
        if self.currency != "CNY" or self.amount_unit != "CNY":
            raise ValueError("A-share price and amount currency must be CNY")
        if self.volume_unit != "SHARES":
            raise ValueError("A-share volume unit must be SHARES")
        if self.rights_state not in {"UNRESOLVED", "DECLARED_LOCAL_RESEARCH"}:
            raise ValueError("rights_state is not registered")
        if self.retention_state not in {"UNRESOLVED", "LOCAL_DERIVED_ONLY"}:
            raise ValueError("retention_state is not registered")
        if (
            self.operator_registered is not True
            or self.local_only is not True
            or self.provider_selected
        ):
            raise ValueError("dataset must remain registered-local and provider-unselected")
        as_of = utc(self.as_of_utc, "as_of_utc")
        as_of_instant = instant(as_of, "as_of_utc")
        if any(
            instant(item.revision_at_utc, "revision_at_utc") > as_of_instant
            or (
                item.factor_available_at_utc is not None
                and instant(item.factor_available_at_utc, "factor_available_at_utc")
                > as_of_instant
            )
            for item in observations
        ):
            raise ValueError("dataset cannot contain knowledge after as_of_utc")
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "dataset_hash",
            canonical_sha256(
                {
                    "amount_unit": self.amount_unit,
                    "as_of_utc": self.as_of_utc,
                    "currency": self.currency,
                    "dataset_id": self.dataset_id,
                    "observations": [
                        {
                            "adjustment_factor": (
                                canonical_decimal(item.adjustment_factor)
                                if item.adjustment_factor is not None
                                else None
                            ),
                            "factor_available_at_utc": item.factor_available_at_utc,
                            "factor_version": item.factor_version,
                            "raw": dict(item.raw_payload()),
                            "source_artifact_sha256": item.source_artifact_sha256,
                        }
                        for item in observations
                    ],
                    "retention_state": self.retention_state,
                    "rights_state": self.rights_state,
                    "schema_version": self.schema_version,
                    "source_id": self.source_id,
                    "volume_unit": self.volume_unit,
                }
            ),
        )


@dataclass(frozen=True)
class AShareCrossSourceReconciliationPolicy:
    policy_id: str
    price_tolerance: Decimal = Decimal("0")
    amount_tolerance: Decimal = Decimal("0")
    volume_tolerance: int = 0
    clock_tolerance_seconds: int = 0
    operator_registered: bool = True
    source_selection_allowed: bool = False
    policy_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        price = decimal_value(self.price_tolerance, "price_tolerance")
        amount = decimal_value(self.amount_tolerance, "amount_tolerance")
        if price > Decimal("100") or amount > Decimal("1000000000"):
            raise ValueError("reconciliation tolerance exceeds its bounded domain")
        if (
            isinstance(self.volume_tolerance, bool)
            or not isinstance(self.volume_tolerance, int)
            or not 0 <= self.volume_tolerance <= 1_000_000_000
        ):
            raise ValueError("volume_tolerance is outside its bounded domain")
        if (
            isinstance(self.clock_tolerance_seconds, bool)
            or not isinstance(self.clock_tolerance_seconds, int)
            or not 0 <= self.clock_tolerance_seconds <= 86_400
        ):
            raise ValueError("clock_tolerance_seconds is outside its bounded domain")
        if self.operator_registered is not True or self.source_selection_allowed:
            raise ValueError("policy requires Operator registration and cannot select a source")
        object.__setattr__(self, "price_tolerance", price)
        object.__setattr__(self, "amount_tolerance", amount)
        object.__setattr__(
            self,
            "policy_hash",
            canonical_sha256(
                {
                    "amount_tolerance": canonical_decimal(amount),
                    "clock_tolerance_seconds": self.clock_tolerance_seconds,
                    "policy_id": self.policy_id,
                    "price_tolerance": canonical_decimal(price),
                    "volume_tolerance": self.volume_tolerance,
                }
            ),
        )


@dataclass(frozen=True)
class CrossSourceQualityFinding:
    code: str
    severity: str
    dataset_ids: tuple[str, ...]
    instrument_id: str | None = None
    trade_date: str | None = None
    field_name: str | None = None
    detail: Mapping[str, str] = field(default_factory=dict)
    finding_hash: str = field(init=False)

    def __post_init__(self) -> None:
        code = identifier(self.code, "finding code")
        if self.severity not in {"BLOCK", "WARN"}:
            raise ValueError("finding severity is not registered")
        datasets = tuple(sorted(set(identifier(item, "dataset_id") for item in self.dataset_ids)))
        if not datasets:
            raise ValueError("finding requires dataset lineage")
        if (self.instrument_id is None) != (self.trade_date is None):
            raise ValueError("finding row identity must be complete")
        if self.instrument_id is not None:
            instrument = str(self.instrument_id).strip().upper()
            if len(instrument) != 11 or instrument[6:] not in {".XSHG", ".XSHE"}:
                raise ValueError("finding instrument_id is not an A-share identifier")
            object.__setattr__(self, "instrument_id", instrument)
            try:
                date.fromisoformat(str(self.trade_date))
            except (TypeError, ValueError) as exc:
                raise ValueError("finding trade_date must be an ISO date") from exc
        if self.field_name is not None:
            object.__setattr__(
                self,
                "field_name",
                identifier(self.field_name, "field_name"),
            )
        detail = {
            identifier(key, "detail key"): str(value)
            for key, value in self.detail.items()
        }
        object.__setattr__(self, "code", code)
        object.__setattr__(self, "dataset_ids", datasets)
        object.__setattr__(self, "detail", MappingProxyType(detail))
        object.__setattr__(
            self,
            "finding_hash",
            canonical_sha256(
                {
                    "code": code,
                    "dataset_ids": datasets,
                    "detail": detail,
                    "field_name": self.field_name,
                    "instrument_id": self.instrument_id,
                    "severity": self.severity,
                    "trade_date": self.trade_date,
                }
            ),
        )


@dataclass(frozen=True)
class AShareCrossSourceReconciliationResult:
    dataset_hashes: tuple[str, ...]
    policy_hash: str
    union_key_count: int
    overlap_key_count: int
    findings: tuple[CrossSourceQualityFinding, ...]
    quality_state: str
    operator_review_required: bool = True
    source_selected: bool = False
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        findings = tuple(self.findings)
        if not all(isinstance(item, CrossSourceQualityFinding) for item in findings):
            raise ValueError("result findings must be typed")
        if findings != tuple(sorted(findings, key=lambda item: item.finding_hash)):
            raise ValueError("result findings must be deterministically ordered")
        dataset_hashes = tuple(digest(item, "dataset_hash") for item in self.dataset_hashes)
        if len(dataset_hashes) < 2 or len(dataset_hashes) != len(set(dataset_hashes)):
            raise ValueError("result requires distinct dataset hashes")
        policy_hash = digest(self.policy_hash, "policy_hash")
        if self.quality_state not in {"CONSISTENT", "QUARANTINE_REVIEW_REQUIRED"}:
            raise ValueError("quality_state is not registered")
        blocked = any(item.severity == "BLOCK" for item in findings)
        if (self.quality_state == "QUARANTINE_REVIEW_REQUIRED") != blocked:
            raise ValueError("quality_state and findings disagree")
        if self.operator_review_required is not True or self.source_selected:
            raise ValueError("reconciliation cannot bypass review or select a source")
        if not 0 <= self.overlap_key_count <= self.union_key_count:
            raise ValueError("reconciliation key counts are inconsistent")
        object.__setattr__(self, "dataset_hashes", dataset_hashes)
        object.__setattr__(self, "policy_hash", policy_hash)
        object.__setattr__(self, "findings", findings)
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(
                {
                    "dataset_hashes": dataset_hashes,
                    "finding_hashes": [item.finding_hash for item in findings],
                    "overlap_key_count": self.overlap_key_count,
                    "policy_hash": policy_hash,
                    "quality_state": self.quality_state,
                    "union_key_count": self.union_key_count,
                }
            ),
        )
