"""Governed version registry record schema."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    VERSION_KINDS,
    VERSION_STATUSES,
)

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_RECORD_FIELDS = (
    "registry_entry_id",
    "registry_entry_hash",
    "app_id",
    "record_kind",
    "record_status",
    "prompt_version",
    "model_version",
    "contract_version",
    "registry_version",
    "correlation_id",
    "research_run_id",
    "source_artifact_ids",
    "validation_baseline_id",
    "content_hash",
    "human_review_required",
    "archive_required",
    "model_execution_allowed",
    "automatic_activation_allowed",
    "automatic_promotion_allowed",
    "automatic_rollback_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
)

FORBIDDEN_ACTION_FIELDS = (
    "buy",
    "sell",
    "order",
    "execute",
    "position_size",
    "portfolio_action",
    "trade_instruction",
    "deployment_instruction",
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


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing_or_invalid_field:{field}")
    return value.strip()


def _require_sha256(value: Any, field: str) -> str:
    normalized = _require_text(value, field).lower()

    if SHA256_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"invalid_sha256:{field}")

    return normalized


def _normalize_artifact_ids(
    source_artifact_ids: Sequence[str],
) -> list[str]:
    if isinstance(source_artifact_ids, (str, bytes)):
        raise ValueError("invalid_source_artifact_ids")

    if not isinstance(source_artifact_ids, Sequence):
        raise ValueError("invalid_source_artifact_ids")

    normalized = [
        _require_text(item, "source_artifact_ids")
        for item in source_artifact_ids
    ]

    if not normalized:
        raise ValueError("empty_source_artifact_ids")

    if len(normalized) != len(set(normalized)):
        raise ValueError("duplicate_source_artifact_ids")

    return sorted(normalized)


def build_version_record(
    *,
    record_kind: str,
    record_status: str,
    prompt_version: str,
    model_version: str,
    contract_version: str,
    registry_version: str,
    correlation_id: str,
    research_run_id: str,
    source_artifact_ids: Sequence[str],
    validation_baseline_id: str,
    content_hash: str,
) -> dict[str, Any]:
    """Build one deterministic paper-only version registry record."""
    normalized_kind = _require_text(record_kind, "record_kind")
    normalized_status = _require_text(record_status, "record_status")

    if normalized_kind not in VERSION_KINDS:
        raise ValueError(f"unsupported_record_kind:{normalized_kind}")

    if normalized_status not in VERSION_STATUSES:
        raise ValueError(f"unsupported_record_status:{normalized_status}")

    record_basis = {
        "app_id": APP_ID,
        "record_kind": normalized_kind,
        "record_status": normalized_status,
        "prompt_version": _require_text(
            prompt_version,
            "prompt_version",
        ),
        "model_version": _require_text(
            model_version,
            "model_version",
        ),
        "contract_version": _require_text(
            contract_version,
            "contract_version",
        ),
        "registry_version": _require_text(
            registry_version,
            "registry_version",
        ),
        "correlation_id": _require_text(
            correlation_id,
            "correlation_id",
        ),
        "research_run_id": _require_text(
            research_run_id,
            "research_run_id",
        ),
        "source_artifact_ids": _normalize_artifact_ids(
            source_artifact_ids
        ),
        "validation_baseline_id": _require_text(
            validation_baseline_id,
            "validation_baseline_id",
        ),
        "content_hash": _require_sha256(
            content_hash,
            "content_hash",
        ),
    }

    registry_entry_hash = _canonical_hash(record_basis)

    return {
        "registry_entry_id": (
            f"version-entry-{registry_entry_hash[:20]}"
        ),
        "registry_entry_hash": registry_entry_hash,
        **record_basis,
        "schema_contract_version": CONTRACT_VERSION,
        "human_review_required": True,
        "archive_required": True,
        "model_execution_allowed": False,
        "automatic_activation_allowed": False,
        "automatic_promotion_allowed": False,
        "automatic_rollback_allowed": False,
        "credential_access_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
    }


def validate_version_record(
    record: Mapping[str, Any],
) -> list[str]:
    """Validate one registry record without modifying it."""
    if not isinstance(record, Mapping):
        return ["record_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_RECORD_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")

    if record.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if record.get("record_kind") not in VERSION_KINDS:
        errors.append("invalid_record_kind")

    if record.get("record_status") not in VERSION_STATUSES:
        errors.append("invalid_record_status")

    artifact_ids = record.get("source_artifact_ids")
    if not isinstance(artifact_ids, list) or not artifact_ids:
        errors.append("invalid_source_artifact_ids")

    content_hash = record.get("content_hash")
    if (
        not isinstance(content_hash, str)
        or SHA256_PATTERN.fullmatch(content_hash) is None
    ):
        errors.append("invalid_content_hash")

    entry_hash = record.get("registry_entry_hash")
    if (
        not isinstance(entry_hash, str)
        or SHA256_PATTERN.fullmatch(entry_hash) is None
    ):
        errors.append("invalid_registry_entry_hash")

    if record.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if record.get("archive_required") is not True:
        errors.append("archive_not_required")

    if record.get("model_execution_allowed") is not False:
        errors.append("model_execution_not_blocked")

    if record.get("automatic_activation_allowed") is not False:
        errors.append("automatic_activation_not_blocked")

    if record.get("automatic_promotion_allowed") is not False:
        errors.append("automatic_promotion_not_blocked")

    if record.get("automatic_rollback_allowed") is not False:
        errors.append("automatic_rollback_not_blocked")

    if record.get("real_trading_allowed") is not False:
        errors.append("real_trading_not_blocked")

    if record.get("real_execution_allowed") is not False:
        errors.append("real_execution_not_blocked")

    for field in FORBIDDEN_ACTION_FIELDS:
        if field in record:
            errors.append(f"forbidden_action_field:{field}")

    return errors
