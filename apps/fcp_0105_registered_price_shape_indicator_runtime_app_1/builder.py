from __future__ import annotations

import hashlib
import json

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (
    RegisteredFactorArtifact,
    load_registered_factor_registry,
)

from .contracts import (
    INDICATOR_KINDS,
    RUNTIME_SCHEMA_VERSION,
    RegisteredPriceShapeArtifact,
    RegisteredPriceShapeSnapshot,
)
from .runtime import (
    SUCCESSOR_KIND_SOURCES,
    calculate_registered_price_shape_indicators,
)


REFERENCE_AS_OF_UTC = "2026-07-24T07:30:00Z"


def _factor_id(kind: str) -> str:
    return kind.lower().replace("_", "-")


def _factor_version(kind: str) -> str:
    return f"v{sorted(SUCCESSOR_KIND_SOURCES).index(kind) + 1}"


def build_reference_registry_artifact_bytes() -> bytes:
    definitions = []
    for index, kind in enumerate(sorted(SUCCESSOR_KIND_SOURCES), start=1):
        definitions.append(
            {
                "asset_scopes": ["A-SHARE", "BTC"],
                "calculation_spec_hash": hashlib.sha256(kind.encode("ascii")).hexdigest(),
                "dependency_factor_refs": [],
                "effective_at_utc": "2026-01-01T00:00:00Z",
                "factor_id": _factor_id(kind),
                "family": "TECHNICAL",
                "input_field_ids": ["close", "is_suspended", "timestamp_utc"],
                "lifecycle": "RESEARCH",
                "maximum_lookback": 10000,
                "minimum_lookback": 3,
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
            "registry_version": "v3",
            "schema_version": "fcf-registered-factor-registry-runtime-v1",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def build_reference_registry_snapshot():
    content = build_reference_registry_artifact_bytes()
    artifact = RegisteredFactorArtifact(
        artifact_id="registered-technical-indicator-registry-v3",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T07:00:00Z",
    )
    return load_registered_factor_registry(
        content,
        artifact,
        observed_at_utc=REFERENCE_AS_OF_UTC,
    )


def build_reference_artifact_bytes() -> bytes:
    bars = [
        ("2026-07-19T07:00:00Z", "10", False),
        ("2026-07-20T07:00:00Z", "12", False),
        ("2026-07-21T07:00:00Z", "11", False),
        ("2026-07-22T07:00:00Z", "13", False),
        ("2026-07-23T07:00:00Z", "99", True),
        ("2026-07-24T07:00:00Z", "15", False),
    ]
    requests = [
        {
            "factor_ref": f"{_factor_id(kind)}@{_factor_version(kind)}",
            "indicator_kind": kind,
            "request_id": f"registered-{_factor_id(kind)}-3",
            "suspension_policy": "EXCLUDE",
            "window": 3,
        }
        for kind in INDICATOR_KINDS
    ]
    requests.sort(key=lambda item: item["request_id"])
    return json.dumps(
        {
            "bars": [
                {
                    "close": close,
                    "is_suspended": suspended,
                    "timestamp_utc": timestamp,
                }
                for timestamp, close, suspended in bars
            ],
            "catalog_id": "fcf-technical-indicator-catalog",
            "catalog_version": "v3",
            "dataset_id": "registered-price-shape-reference",
            "dataset_version": "v1",
            "indicator_requests": requests,
            "price_currency": "CNY",
            "registry_id": "fcf-technical-indicator-registry",
            "registry_version": "v3",
            "schema_version": RUNTIME_SCHEMA_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def build_reference_price_shape_snapshot() -> RegisteredPriceShapeSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredPriceShapeArtifact(
        artifact_id="registered-price-shape-reference-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T07:10:00Z",
    )
    return calculate_registered_price_shape_indicators(
        content,
        artifact,
        build_reference_registry_snapshot(),
        as_of_utc=REFERENCE_AS_OF_UTC,
    )


def render_price_shape_snapshot_json(
    snapshot: RegisteredPriceShapeSnapshot,
) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "as_of_utc": snapshot.as_of_utc,
            "catalog_id": snapshot.catalog_id,
            "catalog_version": snapshot.catalog_version,
            "dataset_id": snapshot.dataset_id,
            "dataset_version": snapshot.dataset_version,
            "missing_candidate_kinds": snapshot.missing_candidate_kinds,
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "registry_id": snapshot.registry_id,
            "registry_snapshot_hash": snapshot.registry_snapshot_hash,
            "registry_version": snapshot.registry_version,
            "result_hashes": dict(snapshot.result_hashes),
            "result_values": {
                key: dict(value) for key, value in snapshot.result_values.items()
            },
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
            "source_last_timestamp_utc": snapshot.source_last_timestamp_utc,
            "supported_kind_sources": dict(snapshot.supported_kind_sources),
        },
        indent=2,
        sort_keys=True,
    )
