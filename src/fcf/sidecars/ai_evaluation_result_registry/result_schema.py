"""Structured schema for imported AI evaluation result records."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import APP_ID, IMPORTED_RESULT_STATUSES


RESULT_STAGE_ID = "AI-EVALUATION-RESULT-REGISTRY-D2"
RESULT_SCHEMA_VERSION = "1.0.0"

OBSERVED_OUTCOMES = (
    "PASS",
    "FAIL",
    "REVIEW_REQUIRED",
    "INDETERMINATE",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "imported_artifact",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "automatic_evaluation_acceptance_allowed",
    "source_artifact_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "news_feed_connection_allowed",
    "trade_instruction_generation_allowed",
    "trade_action_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
    "broker_connection_allowed",
    "exchange_connection_allowed",
    "api_key_storage_allowed",
    "wallet_private_key_access_allowed",
    "real_account_access_allowed",
    "real_position_access_allowed",
    "automatic_position_sizing_allowed",
    "automatic_portfolio_action_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
)


def build_evaluation_result_record(
    *,
    result_id: str,
    result_version: str,
    sample_id: str,
    sample_version: str,
    evaluation_dimension: str,
    imported_output_ref: str,
    imported_output_sha256: str,
    observed_outcome: str,
    result_summary: str,
    evidence_refs: tuple[str, ...],
    prompt_model_registry_entry_ids: tuple[str, ...],
    context_evidence_entry_ids: tuple[str, ...],
    imported_at_utc: str,
    observed_reason_codes: tuple[str, ...] = (),
    observed_risk_flags: tuple[str, ...] = (),
    result_status: str = "REVIEW_REQUIRED",
) -> dict[str, Any]:
    """Build a fresh local imported evaluation result record."""

    sample_key = f"{sample_id}@{sample_version}"
    result_key = f"{result_id}@{result_version}"

    return {
        "app_id": APP_ID,
        "stage_id": RESULT_STAGE_ID,
        "schema_version": RESULT_SCHEMA_VERSION,
        "result_id": result_id,
        "result_version": result_version,
        "result_key": result_key,
        "sample_id": sample_id,
        "sample_version": sample_version,
        "sample_key": sample_key,
        "evaluation_dimension": evaluation_dimension,
        "imported_output_ref": imported_output_ref,
        "imported_output_sha256": imported_output_sha256,
        "observed_outcome": observed_outcome,
        "result_status": result_status,
        "result_summary": result_summary,
        "observed_reason_codes": list(
            observed_reason_codes
        ),
        "observed_risk_flags": list(
            observed_risk_flags
        ),
        "evidence_refs": list(evidence_refs),
        "prompt_model_registry_entry_ids": list(
            prompt_model_registry_entry_ids
        ),
        "context_evidence_entry_ids": list(
            context_evidence_entry_ids
        ),
        "imported_at_utc": imported_at_utc,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "imported_artifact": True,
        "operator_review_bypass_allowed": False,
        "automatic_evaluation_acceptance_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "news_feed_connection_allowed": False,
        "trade_instruction_generation_allowed": False,
        "trade_action_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_storage_allowed": False,
        "wallet_private_key_access_allowed": False,
        "real_account_access_allowed": False,
        "real_position_access_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_semantic_version(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"\d+\.\d+\.\d+", value) is not None
    )


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
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


def _valid_string_list(
    value: Any,
    *,
    allow_empty: bool,
) -> bool:
    if not isinstance(value, list):
        return False

    if not allow_empty and not value:
        return False

    return all(_valid_string(item) for item in value)


def validate_evaluation_result_record(
    record: Mapping[str, Any],
) -> list[str]:
    """Return deterministic imported result validation errors."""

    if not isinstance(record, Mapping):
        return ["record_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": RESULT_STAGE_ID,
        "schema_version": RESULT_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if record.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in (
        "result_id",
        "sample_id",
        "evaluation_dimension",
        "imported_output_ref",
        "result_summary",
    ):
        if not _valid_string(record.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_semantic_version(
        record.get("result_version")
    ):
        errors.append("result_version_invalid")

    if not _valid_semantic_version(
        record.get("sample_version")
    ):
        errors.append("sample_version_invalid")

    expected_result_key = (
        f"{record.get('result_id')}@"
        f"{record.get('result_version')}"
    )

    if record.get("result_key") != expected_result_key:
        errors.append("result_key_mismatch")

    expected_sample_key = (
        f"{record.get('sample_id')}@"
        f"{record.get('sample_version')}"
    )

    if record.get("sample_key") != expected_sample_key:
        errors.append("sample_key_mismatch")

    if not _valid_sha256(
        record.get("imported_output_sha256")
    ):
        errors.append("imported_output_sha256_invalid")

    if (
        record.get("observed_outcome")
        not in OBSERVED_OUTCOMES
    ):
        errors.append("observed_outcome_invalid")

    if (
        record.get("result_status")
        not in IMPORTED_RESULT_STATUSES
    ):
        errors.append("result_status_invalid")

    if not _valid_utc_timestamp(
        record.get("imported_at_utc")
    ):
        errors.append("imported_at_utc_invalid")

    for field in (
        "observed_reason_codes",
        "observed_risk_flags",
    ):
        if not _valid_string_list(
            record.get(field),
            allow_empty=True,
        ):
            errors.append(f"{field}_invalid")

    for field in (
        "evidence_refs",
        "prompt_model_registry_entry_ids",
        "context_evidence_entry_ids",
    ):
        if not _valid_string_list(
            record.get(field),
            allow_empty=False,
        ):
            errors.append(f"{field}_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if record.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors