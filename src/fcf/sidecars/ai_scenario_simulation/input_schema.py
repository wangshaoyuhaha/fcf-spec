"""Registered input and assumption schemas for scenario simulation."""

from datetime import datetime, timedelta
import re
from typing import Any, Mapping, Sequence

from .contract import REQUIRED_FALSE_FLAGS, REQUIRED_TRUE_FLAGS


SCHEMA_VERSION = "1.0.0"
STAGE_ID = "AI-SCENARIO-SIMULATION-D2"

SOURCE_ARTIFACT_TYPES = (
    "REGISTERED_MARKET_SCENARIO_DEFINITION",
    "REGISTERED_MARKET_SCENARIO_ASSUMPTION",
    "REGISTERED_MARKET_SCENARIO_RISK_CONTEXT",
    "REGISTERED_MARKET_NARRATIVE_ASSESSMENT",
    "REGISTERED_AI_CONTEXT_ARTIFACT",
    "REGISTERED_CONTRARIAN_CHALLENGE_ARTIFACT",
)

SOURCE_REVIEW_STATUSES = (
    "REGISTERED",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

BUNDLE_STATUSES = (
    "READY_FOR_BRANCH_CONSTRUCTION",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

TRUTH_STATUS = "UNDETERMINED"

REQUIRED_INPUT_FIELDS = (
    "record_id",
    "source_scenario_id",
    "source_artifact_id",
    "source_artifact_type",
    "source_artifact_version",
    "registered_at_utc",
    "scenario_label",
    "assumption_ids",
    "evidence_references",
    "risk_flags",
    "source_review_status",
    "operator_review_status",
    "truth_status",
    "original_conclusion_reference",
    "safety_flags",
)

REQUIRED_BUNDLE_FIELDS = (
    "bundle_id",
    "scenario_input_record_id",
    "source_scenario_id",
    "assumption_ids",
    "evidence_references",
    "risk_flags",
    "bundle_status",
    "operator_review_status",
    "truth_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _canonical_strings(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


def build_scenario_input_record(
    *,
    record_id: str,
    source_scenario_id: str,
    source_artifact_id: str,
    source_artifact_type: str,
    source_artifact_version: str,
    registered_at_utc: str,
    scenario_label: str,
    assumption_ids: Sequence[str],
    evidence_references: Sequence[str],
    risk_flags: Sequence[str],
    source_review_status: str,
    original_conclusion_reference: str,
) -> dict[str, Any]:
    """Build a deterministic registered scenario simulation input."""
    return {
        "record_id": record_id,
        "source_scenario_id": source_scenario_id,
        "source_artifact_id": source_artifact_id,
        "source_artifact_type": source_artifact_type,
        "source_artifact_version": source_artifact_version,
        "registered_at_utc": registered_at_utc,
        "scenario_label": scenario_label,
        "assumption_ids": _canonical_strings(assumption_ids),
        "evidence_references": _canonical_strings(
            evidence_references
        ),
        "risk_flags": _canonical_strings(risk_flags),
        "source_review_status": source_review_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": TRUTH_STATUS,
        "original_conclusion_reference": (
            original_conclusion_reference
        ),
        "safety_flags": _safety_flags(),
    }


def build_scenario_assumption_bundle(
    *,
    bundle_id: str,
    scenario_input_record_id: str,
    source_scenario_id: str,
    assumption_ids: Sequence[str],
    evidence_references: Sequence[str],
    risk_flags: Sequence[str],
    bundle_status: str,
) -> dict[str, Any]:
    """Build a deterministic assumption bundle without inference."""
    return {
        "bundle_id": bundle_id,
        "scenario_input_record_id": scenario_input_record_id,
        "source_scenario_id": source_scenario_id,
        "assumption_ids": _canonical_strings(assumption_ids),
        "evidence_references": _canonical_strings(
            evidence_references
        ),
        "risk_flags": _canonical_strings(risk_flags),
        "bundle_status": bundle_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": TRUTH_STATUS,
        "safety_flags": _safety_flags(),
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return False

    return parsed.utcoffset() == timedelta(0)


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item.strip()
        for item in value
    ):
        return False

    return value == sorted(set(value))


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )
    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def validate_scenario_input_record(
    record: object,
) -> list[str]:
    """Return deterministic registered-input validation errors."""
    if not isinstance(record, Mapping):
        return ["record_must_be_mapping"]

    errors: list[str] = []

    if set(record.keys()) != set(REQUIRED_INPUT_FIELDS):
        errors.append("record_fields_must_match_schema")

    for field in (
        "record_id",
        "source_scenario_id",
        "source_artifact_id",
    ):
        if not _valid_identifier(record.get(field)):
            errors.append(f"{field}_invalid")

    for field in (
        "source_artifact_version",
        "scenario_label",
        "original_conclusion_reference",
    ):
        if not _valid_non_empty_string(record.get(field)):
            errors.append(f"{field}_invalid")

    if record.get("source_artifact_type") not in (
        SOURCE_ARTIFACT_TYPES
    ):
        errors.append("source_artifact_type_invalid")

    if not _valid_utc_timestamp(
        record.get("registered_at_utc")
    ):
        errors.append("registered_at_utc_invalid")

    for field in (
        "assumption_ids",
        "evidence_references",
        "risk_flags",
    ):
        if not _valid_canonical_string_list(record.get(field)):
            errors.append(f"{field}_invalid")

    if record.get("source_review_status") not in (
        SOURCE_REVIEW_STATUSES
    ):
        errors.append("source_review_status_invalid")

    if record.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if record.get("truth_status") != TRUTH_STATUS:
        errors.append("truth_status_must_remain_undetermined")

    errors.extend(
        _validate_safety_flags(record.get("safety_flags"))
    )

    return errors


def validate_scenario_assumption_bundle(
    bundle: object,
) -> list[str]:
    """Return deterministic assumption-bundle validation errors."""
    if not isinstance(bundle, Mapping):
        return ["bundle_must_be_mapping"]

    errors: list[str] = []

    if set(bundle.keys()) != set(REQUIRED_BUNDLE_FIELDS):
        errors.append("bundle_fields_must_match_schema")

    for field in (
        "bundle_id",
        "scenario_input_record_id",
        "source_scenario_id",
    ):
        if not _valid_identifier(bundle.get(field)):
            errors.append(f"{field}_invalid")

    for field in (
        "assumption_ids",
        "evidence_references",
        "risk_flags",
    ):
        if not _valid_canonical_string_list(bundle.get(field)):
            errors.append(f"{field}_invalid")

    if bundle.get("bundle_status") not in BUNDLE_STATUSES:
        errors.append("bundle_status_invalid")

    if bundle.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if bundle.get("truth_status") != TRUTH_STATUS:
        errors.append("truth_status_must_remain_undetermined")

    errors.extend(
        _validate_safety_flags(bundle.get("safety_flags"))
    )

    return errors
