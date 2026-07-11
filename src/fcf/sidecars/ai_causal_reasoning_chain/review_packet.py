"""Deterministic operator review packet for causal-chain evidence."""

from copy import deepcopy
import re
from typing import Any, Mapping, Sequence

from .assessment import (
    ASSESSMENT_STATUSES,
    FINDING_SEVERITIES,
    FINDING_TYPES,
    validate_causal_reasoning_assessment,
)
from .contract import (
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)


STAGE_ID = "AI-CAUSAL-REASONING-CHAIN-D5"
REVIEW_PACKET_VERSION = "1.0.0"

REVIEW_PACKET_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

REVIEW_PRIORITIES = (
    "STANDARD",
    "HIGH",
    "CRITICAL",
)

REQUIRED_SEVERITY_COUNT_FIELDS = (
    "INFO",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
)

REQUIRED_SUMMARY_FIELDS = (
    "claim_count",
    "node_count",
    "edge_count",
    "finding_count",
    "non_info_finding_count",
    "component_count",
    "cycle_count",
    "duplicate_edge_group_count",
    "reverse_edge_pair_count",
)

ACTION_BY_FINDING_TYPE = {
    "DISCONNECTED_COMPONENTS": (
        "REVIEW_DISCONNECTED_COMPONENTS"
    ),
    "CYCLE_DETECTED": "REVIEW_CYCLE_STRUCTURE",
    "DUPLICATE_DIRECTIONAL_EDGE": (
        "REVIEW_DUPLICATE_DIRECTIONAL_EDGES"
    ),
    "CONFLICTING_REVERSE_EDGE": (
        "REVIEW_REVERSE_EDGE_CONFLICTS"
    ),
    "MISSING_REGISTERED_PREMISE": (
        "REVIEW_MISSING_REGISTERED_PREMISES"
    ),
    "MISSING_SUPPORTING_EVIDENCE": (
        "REVIEW_MISSING_SUPPORTING_EVIDENCE"
    ),
    "COUNTEREVIDENCE_NOT_REVIEWED": (
        "REVIEW_COUNTEREVIDENCE"
    ),
    "COUNTEREVIDENCE_REVIEW_BLOCKED": (
        "RESOLVE_COUNTEREVIDENCE_REVIEW_BLOCK"
    ),
    "ALTERNATIVE_EXPLANATION_NOT_REVIEWED": (
        "REVIEW_ALTERNATIVE_EXPLANATIONS"
    ),
    "ALTERNATIVE_EXPLANATION_REVIEW_BLOCKED": (
        "RESOLVE_ALTERNATIVE_EXPLANATION_BLOCK"
    ),
    "SOURCE_CLAIM_REVIEW_REQUIRED": (
        "REVIEW_SOURCE_CLAIMS"
    ),
    "BLOCKED_SOURCE_CLAIM": (
        "RESOLVE_BLOCKED_SOURCE_CLAIMS"
    ),
}

REQUIRED_REVIEW_PACKET_FIELDS = (
    "packet_id",
    "source_assessment",
    "source_assessment_id",
    "source_assessment_status",
    "source_chain_id",
    "correlation_id",
    "research_run_id",
    "finding_records",
    "finding_type_counts",
    "severity_counts",
    "review_summary",
    "reason_codes",
    "required_operator_actions",
    "review_priority",
    "packet_status",
    "causal_truth_status",
    "probability_status",
    "winner_status",
    "operator_review_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "runtime_execution_status",
    "live_model_invocation_status",
    "prompt_execution_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class CausalReviewPacketViolation(ValueError):
    """Raised when an assessment cannot form a safe review packet."""


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


def _canonical_strings(
    values: Sequence[str],
) -> list[str]:
    return sorted(set(values))


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str)
        or not item.strip()
        for item in value
    ):
        return False

    return value == sorted(set(value))


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    return errors


