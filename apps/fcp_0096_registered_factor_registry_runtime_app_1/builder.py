from __future__ import annotations

import hashlib
import json

from .contracts import RegisteredFactorArtifact, RegisteredFactorRuntimeSnapshot
from .runtime import load_registered_factor_registry


REFERENCE_OBSERVED_AT_UTC = "2026-07-23T12:00:00Z"


def build_reference_artifact_bytes() -> bytes:
    fields = {
        "asset_scopes": ["BTC"],
        "calculation_spec_hash": "1" * 64,
        "effective_at_utc": "2026-01-01T00:00:00Z",
        "family": "TECHNICAL",
        "input_field_ids": ["close"],
        "maximum_lookback": 20,
        "minimum_lookback": 1,
        "output_unit": "ratio",
        "source_type": "DETERMINISTIC_CODE",
    }
    payload = {
        "definitions": [
            {
                **fields,
                "dependency_factor_refs": [],
                "factor_id": "legacy-trend",
                "lifecycle": "RETIRED",
                "replacement_factor_ref": "trend-v2@v2",
                "retired_at_utc": "2026-06-01T00:00:00Z",
                "version": "v1",
            },
            {
                **fields,
                "dependency_factor_refs": ["legacy-trend@v1"],
                "factor_id": "trend-v2",
                "lifecycle": "RESEARCH",
                "replacement_factor_ref": None,
                "retired_at_utc": None,
                "version": "v2",
            },
            {
                **fields,
                "dependency_factor_refs": ["trend-v2@v2"],
                "factor_id": "trend-confirmation",
                "lifecycle": "RESEARCH",
                "replacement_factor_ref": None,
                "retired_at_utc": None,
                "version": "v1",
            },
            {
                **fields,
                "dependency_factor_refs": [],
                "factor_id": "volume-quality",
                "lifecycle": "RESEARCH",
                "replacement_factor_ref": None,
                "retired_at_utc": None,
                "version": "v1",
            },
        ],
        "registry_id": "fcf-factor-registry",
        "registry_version": "v1",
        "schema_version": "fcf-registered-factor-registry-runtime-v1",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_runtime_snapshot() -> RegisteredFactorRuntimeSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredFactorArtifact(
        artifact_id="registered-factor-registry-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-23T11:00:00Z",
    )
    return load_registered_factor_registry(
        content,
        artifact,
        observed_at_utc=REFERENCE_OBSERVED_AT_UTC,
    )


def render_runtime_snapshot_json(
    snapshot: RegisteredFactorRuntimeSnapshot,
) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "dependency_graph": dict(snapshot.dependency_graph),
            "invalidated_factor_refs": snapshot.invalidated_factor_refs,
            "observed_at_utc": snapshot.observed_at_utc,
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "record_hashes": dict(snapshot.record_hashes),
            "registry_id": snapshot.registry_id,
            "registry_version": snapshot.registry_version,
            "replacement_map": dict(snapshot.replacement_map),
            "retired_factor_refs": snapshot.retired_factor_refs,
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
            "topological_order": snapshot.topological_order,
        },
        indent=2,
        sort_keys=True,
    )
