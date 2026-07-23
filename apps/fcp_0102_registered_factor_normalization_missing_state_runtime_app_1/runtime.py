from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from apps.fcp_0096_registered_factor_registry_runtime_app_1.contracts import (
    RegisteredFactorRuntimeSnapshot,
)
from apps.v2_r21_local_robust_normalization_foundation_app_1 import (
    NormalizationPolicy,
    RegisteredFactorPoint,
    RegisteredFactorSeries,
    build_normalization,
)

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredNormalizationArtifact,
    RegisteredNormalizationSnapshot,
    decimal_text,
)


TOP_LEVEL_FIELDS = {
    "decimal_places",
    "factor_definition_ref",
    "mad_clip_multiplier",
    "minimum_samples",
    "normalization_id",
    "normalization_version",
    "points",
    "registry_id",
    "registry_version",
    "schema_version",
    "series_id",
    "target_point_id",
}
POINT_FIELDS = {
    "available_at_utc",
    "instrument_id",
    "missing_state",
    "observed_at_utc",
    "point_id",
    "source_artifact_hash",
    "value",
}


def _closed(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def _decimal(value: object, name: str) -> Decimal:
    if type(value) is not str:
        raise ValueError(f"{name} must be a decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{name} must be decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class _RegistryEvidenceAdapter:
    registry_id: str
    registry_version: str
    definition_keys: tuple[str, ...]
    evidence_hash: str
    state: str = "REGISTRY_READY"


def normalize_registered_factor_series(
    content: bytes,
    artifact: RegisteredNormalizationArtifact,
    registry: RegisteredFactorRuntimeSnapshot,
    *,
    as_of_utc: str,
) -> RegisteredNormalizationSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered normalization artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered normalization artifact hash mismatch")
    if type(registry) is not RegisteredFactorRuntimeSnapshot:
        raise TypeError("registry must be an exact registered runtime snapshot")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered normalization artifact must be ASCII JSON") from exc
    payload = _closed(payload, TOP_LEVEL_FIELDS, "normalization artifact")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered normalization schema mismatch")
    if (
        payload["registry_id"] != registry.registry_id
        or payload["registry_version"] != registry.registry_version
    ):
        raise ValueError("registered normalization registry identity mismatch")
    factor_ref = str(payload["factor_definition_ref"])
    if factor_ref not in registry.topological_order:
        raise ValueError("normalization factor is not in the registered runtime")
    if factor_ref in registry.invalidated_factor_refs:
        raise ValueError("invalidated factor cannot be normalized")
    raw_points = payload["points"]
    if type(raw_points) is not list or not raw_points:
        raise ValueError("normalization artifact must contain points")
    points = []
    for raw in raw_points:
        point = _closed(raw, POINT_FIELDS, "factor point")
        value = point["value"]
        points.append(
            RegisteredFactorPoint(
                point_id=point["point_id"],
                factor_definition_ref=factor_ref,
                instrument_id=point["instrument_id"],
                observed_at_utc=point["observed_at_utc"],
                available_at_utc=point["available_at_utc"],
                value=None if value is None else _decimal(value, "value"),
                missing_state=point["missing_state"],
                source_artifact_hash=point["source_artifact_hash"],
            )
        )
    series = RegisteredFactorSeries(
        series_id=payload["series_id"],
        points=tuple(points),
    )
    policy = NormalizationPolicy(
        normalization_id=payload["normalization_id"],
        normalization_version=payload["normalization_version"],
        factor_definition_ref=factor_ref,
        registry_id=payload["registry_id"],
        registry_version=payload["registry_version"],
        target_point_id=payload["target_point_id"],
        minimum_samples=payload["minimum_samples"],
        mad_clip_multiplier=_decimal(
            payload["mad_clip_multiplier"], "mad_clip_multiplier"
        ),
        decimal_places=payload["decimal_places"],
    )
    evidence = build_normalization(
        series,
        _RegistryEvidenceAdapter(
            registry_id=registry.registry_id,
            registry_version=registry.registry_version,
            definition_keys=registry.topological_order,
            evidence_hash=registry.snapshot_hash,
        ),
        policy,
        as_of_utc=as_of_utc,
    )
    return RegisteredNormalizationSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        registry_snapshot_hash=registry.snapshot_hash,
        factor_definition_ref=evidence.factor_definition_ref,
        series_id=evidence.series_id,
        target_point_id=evidence.target_point_id,
        state=evidence.state,
        missing_state=evidence.missing_state,
        metrics={
            "available_sample_count": str(evidence.available_sample_count),
            "mad": decimal_text(evidence.mad),
            "median": decimal_text(evidence.median),
            "minimum_samples": str(evidence.minimum_samples),
            "robust_z_score": decimal_text(evidence.robust_z_score),
            "winsorized_value": decimal_text(evidence.winsorized_value),
        },
        reason_codes=evidence.reason_codes,
        evidence_hash=evidence.evidence_hash,
        evaluated_at_utc=evidence.evaluated_at_utc,
    )