def _finding_type_counts(
    finding_records: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    return {
        finding_type: sum(
            1
            for finding in finding_records
            if finding["finding_type"] == finding_type
        )
        for finding_type in FINDING_TYPES
    }


def _severity_counts(
    finding_records: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    return {
        severity: sum(
            1
            for finding in finding_records
            if finding["severity"] == severity
        )
        for severity in FINDING_SEVERITIES
    }


def _review_summary(
    assessment: Mapping[str, Any],
) -> dict[str, int]:
    source_chain = assessment["source_chain"]
    findings = assessment["finding_records"]

    return {
        "claim_count": len(
            source_chain["claim_records"]
        ),
        "node_count": len(source_chain["node_ids"]),
        "edge_count": len(
            source_chain["edge_records"]
        ),
        "finding_count": len(findings),
        "non_info_finding_count": sum(
            1
            for finding in findings
            if finding["severity"] != "INFO"
        ),
        "component_count": int(
            assessment["component_count"]
        ),
        "cycle_count": len(
            assessment["cycle_paths"]
        ),
        "duplicate_edge_group_count": len(
            assessment[
                "duplicate_directional_edge_groups"
            ]
        ),
        "reverse_edge_pair_count": len(
            assessment["reverse_edge_pairs"]
        ),
    }


def _required_operator_actions(
    finding_records: Sequence[Mapping[str, Any]],
) -> list[str]:
    actions = {
        ACTION_BY_FINDING_TYPE[
            str(finding["finding_type"])
        ]
        for finding in finding_records
        if (
            finding["severity"] != "INFO"
            and finding["finding_type"]
            in ACTION_BY_FINDING_TYPE
        )
    }

    actions.add(
        "REVIEW_REGISTERED_CAUSAL_EVIDENCE"
    )

    return sorted(actions)


def _reason_codes(
    assessment: Mapping[str, Any],
) -> list[str]:
    reasons = list(assessment["reason_codes"])

    if not reasons:
        reasons.append(
            "CAUSAL_ASSESSMENT_READY_FOR_OPERATOR_REVIEW"
        )

    return sorted(set(reasons))


def _review_priority(
    assessment: Mapping[str, Any],
    severity_counts: Mapping[str, int],
) -> str:
    if (
        assessment["assessment_status"] == "BLOCKED"
        or severity_counts["CRITICAL"] > 0
    ):
        return "CRITICAL"

    if (
        assessment["assessment_status"]
        == "REVIEW_REQUIRED"
        or severity_counts["HIGH"] > 0
        or severity_counts["MEDIUM"] > 0
    ):
        return "HIGH"

    return "STANDARD"


def _packet_status(
    assessment_status: str,
) -> str:
    mapping = {
        "READY_FOR_REVIEW_PACKET": (
            "READY_FOR_OPERATOR_REVIEW"
        ),
        "REVIEW_REQUIRED": "REVIEW_REQUIRED",
        "BLOCKED": "BLOCKED",
    }

    return mapping[assessment_status]


def _build_from_valid_assessment(
    *,
    packet_id: str,
    assessment: Mapping[str, Any],
) -> dict[str, Any]:
    findings = deepcopy(
        list(assessment["finding_records"])
    )

    type_counts = _finding_type_counts(findings)
    severity_counts = _severity_counts(findings)

    return {
        "packet_id": packet_id,
        "source_assessment": deepcopy(
            dict(assessment)
        ),
        "source_assessment_id": assessment[
            "assessment_id"
        ],
        "source_assessment_status": assessment[
            "assessment_status"
        ],
        "source_chain_id": assessment[
            "source_chain_id"
        ],
        "correlation_id": assessment[
            "correlation_id"
        ],
        "research_run_id": assessment[
            "research_run_id"
        ],
        "finding_records": findings,
        "finding_type_counts": type_counts,
        "severity_counts": severity_counts,
        "review_summary": _review_summary(
            assessment
        ),
        "reason_codes": _reason_codes(
            assessment
        ),
        "required_operator_actions": (
            _required_operator_actions(findings)
        ),
        "review_priority": _review_priority(
            assessment,
            severity_counts,
        ),
        "packet_status": _packet_status(
            str(assessment["assessment_status"])
        ),
        "causal_truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "runtime_execution_status": "NOT_ALLOWED",
        "live_model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def build_causal_reasoning_review_packet(
    *,
    packet_id: str,
    assessment: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a paper-only operator review packet."""
    assessment_errors = (
        validate_causal_reasoning_assessment(
            assessment
        )
    )

    if assessment_errors:
        raise CausalReviewPacketViolation(
            ";".join(assessment_errors)
        )

    return _build_from_valid_assessment(
        packet_id=packet_id,
        assessment=assessment,
    )


def _validate_count_mapping(
    value: Any,
    expected_keys: Sequence[str],
    field_name: str,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{field_name}_must_be_mapping"]

    errors: list[str] = []

    if set(value.keys()) != set(expected_keys):
        errors.append(
            f"{field_name}_fields_must_match_schema"
        )

    for key in expected_keys:
        count = value.get(key)

        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            errors.append(
                f"{field_name}_{key}_invalid"
            )

    return errors


def _validate_review_summary(
    value: Any,
) -> list[str]:
    if not isinstance(value, Mapping):
        return ["review_summary_must_be_mapping"]

    errors: list[str] = []

    if set(value.keys()) != set(
        REQUIRED_SUMMARY_FIELDS
    ):
        errors.append(
            "review_summary_fields_must_match_schema"
        )

    for field in REQUIRED_SUMMARY_FIELDS:
        count = value.get(field)

        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            errors.append(
                f"review_summary_{field}_invalid"
            )

    return errors


def validate_causal_reasoning_review_packet(
    packet: object,
) -> list[str]:
    """Return deterministic D5 review-packet validation errors."""
    if not isinstance(packet, Mapping):
        return ["review_packet_must_be_mapping"]

    errors: list[str] = []

    if set(packet.keys()) != set(
        REQUIRED_REVIEW_PACKET_FIELDS
    ):
        errors.append(
            "review_packet_fields_must_match_schema"
        )

    for field in (
        "packet_id",
        "source_assessment_id",
        "source_chain_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(packet.get(field)):
            errors.append(f"{field}_invalid")

    source_status = packet.get(
        "source_assessment_status"
    )

    if source_status not in ASSESSMENT_STATUSES:
        errors.append(
            "source_assessment_status_invalid"
        )

    source_assessment = packet.get(
        "source_assessment"
    )

    if not isinstance(source_assessment, Mapping):
        errors.append(
            "source_assessment_must_be_mapping"
        )
        source_errors = [
            "source_assessment_must_be_mapping"
        ]
    else:
        source_errors = (
            validate_causal_reasoning_assessment(
                source_assessment
            )
        )

        for source_error in source_errors:
            errors.append(
                f"source_assessment:{source_error}"
            )

    findings = packet.get("finding_records")

    if not isinstance(findings, list):
        errors.append(
            "finding_records_must_be_list"
        )

    errors.extend(
        _validate_count_mapping(
            packet.get("finding_type_counts"),
            FINDING_TYPES,
            "finding_type_counts",
        )
    )

    errors.extend(
        _validate_count_mapping(
            packet.get("severity_counts"),
            REQUIRED_SEVERITY_COUNT_FIELDS,
            "severity_counts",
        )
    )

    errors.extend(
        _validate_review_summary(
            packet.get("review_summary")
        )
    )

    for field in (
        "reason_codes",
        "required_operator_actions",
    ):
        if not _valid_canonical_string_list(
            packet.get(field)
        ):
            errors.append(f"{field}_invalid")

    if packet.get("review_priority") not in (
        REVIEW_PRIORITIES
    ):
        errors.append("review_priority_invalid")

    if packet.get("packet_status") not in (
        REVIEW_PACKET_STATUSES
    ):
        errors.append("packet_status_invalid")

    if packet.get("causal_truth_status") != (
        "UNDETERMINED"
    ):
        errors.append("causal_truth_status_invalid")

    if packet.get("probability_status") != (
        "NOT_ASSIGNED"
    ):
        errors.append("probability_status_invalid")

    if packet.get("winner_status") != (
        "NOT_SELECTED"
    ):
        errors.append("winner_status_invalid")

    if packet.get("operator_review_status") != (
        "REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    for field in (
        "source_artifacts_preserved",
        "original_conclusions_preserved",
    ):
        if packet.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in (
        "runtime_execution_status",
        "live_model_invocation_status",
        "prompt_execution_status",
    ):
        if packet.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_must_be_not_allowed")

    errors.extend(
        _validate_safety_flags(
            packet.get("safety_flags")
        )
    )

    if (
        isinstance(source_assessment, Mapping)
        and not source_errors
        and _valid_identifier(
            packet.get("packet_id")
        )
    ):
        expected = _build_from_valid_assessment(
            packet_id=str(packet["packet_id"]),
            assessment=source_assessment,
        )

        comparison_fields = (
            "source_assessment_id",
            "source_assessment_status",
            "source_chain_id",
            "correlation_id",
            "research_run_id",
            "finding_records",
            "finding_type_counts",
            "severity_counts",
            "review_summary",
            "reason_codes",
            "required_operator_actions",
            "review_priority",
            "packet_status",
        )

        for field in comparison_fields:
            if packet.get(field) != expected[field]:
                errors.append(f"{field}_mismatch")

    return sorted(set(errors))
