from __future__ import annotations

import hashlib
import json

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (
    RegisteredFactorArtifact,
    load_registered_factor_registry,
)

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredIndicatorCatalogArtifact,
    RegisteredIndicatorCatalogSnapshot,
)
from .runtime import FOUNDATION_KIND_SOURCES, load_registered_indicator_catalog


REFERENCE_OBSERVED_AT_UTC = "2026-07-24T05:30:00Z"


def _factor_id(kind: str) -> str:
    return kind.lower().replace("_", "-")


def build_reference_registry_artifact_bytes() -> bytes:
    definitions = []
    for index, kind in enumerate(sorted(FOUNDATION_KIND_SOURCES), start=1):
        definitions.append(
            {
                "asset_scopes": ["A-SHARE", "BTC"],
                "calculation_spec_hash": hashlib.sha256(kind.encode("ascii")).hexdigest(),
                "dependency_factor_refs": [],
                "effective_at_utc": "2026-01-01T00:00:00Z",
                "factor_id": _factor_id(kind),
                "family": "TECHNICAL",
                "input_field_ids": ["amount", "close", "high", "low", "open", "volume"],
                "lifecycle": "RESEARCH",
                "maximum_lookback": 5000,
                "minimum_lookback": 1,
                "output_unit": "indicator",
                "replacement_factor_ref": None,
                "retired_at_utc": None,
                "source_type": "DETERMINISTIC_CODE",
                "version": f"v{index}",
            }
        )
    return json.dumps(
        {
            "definitions": definitions,
            "registry_id": "fcf-technical-indicator-registry",
            "registry_version": "v1",
            "schema_version": "fcf-registered-factor-registry-runtime-v1",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def build_reference_registry_snapshot():
    content = build_reference_registry_artifact_bytes()
    artifact = RegisteredFactorArtifact(
        artifact_id="registered-technical-indicator-registry-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T05:00:00Z",
    )
    return load_registered_factor_registry(
        content,
        artifact,
        observed_at_utc=REFERENCE_OBSERVED_AT_UTC,
    )


def build_reference_artifact_bytes() -> bytes:
    entries = []
    for index, (kind, foundation) in enumerate(
        sorted(FOUNDATION_KIND_SOURCES.items()),
        start=1,
    ):
        entries.append(
            {
                "factor_ref": f"{_factor_id(kind)}@v{index}",
                "foundation_ref": foundation,
                "indicator_kind": kind,
            }
        )
    return json.dumps(
        {
            "catalog_id": "fcf-technical-indicator-catalog",
            "catalog_version": "v1",
            "entries": entries,
            "registry_id": "fcf-technical-indicator-registry",
            "registry_version": "v1",
            "schema_version": RUNTIME_SCHEMA_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def build_reference_catalog_snapshot() -> RegisteredIndicatorCatalogSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredIndicatorCatalogArtifact(
        artifact_id="registered-technical-indicator-catalog-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T05:10:00Z",
    )
    return load_registered_indicator_catalog(
        content,
        artifact,
        build_reference_registry_snapshot(),
        observed_at_utc=REFERENCE_OBSERVED_AT_UTC,
    )


def render_catalog_snapshot_json(snapshot: RegisteredIndicatorCatalogSnapshot) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "catalog_id": snapshot.catalog_id,
            "catalog_version": snapshot.catalog_version,
            "factor_refs": dict(snapshot.factor_refs),
            "missing_candidate_kinds": snapshot.missing_candidate_kinds,
            "observed_at_utc": snapshot.observed_at_utc,
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "reason_codes": snapshot.reason_codes,
            "registry_id": snapshot.registry_id,
            "registry_snapshot_hash": snapshot.registry_snapshot_hash,
            "registry_version": snapshot.registry_version,
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
            "state": snapshot.state,
            "supported_kind_sources": dict(snapshot.supported_kind_sources),
        },
        indent=2,
        sort_keys=True,
    )
