"""Governance review packet for imported AI evaluation results."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import APP_ID
from .linkage_checks import (
    LINKAGE_STATUSES,
    validate_sample_result_linkage_report,
)
from .registry_index import (
    validate_evaluation_result_registry,
)


REVIEW_PACKET_STAGE_ID = "AI-EVALUATION-RESULT-REGISTRY-D5"
REVIEW_PACKET_SCHEMA_VERSION = "1.0.0"

GOVERNANCE_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
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


def _copy_status_counts(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}

    copied: dict[str, int] = {}

    for key, count in value.items():
        if (
            _valid_string(key)
            and isinstance(count, int)
            and not isinstance(count, bool)
            and count >= 0
        ):
            copied[str(key)] = count

    return copied


def _derive_governance_status(
    *,
    source_linkage_status: Any,
    source_validation_errors: list[str],
) -> str:
    if source_validation_errors:
        return "BLOCKED"

    if source_linkage_status == "FAIL":
        return "BLOCKED"

    if source_linkage_status == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"

    if source_linkage_status == "PASS":
        return "READY_FOR_OPERATOR_REVIEW"

    return "BLOCKED"


def build_evaluation_result_review_packet(
    *,
    packet_id: str,
    result_registry: Mapping[str, Any],
    linkage_report: Mapping[str, Any],
    created_at_utc: str,
    reviewer_note: str = "",
) -> dict[str, Any]:
    """Build a local paper-only result governance packet."""

    registry_errors = validate_evaluation_result_registry(
        result_registry
    )
    linkage_errors = validate_sample_result_linkage_report(
        linkage_report
    )

    source_validation_errors = [
        f"result_registry:{error}"
        for error in registry_errors
    ]
    source_validation_errors.extend(
        f"linkage_report:{error}"
        for error in linkage_errors
    )

    source_linkage_status = linkage_report.get(
        "linkage_status"
    )

    governance_status = _derive_governance_status(
        source_linkage_status=source_linkage_status,
        source_validation_errors=source_validation_errors,
    )

    known_sample_keys = _copy_string_list(
        linkage_report.get("known_sample_keys")
    )
    linked_result_keys = _copy_string_list(
        linkage_report.get("linked_result_keys")
    )

    return {
        "app_id": APP_ID,
        "stage_id": REVIEW_PACKET_STAGE_ID,
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
        "packet_id": packet_id,
        "created_at_utc": created_at_utc,
        "source_result_registry_id": result_registry.get(
            "registry_id"
        ),
        "source_linkage_report_id": linkage_report.get(
            "report_id"
        ),
        "source_linkage_stage_id": linkage_report.get(
            "stage_id"
        ),
        "sample_count": len(known_sample_keys),
        "result_count": linkage_report.get(
            "result_count",
            0,
        ),
        "linked_result_count": len(linked_result_keys),
        "known_sample_keys": known_sample_keys,
        "linked_result_keys": linked_result_keys,
        "unknown_sample_keys": _copy_string_list(
            linkage_report.get("unknown_sample_keys")
        ),
        "samples_without_results": _copy_string_list(
            linkage_report.get("samples_without_results")
        ),
        "dimension_mismatch_result_keys": _copy_string_list(
            linkage_report.get(
                "dimension_mismatch_result_keys"
            )
        ),
        "duplicate_output_sha256": _copy_string_list(
            linkage_report.get("duplicate_output_sha256")
        ),
        "result_status_counts": _copy_status_counts(
            linkage_report.get("result_status_counts")
        ),
        "source_validation_errors": (
            source_validation_errors
        ),
        "source_linkage_status": source_linkage_status,
        "governance_status": governance_status,
        "reviewer_note": reviewer_note,
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


def _expected_governance_status(
    packet: Mapping[str, Any],
) -> str:
    raw_errors = packet.get(
        "source_validation_errors",
        [],
    )

    source_errors = (
        raw_errors
        if isinstance(raw_errors, list)
        else ["invalid_source_validation_errors"]
    )

    return _derive_governance_status(
        source_linkage_status=packet.get(
            "source_linkage_status"
        ),
        source_validation_errors=source_errors,
    )


def validate_evaluation_result_review_packet(
    packet: Mapping[str, Any],
) -> list[str]:
    """Return deterministic governance packet errors."""

    if not isinstance(packet, Mapping):
        return ["packet_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": REVIEW_PACKET_STAGE_ID,
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if packet.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in (
        "packet_id",
        "source_result_registry_id",
        "source_linkage_report_id",
        "source_linkage_stage_id",
    ):
        if not _valid_string(packet.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_utc_timestamp(
        packet.get("created_at_utc")
    ):
        errors.append("created_at_utc_invalid")

    for field in (
        "sample_count",
        "result_count",
        "linked_result_count",
    ):
        value = packet.get(field)

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
        if not _valid_string_list(packet.get(field)):
            errors.append(f"{field}_invalid")

    known_sample_keys = packet.get("known_sample_keys")
    linked_result_keys = packet.get("linked_result_keys")

    if (
        isinstance(known_sample_keys, list)
        and isinstance(packet.get("sample_count"), int)
        and not isinstance(packet.get("sample_count"), bool)
        and packet.get("sample_count")
        != len(known_sample_keys)
    ):
        errors.append("sample_count_mismatch")

    if (
        isinstance(linked_result_keys, list)
        and isinstance(
            packet.get("linked_result_count"),
            int,
        )
        and not isinstance(
            packet.get("linked_result_count"),
            bool,
        )
        and packet.get("linked_result_count")
        != len(linked_result_keys)
    ):
        errors.append("linked_result_count_mismatch")

    status_counts = packet.get("result_status_counts")

    if not isinstance(status_counts, Mapping):
        errors.append("result_status_counts_invalid")
    else:
        for key, count in status_counts.items():
            if not _valid_string(key):
                errors.append(
                    "result_status_count_key_invalid"
                )
                break

            if (
                not isinstance(count, int)
                or isinstance(count, bool)
                or count < 0
            ):
                errors.append(
                    "result_status_count_value_invalid"
                )
                break

    if packet.get("source_linkage_status") not in (
        LINKAGE_STATUSES
    ):
        errors.append("source_linkage_status_invalid")

    governance_status = packet.get("governance_status")

    if governance_status not in GOVERNANCE_STATUSES:
        errors.append("governance_status_invalid")
    elif governance_status != _expected_governance_status(
        packet
    ):
        errors.append("governance_status_mismatch")

    if not isinstance(packet.get("reviewer_note"), str):
        errors.append("reviewer_note_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if packet.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if packet.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors