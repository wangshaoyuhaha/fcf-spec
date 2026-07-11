"""Paper-only operator review packet for scenario simulation."""

import re
from typing import Any, Mapping

from .assessment import validate_cross_scenario_assessment
from .contract import REQUIRED_FALSE_FLAGS, REQUIRED_TRUE_FLAGS


STAGE_ID = "AI-SCENARIO-SIMULATION-D5"
REVIEW_PACKET_VERSION = "1.0.0"

PACKET_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

REVIEW_PRIORITIES = (
    "STANDARD",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
)

REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "assessment_id",
    "packet_status",
    "review_priority",
    "branch_ids",
    "source_scenario_ids",
    "consequence_record_ids",
    "contradiction_items",
    "uncertainty_items",
    "evidence_gap_items",
    "coverage_gap_items",
    "reason_codes",
    "assessment_summary",
    "original_conclusion_references",
    "required_action",
    "operator_review_status",
    "truth_status",
    "probability_status",
    "rank_status",
    "winner_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class ScenarioReviewPacketViolation(ValueError):
    """Raised when a D5 source assessment is invalid."""


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


def _packet_status(assessment_status: str) -> str:
    if assessment_status == "BLOCKED":
        return "BLOCKED"

    if assessment_status == "ARCHIVED":
        return "ARCHIVED"

    if assessment_status == "READY_FOR_OPERATOR_REVIEW":
        return "READY_FOR_OPERATOR_REVIEW"

    return "REVIEW_REQUIRED"


def _review_priority(
    assessment: Mapping[str, Any],
) -> str:
    if assessment["assessment_status"] == "BLOCKED":
        return "CRITICAL"

    summary = assessment["summary"]

    if summary["contradiction_count"] > 0:
        return "HIGH"

    if (
        summary["uncertainty_count"] > 0
        or summary["evidence_gap_count"] > 0
        or summary["coverage_gap_count"] > 0
        or "NO_REGISTERED_CONSEQUENCES"
        in assessment["reason_codes"]
    ):
        return "MEDIUM"

    return "STANDARD"


def _comparison_item_summary(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "consequence_key": item["consequence_key"],
        "branch_ids": list(item["branch_ids"]),
        "polarities": list(item["polarities"]),
        "shared_evidence_references": list(
            item["shared_evidence_references"]
        ),
        "missing_evidence_branch_ids": list(
            item["missing_evidence_branch_ids"]
        ),
        "missing_branch_coverage_ids": list(
            item["missing_branch_coverage_ids"]
        ),
        "reason_codes": list(item["reason_codes"]),
    }


def build_scenario_simulation_review_packet(
    *,
    packet_id: str,
    assessment: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic operator-only D5 review packet."""
    errors = validate_cross_scenario_assessment(assessment)

    if errors:
        raise ScenarioReviewPacketViolation(
            ";".join(errors)
        )

    comparison_items = assessment["comparison_items"]

    contradiction_items = [
        _comparison_item_summary(item)
        for item in comparison_items
        if item["contradiction_detected"]
    ]
    uncertainty_items = [
        _comparison_item_summary(item)
        for item in comparison_items
        if item["uncertainty_detected"]
    ]
    evidence_gap_items = [
        _comparison_item_summary(item)
        for item in comparison_items
        if item["missing_evidence_branch_ids"]
    ]
    coverage_gap_items = [
        _comparison_item_summary(item)
        for item in comparison_items
        if item["missing_branch_coverage_ids"]
    ]

    return {
        "packet_id": packet_id,
        "assessment_id": assessment["assessment_id"],
        "packet_status": _packet_status(
            assessment["assessment_status"]
        ),
        "review_priority": _review_priority(assessment),
        "branch_ids": list(assessment["branch_ids"]),
        "source_scenario_ids": list(
            assessment["source_scenario_ids"]
        ),
        "consequence_record_ids": list(
            assessment["consequence_record_ids"]
        ),
        "contradiction_items": contradiction_items,
        "uncertainty_items": uncertainty_items,
        "evidence_gap_items": evidence_gap_items,
        "coverage_gap_items": coverage_gap_items,
        "reason_codes": list(assessment["reason_codes"]),
        "assessment_summary": dict(
            assessment["summary"]
        ),
        "original_conclusion_references": list(
            assessment[
                "original_conclusion_references"
            ]
        ),
        "required_action": (
            "human_operator_review_scenario_simulation_evidence"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "rank_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "safety_flags": _safety_flags(),
    }


def _valid_review_item(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    required = {
        "consequence_key",
        "branch_ids",
        "polarities",
        "shared_evidence_references",
        "missing_evidence_branch_ids",
        "missing_branch_coverage_ids",
        "reason_codes",
    }

    if set(value.keys()) != required:
        return False

    if not _valid_non_empty_string(
        value.get("consequence_key")
    ):
        return False

    for field in (
        "branch_ids",
        "polarities",
        "shared_evidence_references",
        "missing_evidence_branch_ids",
        "missing_branch_coverage_ids",
        "reason_codes",
    ):
        if not _valid_canonical_string_list(
            value.get(field)
        ):
            return False

    return True


def validate_scenario_simulation_review_packet(
    packet: object,
) -> list[str]:
    """Return deterministic D5 packet validation errors."""
    if not isinstance(packet, Mapping):
        return ["packet_must_be_mapping"]

    errors: list[str] = []

    if set(packet.keys()) != set(REQUIRED_PACKET_FIELDS):
        errors.append("packet_fields_must_match_schema")

    for field in ("packet_id", "assessment_id"):
        if not _valid_identifier(packet.get(field)):
            errors.append(f"{field}_invalid")

    if packet.get("packet_status") not in PACKET_STATUSES:
        errors.append("packet_status_invalid")

    if packet.get("review_priority") not in (
        REVIEW_PRIORITIES
    ):
        errors.append("review_priority_invalid")

    for field in (
        "branch_ids",
        "source_scenario_ids",
        "consequence_record_ids",
        "reason_codes",
        "original_conclusion_references",
    ):
        if not _valid_canonical_string_list(
            packet.get(field)
        ):
            errors.append(f"{field}_invalid")

    for field in (
        "contradiction_items",
        "uncertainty_items",
        "evidence_gap_items",
        "coverage_gap_items",
    ):
        value = packet.get(field)

        if not isinstance(value, list):
            errors.append(f"{field}_must_be_list")
        else:
            for index, item in enumerate(value):
                if not _valid_review_item(item):
                    errors.append(
                        f"{field}:{index}:invalid"
                    )

    summary = packet.get("assessment_summary")

    if not isinstance(summary, Mapping):
        errors.append(
            "assessment_summary_must_be_mapping"
        )
    else:
        for field in (
            "branch_count",
            "consequence_record_count",
            "comparison_item_count",
            "contradiction_count",
            "uncertainty_count",
            "evidence_gap_count",
            "coverage_gap_count",
        ):
            value = summary.get(field)

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append(
                    f"assessment_summary_{field}_invalid"
                )

    if packet.get("required_action") != (
        "human_operator_review_scenario_simulation_evidence"
    ):
        errors.append("required_action_invalid")

    if packet.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if packet.get("truth_status") != "UNDETERMINED":
        errors.append(
            "truth_status_must_remain_undetermined"
        )

    if packet.get("probability_status") != "NOT_ASSIGNED":
        errors.append(
            "probability_must_not_be_assigned"
        )

    if packet.get("rank_status") != "NOT_ASSIGNED":
        errors.append("rank_must_not_be_assigned")

    if packet.get("winner_status") != "NOT_SELECTED":
        errors.append("winner_must_not_be_selected")

    errors.extend(
        _validate_safety_flags(
            packet.get("safety_flags")
        )
    )

    return errors
