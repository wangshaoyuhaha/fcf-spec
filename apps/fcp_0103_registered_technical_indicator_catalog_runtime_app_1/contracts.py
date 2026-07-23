from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from apps.fcp_0101_registered_technical_indicator_core_runtime_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
    utc,
)
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import (
    factor_ref,
)


PHASE_ID = "FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1"
RUNTIME_SCHEMA_VERSION = "fcf-registered-technical-indicator-catalog-runtime-v1"


@dataclass(frozen=True)
class RegisteredIndicatorCatalogArtifact:
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
            raise ValueError("catalog artifact must be Operator-registered")


@dataclass(frozen=True)
class IndicatorCatalogEntry:
    indicator_kind: str
    factor_ref: str
    foundation_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "indicator_kind",
            identifier(self.indicator_kind, "indicator_kind").upper(),
        )
        object.__setattr__(
            self,
            "factor_ref",
            factor_ref(self.factor_ref, "factor_ref"),
        )
        object.__setattr__(
            self,
            "foundation_ref",
            identifier(self.foundation_ref, "foundation_ref"),
        )
        if "@" not in self.factor_ref:
            raise ValueError("factor_ref must include a version")


@dataclass(frozen=True)
class RegisteredIndicatorCatalogSnapshot:
    artifact_id: str
    artifact_hash: str
    catalog_id: str
    catalog_version: str
    registry_id: str
    registry_version: str
    registry_snapshot_hash: str
    supported_kind_sources: Mapping[str, str]
    factor_refs: Mapping[str, str]
    missing_candidate_kinds: tuple[str, ...]
    reason_codes: tuple[str, ...]
    observed_at_utc: str
    state: str
    operator_review_required: bool = True
    read_only: bool = True
    calculation_activation_allowed: bool = False
    scoring_allowed: bool = False
    ranking_allowed: bool = False
    recommendation_allowed: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.state not in {"CATALOG_READY", "CATALOG_PARTIAL"}:
            raise ValueError("invalid catalog state")
        sources = dict(sorted(self.supported_kind_sources.items()))
        factors = dict(sorted(self.factor_refs.items()))
        if not sources or set(sources) != set(factors):
            raise ValueError("catalog sources and factors must share nonempty keys")
        if tuple(sorted(set(self.missing_candidate_kinds))) != self.missing_candidate_kinds:
            raise ValueError("missing_candidate_kinds must be unique and sorted")
        if self.state == "CATALOG_READY" and self.missing_candidate_kinds:
            raise ValueError("ready catalog cannot report missing candidates")
        if self.state == "CATALOG_PARTIAL" and not self.missing_candidate_kinds:
            raise ValueError("partial catalog must report missing candidates")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or any(
                (
                    self.calculation_activation_allowed,
                    self.scoring_allowed,
                    self.ranking_allowed,
                    self.recommendation_allowed,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("catalog exceeds read-only authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "artifact_hash", digest(self.artifact_hash, "artifact_hash"))
        object.__setattr__(self, "catalog_id", identifier(self.catalog_id, "catalog_id"))
        object.__setattr__(
            self,
            "catalog_version",
            identifier(self.catalog_version, "catalog_version"),
        )
        object.__setattr__(self, "registry_id", identifier(self.registry_id, "registry_id"))
        object.__setattr__(
            self,
            "registry_version",
            identifier(self.registry_version, "registry_version"),
        )
        object.__setattr__(
            self,
            "registry_snapshot_hash",
            digest(self.registry_snapshot_hash, "registry_snapshot_hash"),
        )
        object.__setattr__(self, "supported_kind_sources", MappingProxyType(sources))
        object.__setattr__(self, "factor_refs", MappingProxyType(factors))
        object.__setattr__(
            self,
            "observed_at_utc",
            utc(self.observed_at_utc, "observed_at_utc"),
        )
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": self.artifact_hash,
                    "artifact_id": self.artifact_id,
                    "catalog_id": self.catalog_id,
                    "catalog_version": self.catalog_version,
                    "factor_refs": factors,
                    "missing_candidate_kinds": list(self.missing_candidate_kinds),
                    "observed_at_utc": self.observed_at_utc,
                    "reason_codes": list(self.reason_codes),
                    "registry_id": self.registry_id,
                    "registry_snapshot_hash": self.registry_snapshot_hash,
                    "registry_version": self.registry_version,
                    "schema_version": self.schema_version,
                    "state": self.state,
                    "supported_kind_sources": sources,
                }
            ),
        )
