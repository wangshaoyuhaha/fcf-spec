from __future__ import annotations

import hashlib
import json

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (
    RegisteredFactorArtifact,
    load_registered_factor_registry,
)

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredVolumeFlowArtifact,
    RegisteredVolumeFlowSnapshot,
)
from .runtime import (
    SUCCESSOR_KIND_SOURCES,
    calculate_registered_volume_flow_indicators,
)


REFERENCE_AS_OF_UTC = "2026-07-24T06:30:00Z"


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
                "input_field_ids": ["amount", "close", "high", "low", "volume"],
                "lifecycle": "RESEARCH",
                "maximum_lookback": 10000,
                "minimum_lookback": 2,
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
            "registry_version": "v2",
            "schema_version": "fcf-registered-factor-registry-runtime-v1",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def build_reference_registry_snapshot():
    content = build_reference_registry_artifact_bytes()
    artifact = RegisteredFactorArtifact(
        artifact_id="registered-technical-indicator-registry-v2",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T06:00:00Z",
    )
    return load_registered_factor_registry(
        content,
        artifact,
        observed_at_utc=REFERENCE_AS_OF_UTC,
    )


def build_reference_artifact_bytes() -> bytes:
    bars = [
        ("2026-07-20T07:00:00Z", "10", "8", "9", "100", "900", False),
        ("2026-07-21T07:00:00Z", "11", "9", "10", "120", "1200", False),
        ("2026-07-22T07:00:00Z", "10", "8", "9", "80", "720", False),
        ("2026-07-23T07:00:00Z", "9", "9", "9", "0", "0", True),
        ("2026-07-24T06:00:00Z", "12", "10", "11", "150", "1650", False),
    ]
    requests = [
        {
            "factor_ref": f"mfi@{_factor_version('MFI')}",
            "indicator_kind": "MFI",
            "request_id": "registered-mfi-3",
            "suspension_policy": "EXCLUDE",
            "window": 3,
        },
        {
            "factor_ref": f"obv@{_factor_version('OBV')}",
            "indicator_kind": "OBV",
            "request_id": "registered-obv-3",
            "suspension_policy": "EXCLUDE",
            "window": 3,
        },
        {
            "factor_ref": (
                "volume-price-trend@"
                f"{_factor_version('VOLUME_PRICE_TREND')}"
            ),
            "indicator_kind": "VOLUME_PRICE_TREND",
            "request_id": "registered-volume-price-trend-3",
            "suspension_policy": "EXCLUDE",
            "window": 3,
        },
    ]
    return json.dumps(
        {
            "amount_currency": "CNY",
            "bars": [
                {
                    "amount": amount,
                    "close": close,
                    "high": high,
                    "is_suspended": suspended,
                    "low": low,
                    "timestamp_utc": timestamp,
                    "volume": volume,
                }
                for timestamp, high, low, close, volume, amount, suspended in bars
            ],
            "catalog_id": "fcf-technical-indicator-catalog",
            "catalog_version": "v2",
            "dataset_id": "registered-volume-flow-reference",
            "dataset_version": "v1",
            "indicator_requests": requests,
            "registry_id": "fcf-technical-indicator-registry",
            "registry_version": "v2",
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "volume_unit": "SHARES",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def build_reference_volume_flow_snapshot() -> RegisteredVolumeFlowSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredVolumeFlowArtifact(
        artifact_id="registered-volume-flow-reference-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T06:10:00Z",
    )
    return calculate_registered_volume_flow_indicators(
        content,
        artifact,
        build_reference_registry_snapshot(),
        as_of_utc=REFERENCE_AS_OF_UTC,
    )


def render_volume_flow_snapshot_json(
    snapshot: RegisteredVolumeFlowSnapshot,
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
