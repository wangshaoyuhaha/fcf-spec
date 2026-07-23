from __future__ import annotations

import hashlib
import json

from apps.fcp_0096_registered_factor_registry_runtime_app_1.builder import (
    build_reference_runtime_snapshot,
)

from .contracts import RegisteredNormalizationArtifact
from .runtime import normalize_registered_factor_series


def build_reference_artifact_bytes(*, target_missing: bool = False) -> bytes:
    values = ("1", "2", "3", "4", "100")
    points = [
        {
            "available_at_utc": f"2026-07-{index:02d}T00:01:00Z",
            "instrument_id": "BTC-USD",
            "missing_state": (
                "NOT_YET_PUBLISHED" if target_missing and index == 5 else "AVAILABLE"
            ),
            "observed_at_utc": f"2026-07-{index:02d}T00:00:00Z",
            "point_id": f"factor-point-{index}",
            "source_artifact_hash": str(index) * 64,
            "value": None if target_missing and index == 5 else value,
        }
        for index, value in enumerate(values, start=1)
    ]
    payload = {
        "decimal_places": 4,
        "factor_definition_ref": "volume-quality@v1",
        "mad_clip_multiplier": "3",
        "minimum_samples": 3,
        "normalization_id": "volume-quality-robust",
        "normalization_version": "v1",
        "points": points,
        "registry_id": "fcf-factor-registry",
        "registry_version": "v1",
        "schema_version": (
            "fcf-registered-factor-normalization-missing-state-runtime-v1"
        ),
        "series_id": "btc-volume-quality-series",
        "target_point_id": "factor-point-5",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_normalization_snapshot(*, target_missing: bool = False):
    content = build_reference_artifact_bytes(target_missing=target_missing)
    artifact = RegisteredNormalizationArtifact(
        artifact_id=(
            "registered-normalization-missing-v1"
            if target_missing
            else "registered-normalization-ready-v1"
        ),
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-06T00:00:00Z",
    )
    return normalize_registered_factor_series(
        content,
        artifact,
        build_reference_runtime_snapshot(),
        as_of_utc="2026-07-06T00:00:00Z",
    )


def render_normalization_snapshot_json(snapshot) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "evaluated_at_utc": snapshot.evaluated_at_utc,
            "evidence_hash": snapshot.evidence_hash,
            "factor_definition_ref": snapshot.factor_definition_ref,
            "metrics": dict(snapshot.metrics),
            "missing_state": snapshot.missing_state,
            "reason_codes": snapshot.reason_codes,
            "registry_snapshot_hash": snapshot.registry_snapshot_hash,
            "schema_version": snapshot.schema_version,
            "series_id": snapshot.series_id,
            "snapshot_hash": snapshot.snapshot_hash,
            "state": snapshot.state,
            "target_point_id": snapshot.target_point_id,
        },
        indent=2,
        sort_keys=True,
    )
