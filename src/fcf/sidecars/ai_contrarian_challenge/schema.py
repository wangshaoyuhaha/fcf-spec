"""Registered evidence schema for AI contrarian challenge review."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import (
    APP_ID,
    CHALLENGE_CATEGORIES,
    CHALLENGE_STATUSES,
    FORBIDDEN_OUTCOMES,
)


SCHEMA_VERSION = "1.0.0"

SOURCE_ARTIFACT_TYPES = (
    "AI_CONTEXT",
    "EVALUATION_RESULT",
    "COMPARISON",
    "DRIFT_REVIEW",
    "RISK_FLAGS",
    "EVIDENCE_REFERENCE",
)

CHALLENGE_SEVERITIES = (
    "INFO",
    "LOW",
    "MEDIUM",
    "HIGH",
)

OPERATOR_REVIEW_STATUSES = (
    "REVIEW_REQUIRED",
    "PENDING",
    "REVIEWED",
    "BLOCKED",
    "ARCHIVED",
)

REQUIRED_EVIDENCE_FIELDS = (
    "app_id",
    "schema_version",
    "challenge_evidence_id",
    "source_artifact_id",
    "source_artifact_type",
    "source_artifact_reference",
    "claim_reference",
    "source_conclusion",
    "challenge_category",
    "challenge_severity",
    "challenge_statement",
    "evidence_references",
    "risk_flags",
    "challenge_status",
    "operator_review_status",
    "created_at_utc",
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "deterministic_only",
    "registered_artifacts_only",
    "operator_review_required",
    "original_conclusion_preserved",
    "core_mutation_allowed",
    "source_artifact_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "automatic_truth_decision_allowed",
    "automatic_winner_selection_allowed",
    "automatic_conclusion_replacement_allowed",
    "automatic_model_switch_allowed",
    "automatic_prompt_switch_allowed",
    "operator_review_bypass_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
)

STRING_FIELDS = (
    "app_id",
    "schema_version",
    "challenge_evidence_id",
    "source_artifact_id",
    "source_artifact_type",
    "source_artifact_reference",
    "claim_reference",
    "source_conclusion",
    "challenge_category",
    "challenge_severity",
    "challenge_statement",
    "challenge_status",
    "operator_review_status",
    "created_at_utc",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "deterministic_only",
    "registered_artifacts_only",
    "operator_review_required",
    "original_conclusion_preserved",
)

REQUIRED_FALSE_FLAGS = (
    "core_mutation_allowed",
    "source_artifact_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "automatic_truth_decision_allowed",
    "automatic_winner_selection_allowed",
    "automatic_conclusion_replacement_allowed",
    "automatic_model_switch_allowed",
    "automatic_prompt_switch_allowed",
    "operator_review_bypass_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
)


def build_challenge_evidence_record(
    *,
    challenge_evidence_id: str,
    source_artifact_id: str,
    source_artifact_type: str,
    source_artifact_reference: str,
    claim_reference: str,
    source_conclusion: str,
    challenge_category: str,
    challenge_severity: str,
    challenge_statement: str,
    evidence_references: list[str],
    risk_flags: list[str],
    challenge_status: str,
    operator_review_status: str,
    created_at_utc: str,
) -> dict[str, Any]:
    """Build a deterministic registered challenge evidence record."""

    return {
        "app_id": APP_ID,
        "schema_version": SCHEMA_VERSION,
        "challenge_evidence_id": challenge_evidence_id,
        "source_artifact_id": source_artifact_id,
        "source_artifact_type": source_artifact_type,
        "source_artifact_reference": source_artifact_reference,
        "claim_reference": claim_reference,
        "source_conclusion": source_conclusion,
        "challenge_category": challenge_category,
        "challenge_severity": challenge_severity,
        "challenge_statement": challenge_statement,
        "evidence_references": list(evidence_references),
        "risk_flags": list(risk_flags),
        "challenge_status": challenge_status,
        "operator_review_status": operator_review_status,
        "created_at_utc": created_at_utc,
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


def _parse_aware_timestamp(value: Any) -> datetime | None:
    if not _is_non_empty_string(value):
        return None

    normalized = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return None

    return parsed


def validate_challenge_evidence_record(
    record: Mapping[str, Any],
) -> list[str]:
    """Return deterministic challenge evidence validation errors."""

    if not isinstance(record, Mapping):
        return ["record_not_mapping"]

    errors: list[str] = []

    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")

    unexpected_fields = sorted(
        set(record) - set(REQUIRED_EVIDENCE_FIELDS)
    )

    for field in unexpected_fields:
        errors.append(f"unexpected_field:{field}")

    for field in STRING_FIELDS:
        if field in record and not _is_non_empty_string(
            record[field]
        ):
            errors.append(f"{field}_invalid")

    if record.get("app_id") != APP_ID:
        errors.append("app_id_mismatch")

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")

    if record.get(
        "source_artifact_type"
    ) not in SOURCE_ARTIFACT_TYPES:
        errors.append("source_artifact_type_invalid")

    if record.get(
        "challenge_category"
    ) not in CHALLENGE_CATEGORIES:
        errors.append("challenge_category_invalid")

    if record.get(
        "challenge_severity"
    ) not in CHALLENGE_SEVERITIES:
        errors.append("challenge_severity_invalid")

    challenge_status = record.get("challenge_status")

    if challenge_status not in CHALLENGE_STATUSES:
        errors.append("challenge_status_invalid")

    if challenge_status in FORBIDDEN_OUTCOMES:
        errors.append(
            f"forbidden_challenge_outcome:{challenge_status}"
        )

    if record.get(
        "operator_review_status"
    ) not in OPERATOR_REVIEW_STATUSES:
        errors.append("operator_review_status_invalid")

    evidence_references = record.get(
        "evidence_references"
    )

    if not _is_string_list(
        evidence_references,
        allow_empty=True,
    ):
        errors.append("evidence_references_invalid")

    risk_flags = record.get("risk_flags")

    if not _is_string_list(
        risk_flags,
        allow_empty=True,
    ):
        errors.append("risk_flags_invalid")

    if isinstance(evidence_references, list):
        if len(evidence_references) != len(
            set(evidence_references)
        ):
            errors.append(
                "evidence_references_duplicate"
            )

    if isinstance(risk_flags, list):
        if len(risk_flags) != len(set(risk_flags)):
            errors.append("risk_flags_duplicate")

    if (
        record.get("challenge_category")
        == "MISSING_EVIDENCE"
        and isinstance(evidence_references, list)
        and evidence_references
    ):
        errors.append(
            "missing_evidence_category_has_evidence"
        )

    if (
        record.get("challenge_category")
        != "MISSING_EVIDENCE"
        and isinstance(evidence_references, list)
        and not evidence_references
    ):
        errors.append(
            "evidence_references_required"
        )

    if _parse_aware_timestamp(
        record.get("created_at_utc")
    ) is None:
        errors.append("created_at_utc_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if record.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return sorted(set(errors))