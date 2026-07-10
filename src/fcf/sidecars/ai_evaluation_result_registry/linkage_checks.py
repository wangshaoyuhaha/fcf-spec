"""Sample-result linkage and integrity checks."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    validate_evaluation_sample_registry,
)

from .contract import APP_ID
from .registry_index import (
    validate_evaluation_result_registry,
)


LINKAGE_STAGE_ID = "AI-EVALUATION-RESULT-REGISTRY-D4"
LINKAGE_SCHEMA_VERSION = "1.0.0"

LINKAGE_STATUSES = (
    "PASS",
    "REVIEW_REQUIRED",
    "FAIL",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "imported_artifacts_only",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "automatic_evaluation_acceptance_allowed",
    "source_artifact_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "news_feed_connection_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
)


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(_valid_string(item) for item in value)
    )


def _valid_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return False

    return (
        parsed.tzinfo is not None
        and parsed.utcoffset() is not None
        and parsed.utcoffset().total_seconds() == 0
    )


def _safe_entries(registry: Mapping[str, Any]) -> list[Any]:
    entries = registry.get("entries", [])

    if isinstance(entries, list):
        return entries

    return []


def _derive_linkage_status(
    *,
    source_validation_errors: list[str],
    unknown_sample_keys: list[str],
    dimension_mismatch_result_keys: list[str],
    samples_without_results: list[str],
    duplicate_output_sha256: list[str],
    result_status_counts: Mapping[str, Any],
) -> str:
    if (
        source_validation_errors
        or unknown_sample_keys
        or dimension_mismatch_result_keys
    ):
        return "FAIL"

    review_status_total = sum(
        int(result_status_counts.get(status, 0))
        for status in (
            "REVIEW_REQUIRED",
            "INVALID",
            "BLOCKED",
        )
        if isinstance(result_status_counts.get(status, 0), int)
        and not isinstance(
            result_status_counts.get(status, 0),
            bool,
        )
    )

    if (
        samples_without_results
        or duplicate_output_sha256
        or review_status_total > 0
    ):
        return "REVIEW_REQUIRED"

    return "PASS"


def build_sample_result_linkage_report(
    *,
    report_id: str,
    sample_registry: Mapping[str, Any],
    result_registry: Mapping[str, Any],
    created_at_utc: str,
) -> dict[str, Any]:
    """Build deterministic sample-result linkage checks."""

    sample_errors = validate_evaluation_sample_registry(
        sample_registry
    )
    result_errors = validate_evaluation_result_registry(
        result_registry
    )

    source_validation_errors = [
        f"sample_registry:{error}"
        for error in sample_errors
    ]
    source_validation_errors.extend(
        f"result_registry:{error}"
        for error in result_errors
    )

    sample_entries = _safe_entries(sample_registry)
    result_entries = _safe_entries(result_registry)

    sample_by_key: dict[str, Mapping[str, Any]] = {}

    for entry in sample_entries:
        if not isinstance(entry, Mapping):
            continue

        sample_key = entry.get("sample_key")

        if _valid_string(sample_key):
            sample_by_key[str(sample_key)] = entry

    known_sample_keys = sorted(sample_by_key)

    result_sample_keys: list[str] = []
    unknown_sample_keys: list[str] = []
    dimension_mismatch_result_keys: list[str] = []
    linked_result_keys: list[str] = []
    output_hashes: list[str] = []

    for index, entry in enumerate(result_entries):
        if not isinstance(entry, Mapping):
            continue

        result_key = entry.get("result_key")
        sample_key = entry.get("sample_key")
        output_sha256 = entry.get("imported_output_sha256")

        if _valid_string(output_sha256):
            output_hashes.append(str(output_sha256))

        if not _valid_string(sample_key):
            continue

        normalized_sample_key = str(sample_key)
        result_sample_keys.append(normalized_sample_key)

        if normalized_sample_key not in sample_by_key:
            unknown_sample_keys.append(normalized_sample_key)
            continue

        if _valid_string(result_key):
            linked_result_keys.append(str(result_key))
        else:
            linked_result_keys.append(
                f"invalid-result-{index}"
            )

        sample_dimension = sample_by_key[
            normalized_sample_key
        ].get("evaluation_dimension")

        result_dimension = entry.get("evaluation_dimension")

        if sample_dimension != result_dimension:
            if _valid_string(result_key):
                dimension_mismatch_result_keys.append(
                    str(result_key)
                )
            else:
                dimension_mismatch_result_keys.append(
                    f"invalid-result-{index}"
                )

    samples_without_results = sorted(
        set(known_sample_keys) - set(result_sample_keys)
    )

    output_hash_counts = Counter(output_hashes)

    duplicate_output_sha256 = sorted(
        output_hash
        for output_hash, count in output_hash_counts.items()
        if count > 1
    )

    result_status_counts = result_registry.get(
        "status_counts",
        {},
    )

    if not isinstance(result_status_counts, Mapping):
        result_status_counts = {}

    result_status_counts_copy = {
        str(key): value
        for key, value in result_status_counts.items()
    }

    linkage_status = _derive_linkage_status(
        source_validation_errors=source_validation_errors,
        unknown_sample_keys=sorted(
            set(unknown_sample_keys)
        ),
        dimension_mismatch_result_keys=sorted(
            set(dimension_mismatch_result_keys)
        ),
        samples_without_results=samples_without_results,
        duplicate_output_sha256=duplicate_output_sha256,
        result_status_counts=result_status_counts_copy,
    )

    return {
        "app_id": APP_ID,
        "stage_id": LINKAGE_STAGE_ID,
        "schema_version": LINKAGE_SCHEMA_VERSION,
        "report_id": report_id,
        "created_at_utc": created_at_utc,
        "source_sample_registry_id": sample_registry.get(
            "registry_id"
        ),
        "source_result_registry_id": result_registry.get(
            "registry_id"
        ),
        "sample_count": len(known_sample_keys),
        "result_count": len(result_entries),
        "linked_result_count": len(linked_result_keys),
        "known_sample_keys": known_sample_keys,
        "linked_result_keys": sorted(linked_result_keys),
        "unknown_sample_keys": sorted(
            set(unknown_sample_keys)
        ),
        "samples_without_results": samples_without_results,
        "dimension_mismatch_result_keys": sorted(
            set(dimension_mismatch_result_keys)
        ),
        "duplicate_output_sha256": duplicate_output_sha256,
        "result_status_counts": result_status_counts_copy,
        "source_validation_errors": source_validation_errors,
        "linkage_status": linkage_status,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "imported_artifacts_only": True,
        "operator_review_bypass_allowed": False,
        "automatic_evaluation_acceptance_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "news_feed_connection_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def _expected_linkage_status(
    report: Mapping[str, Any],
) -> str:
    raw_status_counts = report.get(
        "result_status_counts",
        {},
    )

    status_counts = (
        raw_status_counts
        if isinstance(raw_status_counts, Mapping)
        else {}
    )

    return _derive_linkage_status(
        source_validation_errors=list(
            report.get("source_validation_errors", [])
        )
        if isinstance(
            report.get("source_validation_errors"),
            list,
        )
        else ["invalid_source_validation_errors"],
        unknown_sample_keys=list(
            report.get("unknown_sample_keys", [])
        )
        if isinstance(
            report.get("unknown_sample_keys"),
            list,
        )
        else ["invalid_unknown_sample_keys"],
        dimension_mismatch_result_keys=list(
            report.get(
                "dimension_mismatch_result_keys",
                [],
            )
        )
        if isinstance(
            report.get("dimension_mismatch_result_keys"),
            list,
        )
        else ["invalid_dimension_mismatch_result_keys"],
        samples_without_results=list(
            report.get("samples_without_results", [])
        )
        if isinstance(
            report.get("samples_without_results"),
            list,
        )
        else ["invalid_samples_without_results"],
        duplicate_output_sha256=list(
            report.get("duplicate_output_sha256", [])
        )
        if isinstance(
            report.get("duplicate_output_sha256"),
            list,
        )
        else ["invalid_duplicate_output_sha256"],
        result_status_counts=status_counts,
    )


def validate_sample_result_linkage_report(
    report: Mapping[str, Any],
) -> list[str]:
    """Return deterministic linkage report validation errors."""

    if not isinstance(report, Mapping):
        return ["report_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": LINKAGE_STAGE_ID,
        "schema_version": LINKAGE_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if report.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in (
        "report_id",
        "source_sample_registry_id",
        "source_result_registry_id",
    ):
        if not _valid_string(report.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_utc_timestamp(
        report.get("created_at_utc")
    ):
        errors.append("created_at_utc_invalid")

    for field in (
        "sample_count",
        "result_count",
        "linked_result_count",
    ):
        value = report.get(field)

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            errors.append(f"{field}_invalid")

    list_fields = (
        "known_sample_keys",
        "linked_result_keys",
        "unknown_sample_keys",
        "samples_without_results",
        "dimension_mismatch_result_keys",
        "duplicate_output_sha256",
        "source_validation_errors",
    )

    for field in list_fields:
        if not _valid_string_list(report.get(field)):
            errors.append(f"{field}_invalid")

    known_sample_keys = report.get("known_sample_keys")
    linked_result_keys = report.get("linked_result_keys")

    if (
        isinstance(known_sample_keys, list)
        and isinstance(report.get("sample_count"), int)
        and not isinstance(report.get("sample_count"), bool)
        and report.get("sample_count")
        != len(known_sample_keys)
    ):
        errors.append("sample_count_mismatch")

    if (
        isinstance(linked_result_keys, list)
        and isinstance(
            report.get("linked_result_count"),
            int,
        )
        and not isinstance(
            report.get("linked_result_count"),
            bool,
        )
        and report.get("linked_result_count")
        != len(linked_result_keys)
    ):
        errors.append("linked_result_count_mismatch")

    status_counts = report.get("result_status_counts")

    if not isinstance(status_counts, Mapping):
        errors.append("result_status_counts_invalid")
    else:
        for value in status_counts.values():
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append(
                    "result_status_count_value_invalid"
                )
                break

    linkage_status = report.get("linkage_status")

    if linkage_status not in LINKAGE_STATUSES:
        errors.append("linkage_status_invalid")
    elif linkage_status != _expected_linkage_status(report):
        errors.append("linkage_status_mismatch")

    for field in REQUIRED_TRUE_FLAGS:
        if report.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors