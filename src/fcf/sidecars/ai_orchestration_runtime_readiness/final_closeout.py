"""Final readiness-only closeout for AI orchestration runtime."""

import copy
import hashlib
import json
import re
from typing import Any, Mapping

from .contract import (
    APP_ID,
    READINESS_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)
from .policy_config_review import (
    validate_operator_handoff,
    validate_runtime_readiness_review_packet,
)


STAGE_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-D6"
FINAL_CLOSEOUT_VERSION = "1.0.0"

FINAL_CLOSEOUT_TARGETS = (
    "FCF_PROJECT_CONTROL_CENTER",
    "OPERATOR_REVIEW_APP_1",
    "REPORT_ARCHIVE_APP_1",
    "VALIDATION_BASELINE_REGISTRY_APP_1",
)

FINAL_HANDOFF_STATUSES = (
    "WAITING_FOR_OPERATOR_REVIEW",
    "BLOCKED",
    "DEGRADED",
)

REQUIRED_FINAL_CLOSEOUT_FIELDS = (
    "closeout_id",
    "closeout_hash",
    "app_id",
    "stage_id",
    "closeout_version",
    "readiness_mode",
    "source_review_packet_id",
    "source_operator_handoff_id",
    "overall_status",
    "implementation_status",
    "handoff_status",
    "target_consumers",
    "review_packet_snapshot",
    "operator_handoff_snapshot",
    "operator_review_required",
    "operator_review_bypass_allowed",
    "main_merge_authorization_status",
    "control_center_sync_status",
    "final_current_state_status",
    "manual_archive_authorization_status",
    "automatic_archive_status",
    "archive_writing_status",
    "model_invocation_status",
    "prompt_execution_status",
    "automatic_routing_status",
    "automatic_fallback_status",
    "automatic_retry_status",
    "automatic_policy_activation_status",
    "automatic_learning_activation_status",
    "automatic_champion_promotion_status",
    "shadow_trading_status",
    "runtime_execution_status",
    "real_execution_status",
    "trading_api_status",
    "trading_credential_access_status",
    "core_mutation_status",
    "p48_expansion_status",
    "tag_status",
    "release_status",
    "deploy_status",
    "safety_flags",
)

FORBIDDEN_ACTION_FIELDS = (
    "activation_instruction",
    "archive_instruction",
    "buy",
    "deploy_instruction",
    "execute",
    "model_request",
    "order",
    "portfolio_action",
    "position_size",
    "prompt_request",
    "route_selection",
    "sell",
    "trade_instruction",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)
_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class FinalCloseoutViolation(ValueError):
    """Raised when the D6 closeout cannot be built safely."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


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

    expected = set(REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS)
    if set(value.keys()) != expected:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _handoff_status(overall_status: str) -> str:
    if overall_status == "BLOCKED":
        return "BLOCKED"
    if overall_status == "DEGRADED":
        return "DEGRADED"
    return "WAITING_FOR_OPERATOR_REVIEW"


def _closeout_hash_basis(
    closeout: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "closeout_id": closeout["closeout_id"],
        "app_id": closeout["app_id"],
        "stage_id": closeout["stage_id"],
        "closeout_version": closeout["closeout_version"],
        "readiness_mode": closeout["readiness_mode"],
        "source_review_packet_id": (
            closeout["source_review_packet_id"]
        ),
        "source_operator_handoff_id": (
            closeout["source_operator_handoff_id"]
        ),
        "overall_status": closeout["overall_status"],
        "implementation_status": (
            closeout["implementation_status"]
        ),
        "handoff_status": closeout["handoff_status"],
        "target_consumers": closeout["target_consumers"],
        "review_packet_snapshot": (
            closeout["review_packet_snapshot"]
        ),
        "operator_handoff_snapshot": (
            closeout["operator_handoff_snapshot"]
        ),
    }


def build_final_readiness_closeout(
    *,
    closeout_id: str,
    review_packet: Mapping[str, Any],
    operator_handoff: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the immutable readiness-only D6 closeout."""
    if not _valid_identifier(closeout_id):
        raise FinalCloseoutViolation("closeout_id_invalid")

    packet_errors = validate_runtime_readiness_review_packet(
        review_packet
    )
    if packet_errors:
        raise FinalCloseoutViolation(
            "invalid_review_packet:" + ";".join(packet_errors)
        )

    handoff_errors = validate_operator_handoff(
        operator_handoff
    )
    if handoff_errors:
        raise FinalCloseoutViolation(
            "invalid_operator_handoff:"
            + ";".join(handoff_errors)
        )

    if operator_handoff["source_review_packet_id"] != (
        review_packet["review_packet_id"]
    ):
        raise FinalCloseoutViolation(
            "operator_handoff_review_packet_linkage_invalid"
        )

    if operator_handoff["overall_status"] != (
        review_packet["overall_status"]
    ):
        raise FinalCloseoutViolation(
            "operator_handoff_overall_status_mismatch"
        )

    packet_snapshot = copy.deepcopy(dict(review_packet))
    handoff_snapshot = copy.deepcopy(dict(operator_handoff))
    overall_status = str(review_packet["overall_status"])

    closeout: dict[str, Any] = {
        "closeout_id": closeout_id,
        "closeout_hash": "",
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "closeout_version": FINAL_CLOSEOUT_VERSION,
        "readiness_mode": READINESS_MODE,
        "source_review_packet_id": (
            review_packet["review_packet_id"]
        ),
        "source_operator_handoff_id": (
            operator_handoff["handoff_id"]
        ),
        "overall_status": overall_status,
        "implementation_status": "D1_D6_IMPLEMENTED",
        "handoff_status": _handoff_status(overall_status),
        "target_consumers": list(FINAL_CLOSEOUT_TARGETS),
        "review_packet_snapshot": packet_snapshot,
        "operator_handoff_snapshot": handoff_snapshot,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "main_merge_authorization_status": "NOT_GRANTED",
        "control_center_sync_status": "NOT_STARTED",
        "final_current_state_status": "NOT_STARTED",
        "manual_archive_authorization_status": "NOT_GRANTED",
        "automatic_archive_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "automatic_policy_activation_status": "NOT_ALLOWED",
        "automatic_learning_activation_status": "NOT_ALLOWED",
        "automatic_champion_promotion_status": "NOT_ALLOWED",
        "shadow_trading_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "real_execution_status": "NOT_ALLOWED",
        "trading_api_status": "NOT_ALLOWED",
        "trading_credential_access_status": "NOT_ALLOWED",
        "core_mutation_status": "NOT_ALLOWED",
        "p48_expansion_status": "NOT_ALLOWED",
        "tag_status": "NONE",
        "release_status": "NONE",
        "deploy_status": "NONE",
        "safety_flags": _safety_flags(),
    }

    closeout["closeout_hash"] = _canonical_hash(
        _closeout_hash_basis(closeout)
    )
    return closeout


def validate_final_readiness_closeout(
    closeout: object,
) -> list[str]:
    """Return deterministic D6 closeout validation errors."""
    if not isinstance(closeout, Mapping):
        return ["final_closeout_must_be_mapping"]

    errors: list[str] = []

    if set(closeout.keys()) != set(
        REQUIRED_FINAL_CLOSEOUT_FIELDS
    ):
        errors.append("final_closeout_fields_must_match_schema")

    expected = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "closeout_version": FINAL_CLOSEOUT_VERSION,
        "readiness_mode": READINESS_MODE,
        "implementation_status": "D1_D6_IMPLEMENTED",
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "main_merge_authorization_status": "NOT_GRANTED",
        "control_center_sync_status": "NOT_STARTED",
        "final_current_state_status": "NOT_STARTED",
        "manual_archive_authorization_status": "NOT_GRANTED",
        "automatic_archive_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "automatic_policy_activation_status": "NOT_ALLOWED",
        "automatic_learning_activation_status": "NOT_ALLOWED",
        "automatic_champion_promotion_status": "NOT_ALLOWED",
        "shadow_trading_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "real_execution_status": "NOT_ALLOWED",
        "trading_api_status": "NOT_ALLOWED",
        "trading_credential_access_status": "NOT_ALLOWED",
        "core_mutation_status": "NOT_ALLOWED",
        "p48_expansion_status": "NOT_ALLOWED",
        "tag_status": "NONE",
        "release_status": "NONE",
        "deploy_status": "NONE",
    }
    for field, value in expected.items():
        if closeout.get(field) != value:
            errors.append(f"{field}_invalid")

    for field in (
        "closeout_id",
        "source_review_packet_id",
        "source_operator_handoff_id",
    ):
        if not _valid_identifier(closeout.get(field)):
            errors.append(f"{field}_invalid")

    closeout_hash = closeout.get("closeout_hash")
    if (
        not isinstance(closeout_hash, str)
        or _HASH_PATTERN.fullmatch(closeout_hash) is None
    ):
        errors.append("closeout_hash_invalid")

    if closeout.get("target_consumers") != list(
        FINAL_CLOSEOUT_TARGETS
    ):
        errors.append("target_consumers_invalid")

    packet = closeout.get("review_packet_snapshot")
    handoff = closeout.get("operator_handoff_snapshot")

    if not isinstance(packet, Mapping):
        errors.append("review_packet_snapshot_invalid")
        packet = {}

    if not isinstance(handoff, Mapping):
        errors.append("operator_handoff_snapshot_invalid")
        handoff = {}

    if packet:
        packet_errors = (
            validate_runtime_readiness_review_packet(packet)
        )
        if packet_errors:
            errors.append("review_packet_snapshot_invalid")

    if handoff:
        handoff_errors = validate_operator_handoff(handoff)
        if handoff_errors:
            errors.append("operator_handoff_snapshot_invalid")

    if packet and handoff:
        if closeout.get("source_review_packet_id") != (
            packet.get("review_packet_id")
        ):
            errors.append("review_packet_id_mismatch")

        if closeout.get("source_operator_handoff_id") != (
            handoff.get("handoff_id")
        ):
            errors.append("operator_handoff_id_mismatch")

        if handoff.get("source_review_packet_id") != (
            packet.get("review_packet_id")
        ):
            errors.append(
                "operator_handoff_review_packet_linkage_invalid"
            )

        if handoff.get("overall_status") != packet.get(
            "overall_status"
        ):
            errors.append("snapshot_overall_status_mismatch")

        if closeout.get("overall_status") != packet.get(
            "overall_status"
        ):
            errors.append("overall_status_mismatch")

    overall_status = closeout.get("overall_status")
    if overall_status not in (
        "READY_FOR_OPERATOR_REVIEW",
        "BLOCKED",
        "DEGRADED",
    ):
        errors.append("overall_status_invalid")
    elif closeout.get("handoff_status") != _handoff_status(
        str(overall_status)
    ):
        errors.append("handoff_status_invalid")

    if closeout.get("handoff_status") not in (
        FINAL_HANDOFF_STATUSES
    ):
        errors.append("handoff_status_not_supported")

    if set(REQUIRED_FINAL_CLOSEOUT_FIELDS).issubset(
        closeout.keys()
    ):
        expected_hash = _canonical_hash(
            _closeout_hash_basis(closeout)
        )
        if closeout.get("closeout_hash") != expected_hash:
            errors.append("closeout_hash_mismatch")

    errors.extend(
        _validate_safety_flags(closeout.get("safety_flags"))
    )

    for field in FORBIDDEN_ACTION_FIELDS:
        if field in closeout:
            errors.append(f"forbidden_action_field:{field}")

    return errors
