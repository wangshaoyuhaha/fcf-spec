from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType

from apps.fcp_0101_registered_technical_indicator_core_runtime_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
    utc,
)
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import factor_ref


PHASE_ID = "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1"
RUNTIME_SCHEMA_VERSION = "fcf-registered-volume-flow-indicator-runtime-v1"
INDICATOR_KINDS = ("MFI", "OBV", "VOLUME_PRICE_TREND")


@dataclass(frozen=True)
class RegisteredVolumeFlowArtifact:
    artifact_id: str
    artifact_hash: str
    byte_length: int
    rights_id: str
    registered_at_utc: str
    operator_registered: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "artifact_hash", digest(self.artifact_hash, "artifact_hash"))
        if isinstance(self.byte_length, bool) or self.byte_length <= 0:
            raise ValueError("byte_length must be a positive integer")
        object.__setattr__(self, "rights_id", identifier(self.rights_id, "rights_id"))
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if self.operator_registered is not True:
            raise ValueError("artifact must be Operator-registered")


@dataclass(frozen=True)
class VolumeFlowBar:
    timestamp_utc: str
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    amount: Decimal
    is_suspended: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp_utc", utc(self.timestamp_utc, "timestamp_utc"))
        if any(
            not value.is_finite() or value <= 0
            for value in (self.high, self.low, self.close)
        ):
            raise ValueError("prices must be positive finite decimals")
        if self.high < max(self.low, self.close) or self.low > self.close:
            raise ValueError("price ordering is invalid")
        if (
            not self.volume.is_finite()
            or not self.amount.is_finite()
            or self.volume < 0
            or self.amount < 0
        ):
            raise ValueError("volume and amount must be nonnegative finite decimals")
        if type(self.is_suspended) is not bool:
            raise ValueError("is_suspended must be boolean")
        if self.is_suspended != (self.volume == 0 and self.amount == 0):
            raise ValueError("suspension must match zero volume and amount")


@dataclass(frozen=True)
class VolumeFlowRequest:
    request_id: str
    indicator_kind: str
    factor_ref: str
    window: int
    suspension_policy: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", identifier(self.request_id, "request_id"))
        kind = str(self.indicator_kind).strip().upper()
        if kind not in INDICATOR_KINDS:
            raise ValueError("indicator_kind is not registered")
        object.__setattr__(self, "indicator_kind", kind)
        object.__setattr__(self, "factor_ref", factor_ref(self.factor_ref, "factor_ref"))
        if isinstance(self.window, bool) or not 1 <= self.window <= 10000:
            raise ValueError("window must be an integer between 1 and 10000")
        policy = str(self.suspension_policy).strip().upper()
        if policy != "EXCLUDE":
            raise ValueError("only registered EXCLUDE suspension policy is allowed")
        object.__setattr__(self, "suspension_policy", policy)


@dataclass(frozen=True)
class RegisteredVolumeFlowSnapshot:
    artifact_id: str
    artifact_hash: str
    dataset_id: str
    dataset_version: str
    registry_id: str
    registry_version: str
    registry_snapshot_hash: str
    catalog_id: str
    catalog_version: str
    supported_kind_sources: Mapping[str, str]
    missing_candidate_kinds: tuple[str, ...]
    result_values: Mapping[str, Mapping[str, str]]
    result_hashes: Mapping[str, str]
    source_last_timestamp_utc: str
    as_of_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    deterministic_engine_authority: bool = True
    scoring_authority: bool = False
    ranking_authority: bool = False
    recommendation_authority: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        sources = dict(sorted(self.supported_kind_sources.items()))
        values = {
            key: MappingProxyType(dict(sorted(value.items())))
            for key, value in sorted(self.result_values.items())
        }
        hashes = dict(sorted(self.result_hashes.items()))
        if set(values) != set(hashes) or not values:
            raise ValueError("result values and hashes must share nonempty keys")
        if tuple(sorted(set(self.missing_candidate_kinds))) != self.missing_candidate_kinds:
            raise ValueError("missing candidates must be unique and sorted")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or self.deterministic_engine_authority is not True
            or any(
                (
                    self.scoring_authority,
                    self.ranking_authority,
                    self.recommendation_authority,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("snapshot exceeds deterministic read-only authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        for name in (
            "artifact_id",
            "dataset_id",
            "dataset_version",
            "registry_id",
            "registry_version",
            "catalog_id",
            "catalog_version",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "artifact_hash", digest(self.artifact_hash, "artifact_hash"))
        object.__setattr__(
            self,
            "registry_snapshot_hash",
            digest(self.registry_snapshot_hash, "registry_snapshot_hash"),
        )
        object.__setattr__(self, "source_last_timestamp_utc", utc(self.source_last_timestamp_utc, "source_last_timestamp_utc"))
        object.__setattr__(self, "as_of_utc", utc(self.as_of_utc, "as_of_utc"))
        object.__setattr__(self, "supported_kind_sources", MappingProxyType(sources))
        object.__setattr__(self, "result_values", MappingProxyType(values))
        object.__setattr__(self, "result_hashes", MappingProxyType(hashes))
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": self.artifact_hash,
                    "artifact_id": self.artifact_id,
                    "as_of_utc": self.as_of_utc,
                    "catalog_id": self.catalog_id,
                    "catalog_version": self.catalog_version,
                    "dataset_id": self.dataset_id,
                    "dataset_version": self.dataset_version,
                    "missing_candidate_kinds": list(self.missing_candidate_kinds),
                    "registry_id": self.registry_id,
                    "registry_snapshot_hash": self.registry_snapshot_hash,
                    "registry_version": self.registry_version,
                    "result_hashes": hashes,
                    "result_values": {
                        key: dict(value) for key, value in values.items()
                    },
                    "schema_version": self.schema_version,
                    "source_last_timestamp_utc": self.source_last_timestamp_utc,
                    "supported_kind_sources": sources,
                }
            ),
        )
