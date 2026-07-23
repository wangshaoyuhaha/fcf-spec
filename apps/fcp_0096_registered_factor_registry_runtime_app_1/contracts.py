from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, utc
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import (
    FactorDefinition,
)


PHASE_ID = "FCF-FCP-0096-REGISTERED-FACTOR-REGISTRY-RUNTIME-APP-1"
RUNTIME_SCHEMA_VERSION = "fcf-registered-factor-registry-runtime-v1"


@dataclass(frozen=True)
class RegisteredFactorArtifact:
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
            raise ValueError("factor artifact must be Operator-registered")


@dataclass(frozen=True)
class RegisteredFactorRecord:
    definition: FactorDefinition
    effective_at_utc: str
    retired_at_utc: str | None = None
    replacement_factor_ref: str | None = None
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.definition) is not FactorDefinition:
            raise TypeError("definition must be an exact FactorDefinition")
        effective = utc(self.effective_at_utc, "effective_at_utc")
        retired = (
            None
            if self.retired_at_utc is None
            else utc(self.retired_at_utc, "retired_at_utc")
        )
        replacement = (
            None
            if self.replacement_factor_ref is None
            else str(self.replacement_factor_ref).strip()
        )
        if retired is not None and retired < effective:
            raise ValueError("retired_at_utc cannot precede effective_at_utc")
        if self.definition.lifecycle == "RETIRED":
            if retired is None:
                raise ValueError("retired factor requires retired_at_utc")
        elif retired is not None or replacement is not None:
            raise ValueError("only retired factors may declare retirement metadata")
        if replacement == self.definition.natural_key:
            raise ValueError("retired factor cannot replace itself")
        object.__setattr__(self, "effective_at_utc", effective)
        object.__setattr__(self, "retired_at_utc", retired)
        object.__setattr__(self, "replacement_factor_ref", replacement)
        object.__setattr__(
            self,
            "record_hash",
            canonical_sha256(
                {
                    "definition": {
                        "asset_scopes": list(self.definition.asset_scopes),
                        "calculation_spec_hash": self.definition.calculation_spec_hash,
                        "dependency_factor_refs": list(
                            self.definition.dependency_factor_refs
                        ),
                        "factor_id": self.definition.factor_id,
                        "family": self.definition.family,
                        "input_field_ids": list(self.definition.input_field_ids),
                        "lifecycle": self.definition.lifecycle,
                        "maximum_lookback": self.definition.maximum_lookback,
                        "minimum_lookback": self.definition.minimum_lookback,
                        "output_unit": self.definition.output_unit,
                        "source_type": self.definition.source_type,
                        "version": self.definition.version,
                    },
                    "effective_at_utc": effective,
                    "replacement_factor_ref": replacement,
                    "retired_at_utc": retired,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredFactorRuntimeSnapshot:
    artifact_id: str
    artifact_hash: str
    registry_id: str
    registry_version: str
    record_hashes: Mapping[str, str]
    dependency_graph: Mapping[str, tuple[str, ...]]
    reverse_dependency_graph: Mapping[str, tuple[str, ...]]
    topological_order: tuple[str, ...]
    retired_factor_refs: tuple[str, ...]
    invalidated_factor_refs: tuple[str, ...]
    replacement_map: Mapping[str, str]
    observed_at_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    calculation_activation_allowed: bool = False
    scoring_allowed: bool = False
    promotion_allowed: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        registry_id = identifier(self.registry_id, "registry_id")
        registry_version = identifier(self.registry_version, "registry_version")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        record_hashes = dict(sorted(self.record_hashes.items()))
        dependency_graph = {
            key: tuple(value) for key, value in sorted(self.dependency_graph.items())
        }
        reverse_graph = {
            key: tuple(value)
            for key, value in sorted(self.reverse_dependency_graph.items())
        }
        replacement_map = dict(sorted(self.replacement_map.items()))
        keys = tuple(record_hashes)
        if not keys:
            raise ValueError("runtime snapshot requires factor records")
        if set(dependency_graph) != set(keys) or set(reverse_graph) != set(keys):
            raise ValueError("runtime graph keys must match factor records")
        if set(self.topological_order) != set(keys) or len(self.topological_order) != len(
            keys
        ):
            raise ValueError("topological_order must contain each factor exactly once")
        if tuple(sorted(set(self.retired_factor_refs))) != self.retired_factor_refs:
            raise ValueError("retired_factor_refs must be unique and sorted")
        if tuple(sorted(set(self.invalidated_factor_refs))) != self.invalidated_factor_refs:
            raise ValueError("invalidated_factor_refs must be unique and sorted")
        if not set(self.retired_factor_refs).issubset(keys):
            raise ValueError("retired factors must be registered")
        if not set(self.invalidated_factor_refs).issubset(keys):
            raise ValueError("invalidated factors must be registered")
        if not set(replacement_map).issubset(self.retired_factor_refs):
            raise ValueError("only retired factors may have replacements")
        if any(value not in keys for value in replacement_map.values()):
            raise ValueError("replacement factors must be registered")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or any(
                (
                    self.calculation_activation_allowed,
                    self.scoring_allowed,
                    self.promotion_allowed,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("runtime snapshot exceeds read-only registry authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "registry_version", registry_version)
        object.__setattr__(self, "record_hashes", MappingProxyType(record_hashes))
        object.__setattr__(self, "dependency_graph", MappingProxyType(dependency_graph))
        object.__setattr__(
            self, "reverse_dependency_graph", MappingProxyType(reverse_graph)
        )
        object.__setattr__(self, "replacement_map", MappingProxyType(replacement_map))
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "dependency_graph": dependency_graph,
                    "invalidated_factor_refs": list(self.invalidated_factor_refs),
                    "observed_at_utc": observed,
                    "record_hashes": record_hashes,
                    "registry_id": registry_id,
                    "registry_version": registry_version,
                    "replacement_map": replacement_map,
                    "retired_factor_refs": list(self.retired_factor_refs),
                    "schema_version": self.schema_version,
                    "topological_order": list(self.topological_order),
                }
            ),
        )
