"""Final handoff for imported AI evaluation result governance."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import APP_ID
from .review_packet import (
    GOVERNANCE_STATUSES,
    validate_evaluation_result_review_packet,
)


HANDOFF_STAGE_ID = "AI-EVALUATION-RESULT-REGISTRY-D6"
HANDOFF_SCHEMA_VERSION = "1.0.0"

HANDOFF_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

COMPLETED_STAGES = (
    "AI-EVALUATION-RESULT-REGISTRY-D1",
    "AI-EVALUATION-RESULT-REGISTRY-D2",
    "AI-EVALUATION-RESULT-REGISTRY-D3",
    "AI-EVALUATION-RESULT-REGISTRY-D4",
    "AI-EVALUATION-RESULT-REGISTRY-D5",
    "AI-EVALUATION-RESULT-REGISTRY-D6",
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


def _copy_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [
        str(item)
        for item in value
        if _valid_string(item)
    ]


def _derive_handoff_status(
    *,
    source_governance_status: Any,
    source_validation_errors: list[str],
) -> str:
    if source_validation_errors:
        return "BLOCKED"

    if source_governance_status == "BLOCKED":
        return "BLOCKED"

    if source_governance_status == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"

    if source_governance_status == "READY_FOR_OPERATOR_REVIEW":
        return "READY_FOR_OPERATOR_REVIEW"

    return "BLOCKED"


def _next_review_state(handoff_status: str) -> str:
    if handoff_status == "BLOCKED":
        return "SOURCE_REPAIR_REQUIRED"

    return "OPERATOR_REVIEW_REQUIRED"


def build_evaluation_result_final_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
    created_at_utc: str,
) -> dict[str, Any]:
    """Build a final paper-only imported-result handoff."""

    review_errors = validate_evaluation_result_review_packet(
        review_packet
    )

    source_validation_errors = [
        f"review_packet:{error}"
        for error in review_errors
    ]

    source_governance_status = review_packet.get(
        "governance_status"
    )

    handoff_status = _derive_handoff_status(
        source_governance_status=source_governance_status,
        source_validation_errors=source_validation_errors,
    )

    summary_by_status = {
        "READY_FOR_OPERATOR_REVIEW": (
            "Imported evaluation result registry is structurally "
            "complete and remains subject to operator review."
        ),
        "REVIEW_REQUIRED": (
            "Imported evaluation result registry requires operator "
            "review before governance acceptance."
        ),
        "BLOCKED": (
            "Imported evaluation result registry is blocked until "
            "source governance issues are repaired and reviewed."
        ),
    }

    return {
        "app_id": APP_ID,
        "stage_id": HANDOFF_STAGE_ID,
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "handoff_id": handoff_id,
        "created_at_utc": created_at_utc,
        "source_review_stage_id": review_packet.get(
            "stage_id"
        ),
        "source_packet_id": review_packet.get("packet_id"),
        "source_result_registry_id": review_packet.get(
            "source_result_registry_id"
        ),
        "source_linkage_report_id": review_packet.get(
            "source_linkage_report_id"
        ),
        "source_linkage_status": review_packet.get(
            "source_linkage_status"
        ),
        "source_governance_status": (
            source_governance_status
        ),
        "sample_count": review_packet.get("sample_count", 0),
        "result_count": review_packet.get("result_count", 0),
        "linked_result_count": review_packet.get(
            "linked_result_count",
            0,
        ),
        "known_sample_keys": _copy_string_list(
            review_packet.get("known_sample_keys")
        ),
        "linked_result_keys": _copy_string_list(
            review_packet.get("linked_result_keys")
        ),
        "unknown_sample_keys": _copy_string_list(
            review_packet.get("unknown_sample_keys")
        ),
        "samples_without_results": _copy_string_list(
            review_packet.get("samples_without_results")
        ),
        "dimension_mismatch_result_keys": _copy_string_list(
            review_packet.get(
                "dimension_mismatch_result_keys"
            )
        ),
        "duplicate_output_sha256": _copy_string_list(
            review_packet.get("duplicate_output_sha256")
        ),
        "source_validation_errors": source_validation_errors,
        "completed_stages": list(COMPLETED_STAGES),
        "handoff_status": handoff_status,
        "next_review_state": _next_review_state(
            handoff_status
        ),
        "closeout_summary": summary_by_status[
            handoff_status
        ],
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


def _expected_handoff_status(
    handoff: Mapping[str, Any],
) -> str:
    raw_errors = handoff.get(
        "source_validation_errors",
        [],
    )

    source_errors = (
        raw_errors
        if isinstance(raw_errors, list)
        else ["invalid_source_validation_errors"]
    )

    return _derive_handoff_status(
        source_governance_status=handoff.get(
            "source_governance_status"
        ),
        source_validation_errors=source_errors,
    )


def validate_evaluation_result_final_handoff(
    handoff: Mapping[str, Any],
) -> list[str]:
    """Return deterministic final handoff validation errors."""

    if not isinstance(handoff, Mapping):
        return ["handoff_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": HANDOFF_STAGE_ID,
        "schema_version": HANDOFF_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if handoff.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in (
        "handoff_id",
        "source_review_stage_id",
        "source_packet_id",
        "source_result_registry_id",
        "source_linkage_report_id",
        "next_review_state",
        "closeout_summary",
    ):
        if not _valid_string(handoff.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_utc_timestamp(
        handoff.get("created_at_utc")
    ):
        errors.append("created_at_utc_invalid")

    for field in (
        "sample_count",
        "result_count",
        "linked_result_count",
    ):
        value = handoff.get(field)

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
        if not _valid_string_list(handoff.get(field)):
            errors.append(f"{field}_invalid")

    if handoff.get("completed_stages") != list(
        COMPLETED_STAGES
    ):
        errors.append("completed_stages_mismatch")

    if (
        isinstance(handoff.get("known_sample_keys"), list)
        and isinstance(handoff.get("sample_count"), int)
        and not isinstance(handoff.get("sample_count"), bool)
        and handoff.get("sample_count")
        != len(handoff.get("known_sample_keys"))
    ):
        errors.append("sample_count_mismatch")

    if (
        isinstance(handoff.get("linked_result_keys"), list)
        and isinstance(
            handoff.get("linked_result_count"),
            int,
        )
        and not isinstance(
            handoff.get("linked_result_count"),
            bool,
        )
        and handoff.get("linked_result_count")
        != len(handoff.get("linked_result_keys"))
    ):
        errors.append("linked_result_count_mismatch")

    if (
        handoff.get("source_governance_status")
        not in GOVERNANCE_STATUSES
    ):
        errors.append("source_governance_status_invalid")

    if handoff.get("source_linkage_status") not in (
        "PASS",
        "REVIEW_REQUIRED",
        "FAIL",
    ):
        errors.append("source_linkage_status_invalid")

    handoff_status = handoff.get("handoff_status")

    if handoff_status not in HANDOFF_STATUSES:
        errors.append("handoff_status_invalid")
    elif handoff_status != _expected_handoff_status(
        handoff
    ):
        errors.append("handoff_status_mismatch")

    if (
        handoff_status in HANDOFF_STATUSES
        and handoff.get("next_review_state")
        != _next_review_state(handoff_status)
    ):
        errors.append("next_review_state_mismatch")

    for field in REQUIRED_TRUE_FLAGS:
        if handoff.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if handoff.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors