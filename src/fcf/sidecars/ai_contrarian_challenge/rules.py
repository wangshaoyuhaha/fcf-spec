"""Deterministic challenge rules for registered AI artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .contract import APP_ID
from .schema import validate_challenge_evidence_record


RULE_ENGINE_VERSION = "1.0.0"

RULE_IDS = (
    "RULE_UNSUPPORTED_CLAIM",
    "RULE_MISSING_EVIDENCE",
    "RULE_LOGICAL_GAP",
    "RULE_HIDDEN_RISK",
    "RULE_OVERCONFIDENCE",
    "RULE_CROSS_ARTIFACT_CONTRADICTION",
)

REASON_CODES = (
    "CLAIM_SUPPORT_INCOMPLETE",
    "REGISTERED_EVIDENCE_MISSING",
    "LOGICAL_LINK_NOT_REGISTERED",
    "RISK_NOT_REFLECTED_IN_CONCLUSION",
    "CONFIDENCE_EXCEEDS_REGISTERED_SUPPORT",
    "REGISTERED_ARTIFACTS_CONTRADICT",
)

_CATEGORY_RULES = {
    "UNSUPPORTED_CLAIM": (
        "RULE_UNSUPPORTED_CLAIM",
        "CLAIM_SUPPORT_INCOMPLETE",
        "MEDIUM",
    ),
    "MISSING_EVIDENCE": (
        "RULE_MISSING_EVIDENCE",
        "REGISTERED_EVIDENCE_MISSING",
        "HIGH",
    ),
    "LOGICAL_GAP": (
        "RULE_LOGICAL_GAP",
        "LOGICAL_LINK_NOT_REGISTERED",
        "MEDIUM",
    ),
    "HIDDEN_RISK": (
        "RULE_HIDDEN_RISK",
        "RISK_NOT_REFLECTED_IN_CONCLUSION",
        "HIGH",
    ),
    "OVERCONFIDENCE": (
        "RULE_OVERCONFIDENCE",
        "CONFIDENCE_EXCEEDS_REGISTERED_SUPPORT",
        "MEDIUM",
    ),
    "CROSS_ARTIFACT_CONTRADICTION": (
        "RULE_CROSS_ARTIFACT_CONTRADICTION",
        "REGISTERED_ARTIFACTS_CONTRADICT",
        "HIGH",
    ),
}

_SEVERITY_RANK = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


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
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "operator_review_bypass_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def _base_report(
    record: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = record or {}

    return {
        "app_id": APP_ID,
        "rule_engine_version": RULE_ENGINE_VERSION,
        "challenge_evidence_id": source.get(
            "challenge_evidence_id"
        ),
        "source_artifact_id": source.get(
            "source_artifact_id"
        ),
        "source_artifact_type": source.get(
            "source_artifact_type"
        ),
        "source_artifact_reference": source.get(
            "source_artifact_reference"
        ),
        "claim_reference": source.get(
            "claim_reference"
        ),
        "source_conclusion": source.get(
            "source_conclusion"
        ),
        "challenge_status": "INVALID",
        "result_status": "INVALID",
        "finding_count": 0,
        "highest_severity": "INFO",
        "findings": [],
        "operator_review_status": "REVIEW_REQUIRED",
        "errors": [],
        **_safety_fields(),
    }


def _invalid_report(
    record: Mapping[str, Any] | None,
    errors: list[str],
) -> dict[str, Any]:
    report = _base_report(record)
    report["errors"] = sorted(set(errors))
    return report


def _terminal_report(
    record: Mapping[str, Any],
    *,
    challenge_status: str,
    result_status: str,
) -> dict[str, Any]:
    report = _base_report(record)

    report.update(
        {
            "challenge_status": challenge_status,
            "result_status": result_status,
            "errors": [],
        }
    )

    return report


def _max_severity(
    input_severity: str,
    minimum_severity: str,
) -> str:
    if (
        _SEVERITY_RANK[input_severity]
        >= _SEVERITY_RANK[minimum_severity]
    ):
        return input_severity

    return minimum_severity


def apply_challenge_rules(
    record: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply deterministic contrarian challenge rules."""

    if not isinstance(record, Mapping):
        return _invalid_report(
            None,
            ["record_not_mapping"],
        )

    validation_errors = (
        validate_challenge_evidence_record(record)
    )

    if validation_errors:
        return _invalid_report(
            record,
            validation_errors,
        )

    source_status = record["challenge_status"]

    if source_status == "INVALID":
        return _invalid_report(
            record,
            ["source_challenge_status_invalid"],
        )

    if source_status == "BLOCKED":
        return _terminal_report(
            record,
            challenge_status="BLOCKED",
            result_status="BLOCKED",
        )

    if source_status == "ARCHIVED":
        return _terminal_report(
            record,
            challenge_status="ARCHIVED",
            result_status="ARCHIVED",
        )

    if source_status == "NO_CHALLENGE":
        return _terminal_report(
            record,
            challenge_status="NO_CHALLENGE",
            result_status="RECORDED",
        )

    category = record["challenge_category"]
    rule_id, reason_code, minimum_severity = (
        _CATEGORY_RULES[category]
    )

    effective_severity = _max_severity(
        record["challenge_severity"],
        minimum_severity,
    )

    finding = {
        "rule_id": rule_id,
        "reason_code": reason_code,
        "challenge_category": category,
        "challenge_severity": effective_severity,
        "challenge_statement": record[
            "challenge_statement"
        ],
        "source_conclusion": record[
            "source_conclusion"
        ],
        "evidence_references": sorted(
            record["evidence_references"]
        ),
        "risk_flags": sorted(record["risk_flags"]),
        "original_conclusion_preserved": True,
        "required_action": (
            "operator_review_registered_challenge"
        ),
        "automatic_truth_decision_allowed": False,
        "automatic_conclusion_replacement_allowed": False,
    }

    result_status = (
        "INSUFFICIENT_EVIDENCE"
        if source_status == "INSUFFICIENT_EVIDENCE"
        else "REVIEW_REQUIRED"
    )

    report = _base_report(record)

    report.update(
        {
            "challenge_status": "REVIEW_REQUIRED",
            "result_status": result_status,
            "finding_count": 1,
            "highest_severity": effective_severity,
            "findings": [finding],
            "errors": [],
        }
    )

    return report