"""Final governed handoff for AI prompt and model version records."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .contract import APP_ID, CONTRACT_VERSION
from .review_packet import (
    validate_version_governance_review_packet,
)

HANDOFF_TARGETS = (
    "AI-CONTEXT-EVIDENCE-CONTRACT-APP-1",
    "MODEL-GOVERNANCE-APP-1",
    "OPERATOR-REVIEW-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "VALIDATION-BASELINE-REGISTRY-APP-1",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "handoff_hash",
    "app_id",
    "contract_version",
    "handoff_status",
    "source_review_packet_id",
    "source_review_packet_hash",
    "source_compatibility_report_id",
    "source_compatibility_report_hash",
    "compatible_for_paper_review",
    "registry_entry_ids",
    "selected_versions",
    "finding_count",
    "open_finding_ids",
    "highest_severity",
    "target_consumers",
    "review_packet_snapshot",
    "human_review_required",
    "operator_review_bypass_allowed",
    "automatic_approval_allowed",
    "automatic_activation_allowed",
    "automatic_promotion_allowed",
    "automatic_rollback_allowed",
    "model_execution_allowed",
    "archive_required",
    "source_mutation_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
)

FORBIDDEN_ACTION_FIELDS = (
    "buy",
    "sell",
    "order",
    "execute",
    "position_size",
    "portfolio_action",
    "trade_instruction",
    "deployment_instruction",
    "activation_instruction",
    "promotion_instruction",
    "rollback_instruction",
)


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing_or_invalid_field:{field}")
    return value.strip()


def build_final_handoff(
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the immutable paper-only final governance handoff."""
    if not isinstance(review_packet, Mapping):
        raise TypeError("review_packet_must_be_mapping")

    packet_errors = validate_version_governance_review_packet(
        review_packet
    )
    if packet_errors:
        raise ValueError(
            "invalid_review_packet:"
            + ",".join(sorted(packet_errors))
        )

    packet_snapshot = copy.deepcopy(dict(review_packet))

    packet_id = _require_text(
        packet_snapshot.get("review_packet_id"),
        "review_packet_id",
    )
    packet_hash = _require_text(
        packet_snapshot.get("review_packet_hash"),
        "review_packet_hash",
    )
    report_id = _require_text(
        packet_snapshot.get(
            "source_compatibility_report_id"
        ),
        "source_compatibility_report_id",
    )
    report_hash = _require_text(
        packet_snapshot.get(
            "source_compatibility_report_hash"
        ),
        "source_compatibility_report_hash",
    )

    registry_entry_ids = packet_snapshot.get(
        "registry_entry_ids"
    )
    if not isinstance(registry_entry_ids, list) or not (
        registry_entry_ids
    ):
        raise ValueError("invalid_registry_entry_ids")

    selected_versions = packet_snapshot.get(
        "selected_versions"
    )
    if not isinstance(selected_versions, Mapping):
        raise ValueError("invalid_selected_versions")

    handoff_basis = {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "source_review_packet_id": packet_id,
        "source_review_packet_hash": packet_hash,
        "source_compatibility_report_id": report_id,
        "source_compatibility_report_hash": report_hash,
        "registry_entry_ids": list(registry_entry_ids),
        "selected_versions": copy.deepcopy(
            dict(selected_versions)
        ),
        "finding_count": packet_snapshot["finding_count"],
        "open_finding_ids": packet_snapshot[
            "open_finding_ids"
        ],
        "target_consumers": list(HANDOFF_TARGETS),
    }

    handoff_hash = _canonical_hash(handoff_basis)

    return {
        "handoff_id": (
            f"version-registry-handoff-{handoff_hash[:20]}"
        ),
        "handoff_hash": handoff_hash,
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "handoff_status": "WAITING_FOR_OPERATOR_REVIEW",
        "source_review_packet_id": packet_id,
        "source_review_packet_hash": packet_hash,
        "source_compatibility_report_id": report_id,
        "source_compatibility_report_hash": report_hash,
        "compatible_for_paper_review": packet_snapshot[
            "compatible_for_paper_review"
        ],
        "registry_entry_ids": copy.deepcopy(
            registry_entry_ids
        ),
        "selected_versions": copy.deepcopy(
            dict(selected_versions)
        ),
        "finding_count": packet_snapshot["finding_count"],
        "open_finding_ids": copy.deepcopy(
            packet_snapshot["open_finding_ids"]
        ),
        "highest_severity": packet_snapshot[
            "highest_severity"
        ],
        "target_consumers": list(HANDOFF_TARGETS),
        "review_packet_snapshot": packet_snapshot,
        "human_review_required": True,
        "operator_review_bypass_allowed": False,
        "automatic_approval_allowed": False,
        "automatic_activation_allowed": False,
        "automatic_promotion_allowed": False,
        "automatic_rollback_allowed": False,
        "model_execution_allowed": False,
        "archive_required": True,
        "source_mutation_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "credential_access_allowed": False,
        "api_key_access_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
    }


