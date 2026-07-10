"""Deterministic index for governed AI version records."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import APP_ID, CONTRACT_VERSION, VERSION_KINDS
from .version_record import validate_version_record

VERSION_FIELD_BY_KIND = {
    "PROMPT": "prompt_version",
    "MODEL": "model_version",
    "CONTRACT": "contract_version",
    "REGISTRY": "registry_version",
}

REQUIRED_INDEX_FIELDS = (
    "registry_index_id",
    "registry_index_hash",
    "app_id",
    "contract_version",
    "record_count",
    "registry_entry_ids",
    "version_keys",
    "kind_summary",
    "status_summary",
    "records",
    "human_review_required",
    "archive_required",
    "model_execution_allowed",
    "automatic_activation_allowed",
    "automatic_promotion_allowed",
    "automatic_rollback_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
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


def _version_key(record: Mapping[str, Any]) -> str:
    kind = str(record["record_kind"])
    version_field = VERSION_FIELD_BY_KIND[kind]
    version_value = str(record[version_field])

    return f"{kind}:{version_value}"


def build_registry_index(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic read-only index of governed records."""
    if isinstance(records, (str, bytes)) or not isinstance(
        records,
        Sequence,
    ):
        raise TypeError("records_must_be_sequence")

    if not records:
        raise ValueError("empty_registry_records")

    normalized: list[dict[str, Any]] = []

    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("invalid_registry_record")

        errors = validate_version_record(record)
        if errors:
            raise ValueError(
                "invalid_registry_record:"
                + ",".join(sorted(errors))
            )

        normalized.append(copy.deepcopy(dict(record)))

    normalized.sort(
        key=lambda item: str(item["registry_entry_id"])
    )

    registry_entry_ids = [
        str(record["registry_entry_id"])
        for record in normalized
    ]

    if len(registry_entry_ids) != len(set(registry_entry_ids)):
        raise ValueError("duplicate_registry_entry_id")

    version_keys = [
        _version_key(record)
        for record in normalized
    ]

    if len(version_keys) != len(set(version_keys)):
        raise ValueError("duplicate_version_key")

    kind_summary = dict(
        sorted(
            Counter(
                str(record["record_kind"])
                for record in normalized
            ).items()
        )
    )

    status_summary = dict(
        sorted(
            Counter(
                str(record["record_status"])
                for record in normalized
            ).items()
        )
    )

    index_basis = {
        "registry_entry_ids": registry_entry_ids,
        "registry_entry_hashes": [
            str(record["registry_entry_hash"])
            for record in normalized
        ],
        "version_keys": version_keys,
        "kind_summary": kind_summary,
        "status_summary": status_summary,
    }

    registry_index_hash = _canonical_hash(index_basis)

    return {
        "registry_index_id": (
            f"version-index-{registry_index_hash[:20]}"
        ),
        "registry_index_hash": registry_index_hash,
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "record_count": len(normalized),
        "registry_entry_ids": registry_entry_ids,
        "version_keys": version_keys,
        "kind_summary": kind_summary,
        "status_summary": status_summary,
        "records": normalized,
        "human_review_required": True,
        "archive_required": True,
        "model_execution_allowed": False,
        "automatic_activation_allowed": False,
        "automatic_promotion_allowed": False,
        "automatic_rollback_allowed": False,
        "source_mutation_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
    }


def validate_registry_index(
    index: Mapping[str, Any],
) -> list[str]:
    """Validate an index without modifying it."""
    if not isinstance(index, Mapping):
        return ["index_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_INDEX_FIELDS:
        if field not in index:
            errors.append(f"missing_field:{field}")

    if index.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if index.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    records = index.get("records")
    if not isinstance(records, list) or not records:
        errors.append("invalid_records")
        records = []

    if index.get("record_count") != len(records):
        errors.append("record_count_mismatch")

    entry_ids = index.get("registry_entry_ids")
    if not isinstance(entry_ids, list):
        errors.append("invalid_registry_entry_ids")
    elif len(entry_ids) != len(set(entry_ids)):
        errors.append("duplicate_registry_entry_id")

    version_keys = index.get("version_keys")
    if not isinstance(version_keys, list):
        errors.append("invalid_version_keys")
    elif len(version_keys) != len(set(version_keys)):
        errors.append("duplicate_version_key")

    kind_summary = index.get("kind_summary")
    if not isinstance(kind_summary, Mapping):
        errors.append("invalid_kind_summary")
    else:
        for kind in kind_summary:
            if kind not in VERSION_KINDS:
                errors.append(f"invalid_kind_summary_key:{kind}")

    if index.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if index.get("archive_required") is not True:
        errors.append("archive_not_required")

    if index.get("model_execution_allowed") is not False:
        errors.append("model_execution_not_blocked")

    if index.get("automatic_activation_allowed") is not False:
        errors.append("automatic_activation_not_blocked")

    if index.get("automatic_promotion_allowed") is not False:
        errors.append("automatic_promotion_not_blocked")

    if index.get("automatic_rollback_allowed") is not False:
        errors.append("automatic_rollback_not_blocked")

    if index.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if index.get("real_trading_allowed") is not False:
        errors.append("real_trading_not_blocked")

    if index.get("real_execution_allowed") is not False:
        errors.append("real_execution_not_blocked")

    return errors


def get_record_by_id(
    index: Mapping[str, Any],
    registry_entry_id: str,
) -> dict[str, Any] | None:
    """Return a copied record by registry entry identifier."""
    if not isinstance(registry_entry_id, str) or not (
        registry_entry_id.strip()
    ):
        raise ValueError("invalid_registry_entry_id")

    records = index.get("records")
    if not isinstance(records, list):
        raise ValueError("invalid_registry_index")

    for record in records:
        if record.get("registry_entry_id") == (
            registry_entry_id.strip()
        ):
            return copy.deepcopy(dict(record))

    return None


def get_records_by_kind(
    index: Mapping[str, Any],
    record_kind: str,
) -> list[dict[str, Any]]:
    """Return copied registry records for one governed kind."""
    if record_kind not in VERSION_KINDS:
        raise ValueError(f"unsupported_record_kind:{record_kind}")

    records = index.get("records")
    if not isinstance(records, list):
        raise ValueError("invalid_registry_index")

    return [
        copy.deepcopy(dict(record))
        for record in records
        if record.get("record_kind") == record_kind
    ]
