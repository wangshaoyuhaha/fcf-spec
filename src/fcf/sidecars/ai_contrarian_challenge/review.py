"""Governance review packet for AI contrarian challenge findings."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .contract import APP_ID
from .report import (
    REPORT_STATUSES,
    REPORT_VERSION,
    REVIEW_CATEGORIES,
)


REVIEW_PACKET_VERSION = "1.0.0"

REVIEW_PRIORITIES = (
    "LOW",
    "MEDIUM",
    "HIGH",
)

PROHIBITED_REVIEW_ACTIONS = (
    "automatic_truth_decision",
    "automatic_winner_selection",
    "automatic_conclusion_replacement",
    "automatic_model_ranking",
    "automatic_model_selection",
    "automatic_prompt_selection",
    "automatic_model_switch",
    "automatic_prompt_switch",
    "operator_review_bypass",
    "trade_action",
    "real_execution",
    "core_mutation",
)

REQUIRED_REPORT_FIELDS = (
    "app_id",
    "report_version",
    "report_status",
    "result_status",
    "source_record_count",
    "finding_count",
    "artifact_count",
    "claim_count",
    "highest_severity",
    "category_counts",
    "severity_counts",
    "findings",
    "errors",
)

REQUIRED_FINDING_FIELDS = (
    "challenge_evidence_id",
    "source_artifact_id",
    "source_artifact_type",
    "source_artifact_reference",
    "claim_reference",
    "source_conclusion",
    "rule_id",
    "reason_code",
    "challenge_category",
    "challenge_severity",
    "challenge_statement",
    "evidence_references",
    "risk_flags",
    "required_action",
    "original_conclusion_preserved",
    "automatic_truth_decision_allowed",
    "automatic_conclusion_replacement_allowed",
)

VALID_SEVERITIES = (
    "INFO",
    "LOW",
    "MEDIUM",
    "HIGH",
)


def _safety_fields() -> dict[str, bool]:
    return {
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "deterministic_only": True,
        "registered_artifacts_only": True,
        "operator_review_required": True,
        "original_conclusion_preserved": True,
        "core_mutation_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "automatic_truth_decision_allowed": False,
        "automatic_winner_selection_allowed": False,
        "automatic_conclusion_replacement_allowed": False,
        "automatic_model_ranking_allowed": False,
        "automatic_model_selection_allowed": False,
        "automatic_prompt_selection_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "operator_review_bypass_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def _base_packet(
    *,
    packet_status: str,
    result_status: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "review_packet_version": REVIEW_PACKET_VERSION,
        "packet_status": packet_status,
        "result_status": result_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "source_report_version": REPORT_VERSION,
        "source_report_status": None,
        "source_record_count": 0,
        "review_item_count": 0,
        "priority_counts": {},
        "review_items": [],
        "required_action": (
            "human_operator_review_contrarian_findings"
        ),
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": sorted(set(errors)),
        **_safety_fields(),
    }


def _invalid_packet(errors: list[str]) -> dict[str, Any]:
    return _base_packet(
        packet_status="INVALID",
        result_status="INVALID",
        errors=errors,
    )


def _blocked_packet(errors: list[str]) -> dict[str, Any]:
    return _base_packet(
        packet_status="BLOCKED",
        result_status="BLOCKED",
        errors=errors,
    )


def _is_non_negative_int(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(
    value: Any,
    *,
    allow_empty: bool,
) -> bool:
    if not isinstance(value, list):
        return False

    if not allow_empty and not value:
        return False

    return all(
        _is_non_empty_string(item)
        for item in value
    )


def _is_count_mapping(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    return all(
        _is_non_empty_string(key)
        and _is_non_negative_int(count)
        for key, count in value.items()
    )


def _validate_finding(
    finding: Mapping[str, Any],
    *,
    index: int,
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FINDING_FIELDS:
        if field not in finding:
            errors.append(
                f"finding[{index}]:missing_field:{field}"
            )

    for field in (
        "challenge_evidence_id",
        "source_artifact_id",
        "source_artifact_type",
        "source_artifact_reference",
        "claim_reference",
        "source_conclusion",
        "rule_id",
        "reason_code",
        "challenge_statement",
        "required_action",
    ):
        if not _is_non_empty_string(finding.get(field)):
            errors.append(
                f"finding[{index}]:{field}_invalid"
            )

    if finding.get(
        "challenge_category"
    ) not in REVIEW_CATEGORIES:
        errors.append(
            f"finding[{index}]:challenge_category_invalid"
        )

    if finding.get(
        "challenge_severity"
    ) not in VALID_SEVERITIES:
        errors.append(
            f"finding[{index}]:challenge_severity_invalid"
        )

    if not _is_string_list(
        finding.get("evidence_references"),
        allow_empty=True,
    ):
        errors.append(
            f"finding[{index}]:evidence_references_invalid"
        )

    if not _is_string_list(
        finding.get("risk_flags"),
        allow_empty=True,
    ):
        errors.append(
            f"finding[{index}]:risk_flags_invalid"
        )

    if finding.get("required_action") != (
        "operator_review_registered_challenge"
    ):
        errors.append(
            f"finding[{index}]:required_action_invalid"
        )

    if finding.get(
        "original_conclusion_preserved"
    ) is not True:
        errors.append(
            f"finding[{index}]:"
            "original_conclusion_preserved_must_be_true"
        )

    for field in (
        "automatic_truth_decision_allowed",
        "automatic_conclusion_replacement_allowed",
    ):
        if finding.get(field) is not False:
            errors.append(
                f"finding[{index}]:{field}_must_be_false"
            )

    return errors


def _validate_source_report(
    report: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"missing_report_field:{field}")

    if report.get("app_id") != APP_ID:
        errors.append("report_app_id_mismatch")

    if report.get("report_version") != REPORT_VERSION:
        errors.append("report_version_mismatch")

    if report.get("report_status") not in REPORT_STATUSES:
        errors.append("report_status_invalid")

    for field in (
        "source_record_count",
        "finding_count",
        "artifact_count",
        "claim_count",
    ):
        if not _is_non_negative_int(report.get(field)):
            errors.append(f"{field}_invalid")

    if report.get(
        "highest_severity"
    ) not in VALID_SEVERITIES:
        errors.append("highest_severity_invalid")

    if not _is_count_mapping(
        report.get("category_counts")
    ):
        errors.append("category_counts_invalid")

    if not _is_count_mapping(
        report.get("severity_counts")
    ):
        errors.append("severity_counts_invalid")

    findings = report.get("findings")

    if not isinstance(findings, list):
        errors.append("findings_invalid")
    else:
        for index, finding in enumerate(findings):
            if not isinstance(finding, Mapping):
                errors.append(
                    f"finding_not_mapping:{index}"
                )
                continue

            errors.extend(
                _validate_finding(
                    finding,
                    index=index,
                )
            )

    if not _is_string_list(
        report.get("errors"),
        allow_empty=True,
    ):
        errors.append("report_errors_invalid")

    finding_count = report.get("finding_count")

    if (
        isinstance(findings, list)
        and _is_non_negative_int(finding_count)
        and finding_count != len(findings)
    ):
        errors.append("finding_count_mismatch")

    if (
        report.get("report_status") == "NO_CHALLENGE"
        and finding_count != 0
    ):
        errors.append(
            "no_challenge_report_has_findings"
        )

    if (
        report.get("report_status") == "REVIEW_REQUIRED"
        and finding_count == 0
    ):
        errors.append(
            "review_required_report_has_no_findings"
        )

    return sorted(set(errors))


def _priority_and_reasons(
    finding: Mapping[str, Any],
) -> tuple[str, list[str]]:
    category = finding["challenge_category"]
    severity = finding["challenge_severity"]
    risk_flags = finding["risk_flags"]

    reasons: list[str] = []

    if category in {
        "MISSING_EVIDENCE",
        "HIDDEN_RISK",
        "CROSS_ARTIFACT_CONTRADICTION",
    }:
        priority = "HIGH"

    elif severity == "HIGH":
        priority = "HIGH"

    elif category in {
        "UNSUPPORTED_CLAIM",
        "LOGICAL_GAP",
        "OVERCONFIDENCE",
    }:
        priority = "MEDIUM"

    elif severity == "MEDIUM":
        priority = "MEDIUM"

    else:
        priority = "LOW"

    reasons.append(
        f"challenge_category:{category.lower()}"
    )
    reasons.append(
        f"challenge_severity:{severity.lower()}"
    )

    if risk_flags:
        reasons.append("registered_risk_flags_present")

    if category == "MISSING_EVIDENCE":
        reasons.append("evidence_gap_requires_review")

    if category == "CROSS_ARTIFACT_CONTRADICTION":
        reasons.append(
            "cross_artifact_contradiction_requires_review"
        )

    return priority, sorted(set(reasons))


def build_challenge_review_packet(
    report: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic operator-only review packet."""

    if not isinstance(report, Mapping):
        return _invalid_packet(
            ["source_report_not_mapping"]
        )

    validation_errors = _validate_source_report(report)

    if validation_errors:
        return _invalid_packet(validation_errors)

    report_status = report["report_status"]

    if report_status == "INVALID":
        source_errors = [
            f"source_report:{error}"
            for error in report["errors"]
        ]

        return _invalid_packet(
            ["source_report_invalid", *source_errors]
        )

    if report_status == "BLOCKED":
        source_errors = [
            f"source_report:{error}"
            for error in report["errors"]
        ]

        return _blocked_packet(
            ["source_report_blocked", *source_errors]
        )

    ordered_findings = sorted(
        report["findings"],
        key=lambda item: (
            item["source_artifact_id"],
            item["claim_reference"],
            item["challenge_evidence_id"],
        ),
    )

    review_items: list[dict[str, Any]] = []

    for finding in ordered_findings:
        priority, review_reasons = (
            _priority_and_reasons(finding)
        )

        review_items.append(
            {
                "challenge_evidence_id": finding[
                    "challenge_evidence_id"
                ],
                "source_artifact_id": finding[
                    "source_artifact_id"
                ],
                "source_artifact_type": finding[
                    "source_artifact_type"
                ],
                "source_artifact_reference": finding[
                    "source_artifact_reference"
                ],
                "claim_reference": finding[
                    "claim_reference"
                ],
                "source_conclusion": finding[
                    "source_conclusion"
                ],
                "priority": priority,
                "challenge_category": finding[
                    "challenge_category"
                ],
                "challenge_severity": finding[
                    "challenge_severity"
                ],
                "reason_code": finding["reason_code"],
                "challenge_statement": finding[
                    "challenge_statement"
                ],
                "evidence_references": list(
                    finding["evidence_references"]
                ),
                "risk_flags": list(
                    finding["risk_flags"]
                ),
                "review_reasons": review_reasons,
                "required_action": (
                    "operator_review_contrarian_finding"
                ),
                "operator_review_status": (
                    "REVIEW_REQUIRED"
                ),
                "original_conclusion_preserved": True,
                "automatic_truth_decision_allowed": False,
                "automatic_winner_selection_allowed": False,
                "automatic_conclusion_replacement_allowed": False,
                "operator_review_bypass_allowed": False,
                "trade_action_allowed": False,
            }
        )

    priority_counter = Counter(
        item["priority"]
        for item in review_items
    )

    priority_counts = {
        priority: priority_counter[priority]
        for priority in REVIEW_PRIORITIES
        if priority_counter[priority] > 0
    }

    return {
        "app_id": APP_ID,
        "review_packet_version": REVIEW_PACKET_VERSION,
        "packet_status": "REVIEW_REQUIRED",
        "result_status": "RECORDED",
        "operator_review_status": "REVIEW_REQUIRED",
        "source_report_version": report[
            "report_version"
        ],
        "source_report_status": report_status,
        "source_record_count": report[
            "source_record_count"
        ],
        "review_item_count": len(review_items),
        "priority_counts": priority_counts,
        "review_items": review_items,
        "required_action": (
            "human_operator_review_contrarian_findings"
        ),
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": [],
        **_safety_fields(),
    }