def validate_final_handoff(
    handoff: Mapping[str, Any],
) -> list[str]:
    """Validate the final handoff without modifying it."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_HANDOFF_FIELDS:
        if field not in handoff:
            errors.append(f"missing_field:{field}")

    if handoff.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if handoff.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    if handoff.get("handoff_status") != (
        "WAITING_FOR_OPERATOR_REVIEW"
    ):
        errors.append("invalid_handoff_status")

    if handoff.get("target_consumers") != list(
        HANDOFF_TARGETS
    ):
        errors.append("invalid_target_consumers")

    snapshot = handoff.get("review_packet_snapshot")
    if not isinstance(snapshot, Mapping):
        errors.append("invalid_review_packet_snapshot")
    else:
        packet_errors = (
            validate_version_governance_review_packet(
                snapshot
            )
        )
        if packet_errors:
            errors.append("invalid_review_packet_snapshot")

        if handoff.get("source_review_packet_id") != (
            snapshot.get("review_packet_id")
        ):
            errors.append("review_packet_id_mismatch")

        if handoff.get("source_review_packet_hash") != (
            snapshot.get("review_packet_hash")
        ):
            errors.append("review_packet_hash_mismatch")

        if handoff.get("finding_count") != snapshot.get(
            "finding_count"
        ):
            errors.append("finding_count_mismatch")

        if handoff.get(
            "compatible_for_paper_review"
        ) != snapshot.get("compatible_for_paper_review"):
            errors.append("compatibility_state_mismatch")

    if handoff.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if handoff.get(
        "operator_review_bypass_allowed"
    ) is not False:
        errors.append("operator_review_bypass_not_blocked")

    if handoff.get("automatic_approval_allowed") is not False:
        errors.append("automatic_approval_not_blocked")

    if handoff.get(
        "automatic_activation_allowed"
    ) is not False:
        errors.append("automatic_activation_not_blocked")

    if handoff.get(
        "automatic_promotion_allowed"
    ) is not False:
        errors.append("automatic_promotion_not_blocked")

    if handoff.get(
        "automatic_rollback_allowed"
    ) is not False:
        errors.append("automatic_rollback_not_blocked")

    if handoff.get("model_execution_allowed") is not False:
        errors.append("model_execution_not_blocked")

    if handoff.get("archive_required") is not True:
        errors.append("archive_not_required")

    if handoff.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if handoff.get("core_mutation_allowed") is not False:
        errors.append("core_mutation_not_blocked")

    if handoff.get(
        "p48_core_expansion_allowed"
    ) is not False:
        errors.append("p48_core_expansion_not_blocked")

    if handoff.get("real_trading_allowed") is not False:
        errors.append("real_trading_not_blocked")

    if handoff.get("real_execution_allowed") is not False:
        errors.append("real_execution_not_blocked")

    for field in FORBIDDEN_ACTION_FIELDS:
        if field in handoff:
            errors.append(f"forbidden_action_field:{field}")

    return errors
