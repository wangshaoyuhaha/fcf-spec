"""Deterministic scenario branch construction."""

import re
from typing import Any, Mapping

from .contract import REQUIRED_FALSE_FLAGS, REQUIRED_TRUE_FLAGS
from .input_schema import (
    validate_scenario_assumption_bundle,
    validate_scenario_input_record,
)


STAGE_ID = "AI-SCENARIO-SIMULATION-D3"
BRANCH_SCHEMA_VERSION = "1.0.0"

BRANCH_STATUSES = (
    "READY_FOR_ASSESSMENT",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

TRUTH_STATUS = "UNDETERMINED"
PROBABILITY_STATUS = "NOT_ASSIGNED"
RANK_STATUS = "NOT_ASSIGNED"
WINNER_STATUS = "NOT_SELECTED"

REQUIRED_BRANCH_FIELDS = (
    "branch_id",
    "scenario_input_record_id",
    "assumption_bundle_id",
    "source_scenario_id",
    "branch_label",
    "assumption_ids",
    "evidence_references",
    "risk_flags",
    "source_review_status",
    "bundle_status",
    "branch_status",
    "operator_review_status",
    "truth_status",
    "probability_status",
    "rank_status",
    "winner_status",
    "original_conclusion_reference",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class ScenarioBranchViolation(ValueError):
    """Raised when deterministic branch construction is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_strings(*values: object) -> list[str]:
    merged: set[str] = set()

    for value in values:
        if isinstance(value, list):
            merged.update(
                item
                for item in value
                if isinstance(item, str) and item
            )

    return sorted(merged)


def _derive_branch_status(
    source_review_status: str,
    bundle_status: str,
) -> str:
    if (
        source_review_status == "BLOCKED"
        or bundle_status == "BLOCKED"
    ):
        return "BLOCKED"

    if (
        source_review_status == "ARCHIVED"
        or bundle_status == "ARCHIVED"
    ):
        return "ARCHIVED"

    if (
        source_review_status == "REGISTERED"
        and bundle_status == "READY_FOR_BRANCH_CONSTRUCTION"
    ):
        return "READY_FOR_ASSESSMENT"

    return "REVIEW_REQUIRED"


def _validate_source_linkage(
    input_record: Mapping[str, Any],
    assumption_bundle: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []

    if assumption_bundle.get(
        "scenario_input_record_id"
    ) != input_record.get("record_id"):
        errors.append("scenario_input_record_link_mismatch")

    if assumption_bundle.get(
        "source_scenario_id"
    ) != input_record.get("source_scenario_id"):
        errors.append("source_scenario_link_mismatch")

    return errors


def build_scenario_branch_record(
    *,
    branch_id: str,
    branch_label: str,
    input_record: Mapping[str, Any],
    assumption_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one deterministic branch without truth inference."""
    input_errors = validate_scenario_input_record(input_record)
    bundle_errors = validate_scenario_assumption_bundle(
        assumption_bundle
    )
    linkage_errors = _validate_source_linkage(
        input_record,
        assumption_bundle,
    )

    errors = [
        *[f"input:{item}" for item in input_errors],
        *[f"bundle:{item}" for item in bundle_errors],
        *linkage_errors,
    ]

    if errors:
        raise ScenarioBranchViolation(";".join(errors))

    return {
        "branch_id": branch_id,
        "scenario_input_record_id": input_record["record_id"],
        "assumption_bundle_id": assumption_bundle["bundle_id"],
        "source_scenario_id": input_record[
            "source_scenario_id"
        ],
        "branch_label": branch_label,
        "assumption_ids": _canonical_strings(
            input_record["assumption_ids"],
            assumption_bundle["assumption_ids"],
        ),
        "evidence_references": _canonical_strings(
            input_record["evidence_references"],
            assumption_bundle["evidence_references"],
        ),
        "risk_flags": _canonical_strings(
            input_record["risk_flags"],
            assumption_bundle["risk_flags"],
        ),
        "source_review_status": input_record[
            "source_review_status"
        ],
        "bundle_status": assumption_bundle["bundle_status"],
        "branch_status": _derive_branch_status(
            input_record["source_review_status"],
            assumption_bundle["bundle_status"],
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": TRUTH_STATUS,
        "probability_status": PROBABILITY_STATUS,
        "rank_status": RANK_STATUS,
        "winner_status": WINNER_STATUS,
        "original_conclusion_reference": input_record[
            "original_conclusion_reference"
        ],
        "safety_flags": dict(input_record["safety_flags"]),
    }


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item
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


def validate_scenario_branch_record(
    branch: object,
) -> list[str]:
    """Return deterministic branch validation errors."""
    if not isinstance(branch, Mapping):
        return ["branch_must_be_mapping"]

    errors: list[str] = []

    if set(branch.keys()) != set(REQUIRED_BRANCH_FIELDS):
        errors.append("branch_fields_must_match_schema")

    for field in (
        "branch_id",
        "scenario_input_record_id",
        "assumption_bundle_id",
        "source_scenario_id",
    ):
        if not _valid_identifier(branch.get(field)):
            errors.append(f"{field}_invalid")

    for field in (
        "branch_label",
        "original_conclusion_reference",
    ):
        if not _valid_non_empty_string(branch.get(field)):
            errors.append(f"{field}_invalid")

    for field in (
        "assumption_ids",
        "evidence_references",
        "risk_flags",
    ):
        if not _valid_canonical_string_list(
            branch.get(field)
        ):
            errors.append(f"{field}_invalid")

    if branch.get("branch_status") not in BRANCH_STATUSES:
        errors.append("branch_status_invalid")

    if branch.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if branch.get("truth_status") != TRUTH_STATUS:
        errors.append("truth_status_must_remain_undetermined")

    if branch.get("probability_status") != (
        PROBABILITY_STATUS
    ):
        errors.append("probability_must_not_be_assigned")

    if branch.get("rank_status") != RANK_STATUS:
        errors.append("rank_must_not_be_assigned")

    if branch.get("winner_status") != WINNER_STATUS:
        errors.append("winner_must_not_be_selected")

    errors.extend(
        _validate_safety_flags(branch.get("safety_flags"))
    )

    return errors
