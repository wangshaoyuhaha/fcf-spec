from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0101_registered_technical_indicator_core_runtime_app_1.contracts import (
    digest,
    identifier,
    utc,
)


PHASE_ID = (
    "FCF-FCP-0102-REGISTERED-FACTOR-NORMALIZATION-MISSING-STATE-RUNTIME-APP-1"
)
RUNTIME_SCHEMA_VERSION = (
    "fcf-registered-factor-normalization-missing-state-runtime-v1"
)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class RegisteredNormalizationArtifact:
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
            raise ValueError("normalization artifact must be Operator-registered")


@dataclass(frozen=True)
class RegisteredNormalizationSnapshot:
    artifact_id: str
    artifact_hash: str
    registry_snapshot_hash: str
    factor_definition_ref: str
    series_id: str
    target_point_id: str
    state: str
    missing_state: str
    metrics: Mapping[str, str | None]
    reason_codes: tuple[str, ...]
    evidence_hash: str
    evaluated_at_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    deterministic_engine_authority: bool = True
    scoring_authority: bool = False
    recommendation_authority: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        registry_hash = digest(
            self.registry_snapshot_hash, "registry_snapshot_hash"
        )
        evidence_hash = digest(self.evidence_hash, "evidence_hash")
        factor_ref = str(self.factor_definition_ref).strip()
        if factor_ref.count("@") != 1:
            raise ValueError("factor_definition_ref must use factor-id@version")
        identifier(factor_ref.split("@", 1)[0], "factor_id")
        identifier(factor_ref.split("@", 1)[1], "factor_version")
        series_id = identifier(self.series_id, "series_id")
        target_id = identifier(self.target_point_id, "target_point_id")
        evaluated = utc(self.evaluated_at_utc, "evaluated_at_utc")
        metrics = MappingProxyType(dict(sorted(self.metrics.items())))
        if set(metrics) != {
            "available_sample_count",
            "mad",
            "median",
            "minimum_samples",
            "robust_z_score",
            "winsorized_value",
        }:
            raise ValueError("normalization metrics must use the closed schema")
        if self.state not in {
            "NORMALIZATION_READY",
            "MISSING_STATE_RECORDED",
            "BLOCKED",
        }:
            raise ValueError("normalization state is not registered")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or self.deterministic_engine_authority is not True
            or any(
                (
                    self.scoring_authority,
                    self.recommendation_authority,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("normalization snapshot exceeds deterministic authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "registry_snapshot_hash", registry_hash)
        object.__setattr__(self, "factor_definition_ref", factor_ref)
        object.__setattr__(self, "series_id", series_id)
        object.__setattr__(self, "target_point_id", target_id)
        object.__setattr__(self, "metrics", metrics)
        object.__setattr__(self, "evidence_hash", evidence_hash)
        object.__setattr__(self, "evaluated_at_utc", evaluated)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "evaluated_at_utc": evaluated,
                    "evidence_hash": evidence_hash,
                    "factor_definition_ref": factor_ref,
                    "metrics": dict(metrics),
                    "missing_state": self.missing_state,
                    "reason_codes": self.reason_codes,
                    "registry_snapshot_hash": registry_hash,
                    "schema_version": self.schema_version,
                    "series_id": series_id,
                    "state": self.state,
                    "target_point_id": target_id,
                }
            ),
        )
