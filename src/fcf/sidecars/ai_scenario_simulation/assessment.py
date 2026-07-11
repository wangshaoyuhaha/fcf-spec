"""Deterministic cross-scenario consequence assessment."""

import re
from typing import Any, Mapping, Sequence

from .branch import validate_scenario_branch_record
from .contract import REQUIRED_FALSE_FLAGS, REQUIRED_TRUE_FLAGS


STAGE_ID = "AI-SCENARIO-SIMULATION-D4"
ASSESSMENT_SCHEMA_VERSION = "1.0.0"

CONSEQUENCE_POLARITIES = (
    "POSITIVE",
    "NEGATIVE",
    "NEUTRAL",
    "UNKNOWN",
)

ASSESSMENT_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

TRUTH_STATUS = "UNDETERMINED"
PROBABILITY_STATUS = "NOT_ASSIGNED"
RANK_STATUS = "NOT_ASSIGNED"
WINNER_STATUS = "NOT_SELECTED"

ISSUE_REASON_CODES = (
    "NO_REGISTERED_CONSEQUENCES",
    "EXPLICIT_POLARITY_CONTRADICTION",
    "UNCERTAINTY_REGISTERED",
    "REGISTERED_EVIDENCE_MISSING",
    "BRANCH_COVERAGE_MISSING",
)

REQUIRED_CONSEQUENCE_FIELDS = (
    "consequence_id",
    "branch_id",
    "consequence_key",
    "consequence_polarity",
    "evidence_references",
    "uncertainty_flags",
    "operator_review_status",
    "truth_status",
    "safety_flags",
)

REQUIRED_COMPARISON_FIELDS = (
    "consequence_key",
    "branch_ids",
    "polarities",
    "shared_evidence_references",
    "missing_evidence_branch_ids",
    "missing_branch_coverage_ids",
    "contradiction_detected",
    "uncertainty_detected",
    "reason_codes",
)

REQUIRED_ASSESSMENT_FIELDS = (
    "assessment_id",
    "branch_ids",
    "source_scenario_ids",
    "consequence_record_ids",
    "comparison_items",
    "summary",
    "reason_codes",
    "assessment_status",
    "operator_review_status",
    "truth_status",
    "probability_status",
    "rank_status",
    "winner_status",
    "original_conclusion_references",
    "safety_flags",
)

SUMMARY_FIELDS = (
    "branch_count",
    "consequence_record_count",
    "comparison_item_count",
    "contradiction_count",
    "uncertainty_count",
    "evidence_gap_count",
    "coverage_gap_count",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class ScenarioAssessmentViolation(ValueError):
    """Raised when registered assessment inputs are invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_strings(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


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


def build_registered_consequence_record(
    *,
    consequence_id: str,
    branch_id: str,
    consequence_key: str,
    consequence_polarity: str,
    evidence_references: Sequence[str],
    uncertainty_flags: Sequence[str],
) -> dict[str, Any]:
    """Build a registered consequence record without inference."""
    return {
        "consequence_id": consequence_id,
        "branch_id": branch_id,
        "consequence_key": consequence_key,
        "consequence_polarity": consequence_polarity,
        "evidence_references": _canonical_strings(
            evidence_references
        ),
        "uncertainty_flags": _canonical_strings(
            uncertainty_flags
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": TRUTH_STATUS,
        "safety_flags": _safety_flags(),
    }


def validate_registered_consequence_record(
    record: object,
) -> list[str]:
    """Return deterministic consequence-record errors."""
    if not isinstance(record, Mapping):
        return ["consequence_record_must_be_mapping"]

    errors: list[str] = []

    if set(record.keys()) != set(REQUIRED_CONSEQUENCE_FIELDS):
        errors.append("consequence_fields_must_match_schema")

    for field in (
        "consequence_id",
        "branch_id",
    ):
        if not _valid_identifier(record.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_non_empty_string(
        record.get("consequence_key")
    ):
        errors.append("consequence_key_invalid")

    if record.get("consequence_polarity") not in (
        CONSEQUENCE_POLARITIES
    ):
        errors.append("consequence_polarity_invalid")

    for field in (
        "evidence_references",
        "uncertainty_flags",
    ):
        if not _valid_canonical_string_list(record.get(field)):
            errors.append(f"{field}_invalid")

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


def _shared_evidence(
    records: Sequence[Mapping[str, Any]],
) -> list[str]:
    evidence_sets = [
        set(record["evidence_references"])
        for record in records
        if record["evidence_references"]
    ]

    if not evidence_sets:
        return []

    shared = set(evidence_sets[0])

    for evidence_set in evidence_sets[1:]:
        shared.intersection_update(evidence_set)

    return sorted(shared)


def _comparison_item(
    *,
    consequence_key: str,
    records: Sequence[Mapping[str, Any]],
    all_branch_ids: Sequence[str],
) -> dict[str, Any]:
    branch_ids = sorted(
        {
            str(record["branch_id"])
            for record in records
        }
    )
    polarities = sorted(
        {
            str(record["consequence_polarity"])
            for record in records
        }
    )
    missing_evidence_branch_ids = sorted(
        {
            str(record["branch_id"])
            for record in records
            if not record["evidence_references"]
        }
    )
    missing_branch_coverage_ids = sorted(
        set(all_branch_ids) - set(branch_ids)
    )

    polarity_set = set(polarities)
    contradiction_detected = (
        "POSITIVE" in polarity_set
        and "NEGATIVE" in polarity_set
    )
    uncertainty_detected = (
        "UNKNOWN" in polarity_set
        or any(
            bool(record["uncertainty_flags"])
            for record in records
        )
    )

    shared_evidence_references = _shared_evidence(records)
    reason_codes: list[str] = []

    if contradiction_detected:
        reason_codes.append(
            "EXPLICIT_POLARITY_CONTRADICTION"
        )

    if uncertainty_detected:
        reason_codes.append("UNCERTAINTY_REGISTERED")

    if missing_evidence_branch_ids:
        reason_codes.append("REGISTERED_EVIDENCE_MISSING")

    if missing_branch_coverage_ids:
        reason_codes.append("BRANCH_COVERAGE_MISSING")

    if shared_evidence_references:
        reason_codes.append(
            "SHARED_EVIDENCE_REFERENCE_PRESENT"
        )

    if not reason_codes:
        reason_codes.append(
            "NO_REGISTERED_CONTRADICTION_OR_GAP"
        )

    return {
        "consequence_key": consequence_key,
        "branch_ids": branch_ids,
        "polarities": polarities,
        "shared_evidence_references": (
            shared_evidence_references
        ),
        "missing_evidence_branch_ids": (
            missing_evidence_branch_ids
        ),
        "missing_branch_coverage_ids": (
            missing_branch_coverage_ids
        ),
        "contradiction_detected": contradiction_detected,
        "uncertainty_detected": uncertainty_detected,
        "reason_codes": sorted(reason_codes),
    }


def _derive_assessment_status(
    *,
    branch_statuses: Sequence[str],
    reason_codes: Sequence[str],
) -> str:
    if "BLOCKED" in branch_statuses:
        return "BLOCKED"

    if (
        branch_statuses
        and set(branch_statuses) == {"ARCHIVED"}
    ):
        return "ARCHIVED"

    if any(code in ISSUE_REASON_CODES for code in reason_codes):
        return "REVIEW_REQUIRED"

    return "READY_FOR_OPERATOR_REVIEW"


def build_cross_scenario_assessment(
    *,
    assessment_id: str,
    branch_records: Sequence[Mapping[str, Any]],
    consequence_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build deterministic cross-scenario governance evidence."""
    if (
        not isinstance(branch_records, Sequence)
        or isinstance(branch_records, (str, bytes))
    ):
        raise ScenarioAssessmentViolation(
            "branch_records_must_be_sequence"
        )

    if len(branch_records) < 2:
        raise ScenarioAssessmentViolation(
            "at_least_two_branches_required"
        )

    if (
        not isinstance(consequence_records, Sequence)
        or isinstance(consequence_records, (str, bytes))
    ):
        raise ScenarioAssessmentViolation(
            "consequence_records_must_be_sequence"
        )

    branch_map: dict[str, Mapping[str, Any]] = {}

    for index, branch in enumerate(branch_records):
        branch_errors = validate_scenario_branch_record(branch)

        if branch_errors:
            raise ScenarioAssessmentViolation(
                "branch:"
                + str(index)
                + ":"
                + ";".join(branch_errors)
            )

        branch_id = str(branch["branch_id"])

        if branch_id in branch_map:
            raise ScenarioAssessmentViolation(
                f"duplicate_branch_id:{branch_id}"
            )

        branch_map[branch_id] = branch

    consequence_map: dict[str, Mapping[str, Any]] = {}
    groups: dict[str, list[Mapping[str, Any]]] = {}

    for index, record in enumerate(consequence_records):
        record_errors = (
            validate_registered_consequence_record(record)
        )

        if record_errors:
            raise ScenarioAssessmentViolation(
                "consequence:"
                + str(index)
                + ":"
                + ";".join(record_errors)
            )

        consequence_id = str(record["consequence_id"])

        if consequence_id in consequence_map:
            raise ScenarioAssessmentViolation(
                f"duplicate_consequence_id:{consequence_id}"
            )

        branch_id = str(record["branch_id"])

        if branch_id not in branch_map:
            raise ScenarioAssessmentViolation(
                f"unknown_branch_id:{branch_id}"
            )

        consequence_map[consequence_id] = record
        consequence_key = str(record["consequence_key"])
        groups.setdefault(consequence_key, []).append(record)

    branch_ids = sorted(branch_map)
    comparison_items = [
        _comparison_item(
            consequence_key=consequence_key,
            records=sorted(
                groups[consequence_key],
                key=lambda item: (
                    str(item["branch_id"]),
                    str(item["consequence_id"]),
                ),
            ),
            all_branch_ids=branch_ids,
        )
        for consequence_key in sorted(groups)
    ]

    reason_codes = sorted(
        {
            code
            for item in comparison_items
            for code in item["reason_codes"]
        }
    )

    if not consequence_records:
        reason_codes = ["NO_REGISTERED_CONSEQUENCES"]

    contradiction_count = sum(
        1
        for item in comparison_items
        if item["contradiction_detected"]
    )
    uncertainty_count = sum(
        1
        for item in comparison_items
        if item["uncertainty_detected"]
    )
    evidence_gap_count = sum(
        1
        for item in comparison_items
        if item["missing_evidence_branch_ids"]
    )
    coverage_gap_count = sum(
        1
        for item in comparison_items
        if item["missing_branch_coverage_ids"]
    )

    branch_statuses = sorted(
        {
            str(branch["branch_status"])
            for branch in branch_map.values()
        }
    )

    return {
        "assessment_id": assessment_id,
        "branch_ids": branch_ids,
        "source_scenario_ids": sorted(
            {
                str(branch["source_scenario_id"])
                for branch in branch_map.values()
            }
        ),
        "consequence_record_ids": sorted(consequence_map),
        "comparison_items": comparison_items,
        "summary": {
            "branch_count": len(branch_ids),
            "consequence_record_count": len(consequence_map),
            "comparison_item_count": len(comparison_items),
            "contradiction_count": contradiction_count,
            "uncertainty_count": uncertainty_count,
            "evidence_gap_count": evidence_gap_count,
            "coverage_gap_count": coverage_gap_count,
        },
        "reason_codes": reason_codes,
        "assessment_status": _derive_assessment_status(
            branch_statuses=branch_statuses,
            reason_codes=reason_codes,
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": TRUTH_STATUS,
        "probability_status": PROBABILITY_STATUS,
        "rank_status": RANK_STATUS,
        "winner_status": WINNER_STATUS,
        "original_conclusion_references": sorted(
            {
                str(
                    branch[
                        "original_conclusion_reference"
                    ]
                )
                for branch in branch_map.values()
            }
        ),
        "safety_flags": _safety_flags(),
    }


def _validate_comparison_item(
    item: object,
) -> list[str]:
    if not isinstance(item, Mapping):
        return ["comparison_item_must_be_mapping"]

    errors: list[str] = []

    if set(item.keys()) != set(REQUIRED_COMPARISON_FIELDS):
        errors.append("comparison_fields_must_match_schema")

    if not _valid_non_empty_string(
        item.get("consequence_key")
    ):
        errors.append("consequence_key_invalid")

    for field in (
        "branch_ids",
        "polarities",
        "shared_evidence_references",
        "missing_evidence_branch_ids",
        "missing_branch_coverage_ids",
        "reason_codes",
    ):
        if not _valid_canonical_string_list(item.get(field)):
            errors.append(f"{field}_invalid")

    polarities = item.get("polarities")

    if isinstance(polarities, list) and any(
        polarity not in CONSEQUENCE_POLARITIES
        for polarity in polarities
    ):
        errors.append("polarities_invalid")

    for field in (
        "contradiction_detected",
        "uncertainty_detected",
    ):
        if not isinstance(item.get(field), bool):
            errors.append(f"{field}_must_be_boolean")

    return errors


def validate_cross_scenario_assessment(
    assessment: object,
) -> list[str]:
    """Return deterministic assessment validation errors."""
    if not isinstance(assessment, Mapping):
        return ["assessment_must_be_mapping"]

    errors: list[str] = []

    if set(assessment.keys()) != set(
        REQUIRED_ASSESSMENT_FIELDS
    ):
        errors.append("assessment_fields_must_match_schema")

    if not _valid_identifier(
        assessment.get("assessment_id")
    ):
        errors.append("assessment_id_invalid")

    for field in (
        "branch_ids",
        "source_scenario_ids",
        "consequence_record_ids",
        "reason_codes",
        "original_conclusion_references",
    ):
        if not _valid_canonical_string_list(
            assessment.get(field)
        ):
            errors.append(f"{field}_invalid")

    comparison_items = assessment.get("comparison_items")

    if not isinstance(comparison_items, list):
        errors.append("comparison_items_must_be_list")
        comparison_items = []
    else:
        for index, item in enumerate(comparison_items):
            for item_error in _validate_comparison_item(item):
                errors.append(
                    f"comparison_item:{index}:{item_error}"
                )

    summary = assessment.get("summary")

    if not isinstance(summary, Mapping):
        errors.append("summary_must_be_mapping")
    else:
        if set(summary.keys()) != set(SUMMARY_FIELDS):
            errors.append("summary_fields_must_match_schema")

        for field in SUMMARY_FIELDS:
            value = summary.get(field)

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append(f"{field}_invalid")

        if (
            isinstance(assessment.get("branch_ids"), list)
            and summary.get("branch_count")
            != len(assessment["branch_ids"])
        ):
            errors.append("branch_count_mismatch")

        if (
            isinstance(
                assessment.get("consequence_record_ids"),
                list,
            )
            and summary.get("consequence_record_count")
            != len(assessment["consequence_record_ids"])
        ):
            errors.append(
                "consequence_record_count_mismatch"
            )

        if summary.get("comparison_item_count") != len(
            comparison_items
        ):
            errors.append("comparison_item_count_mismatch")

    if assessment.get("assessment_status") not in (
        ASSESSMENT_STATUSES
    ):
        errors.append("assessment_status_invalid")

    if assessment.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if assessment.get("truth_status") != TRUTH_STATUS:
        errors.append("truth_status_must_remain_undetermined")

    if assessment.get("probability_status") != (
        PROBABILITY_STATUS
    ):
        errors.append("probability_must_not_be_assigned")

    if assessment.get("rank_status") != RANK_STATUS:
        errors.append("rank_must_not_be_assigned")

    if assessment.get("winner_status") != WINNER_STATUS:
        errors.append("winner_must_not_be_selected")

    errors.extend(
        _validate_safety_flags(
            assessment.get("safety_flags")
        )
    )

    return errors
