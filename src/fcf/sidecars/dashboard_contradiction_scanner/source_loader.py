"""Read-only governed source loader for dashboard contradiction scanning."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import ALLOWED_SOURCE_TYPES

REQUIRED_SOURCE_FIELDS = (
    "artifact_id",
    "artifact_type",
    "correlation_id",
    "research_run_id",
    "validation_baseline_id",
)

LIST_FIELDS = (
    "source_artifact_ids",
    "risk_flags",
    "reason_codes",
)

STATE_FIELDS = (
    "validation_state",
    "review_state",
    "lifecycle_state",
    "archive_state",
)


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _require_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing_or_invalid_field:{field}")
    return value.strip()


def _normalize_list(record: Mapping[str, Any], field: str) -> list[str]:
    value = record.get(field, [])

    if not isinstance(value, list):
        raise ValueError(f"invalid_list_field:{field}")

    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"invalid_list_item:{field}")
        normalized.append(item.strip())

    return normalized


def load_source_record(source: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and copy one governed source without mutating the input."""
    if not isinstance(source, Mapping):
        raise TypeError("source_must_be_mapping")

    original = copy.deepcopy(dict(source))

    normalized: dict[str, Any] = {}
    for field in REQUIRED_SOURCE_FIELDS:
        normalized[field] = _require_text(original, field)

    if normalized["artifact_type"] not in ALLOWED_SOURCE_TYPES:
        raise ValueError(
            f"unsupported_artifact_type:{normalized['artifact_type']}"
        )

    for field in LIST_FIELDS:
        normalized[field] = _normalize_list(original, field)

    for field in STATE_FIELDS:
        value = original.get(field)
        normalized[field] = (
            value.strip()
            if isinstance(value, str) and value.strip()
            else "UNKNOWN"
        )

    summary = original.get("summary")
    if summary is not None and not isinstance(summary, str):
        raise ValueError("invalid_summary")

    normalized["summary"] = summary.strip() if isinstance(summary, str) else ""
    normalized["source_payload"] = original
    normalized["source_record_hash"] = _canonical_hash(original)
    normalized["read_only"] = True
    normalized["operator_review_required"] = True

    return normalized


def build_source_manifest(
    sources: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic read-only manifest from governed sources."""
    if isinstance(sources, (str, bytes)) or not isinstance(sources, Sequence):
        raise TypeError("sources_must_be_sequence")

    loaded = [load_source_record(source) for source in sources]
    loaded.sort(key=lambda item: item["artifact_id"])

    artifact_ids = [item["artifact_id"] for item in loaded]
    if len(artifact_ids) != len(set(artifact_ids)):
        raise ValueError("duplicate_artifact_id")

    manifest_basis = {
        "artifact_ids": artifact_ids,
        "source_record_hashes": [
            item["source_record_hash"] for item in loaded
        ],
    }

    return {
        "source_count": len(loaded),
        "artifact_ids": artifact_ids,
        "sources": loaded,
        "manifest_hash": _canonical_hash(manifest_basis),
        "read_only": True,
        "operator_review_required": True,
    }
