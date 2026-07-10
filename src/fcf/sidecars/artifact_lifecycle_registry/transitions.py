"""Lifecycle transition policy for ARTIFACT-LIFECYCLE-D2."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Tuple

from .contract import ALLOWED_LIFECYCLE_STATUSES

ALLOWED_LIFECYCLE_TRANSITIONS: Tuple[Tuple[str, str], ...] = (
    ("REGISTERED", "OBSERVED"),
    ("REGISTERED", "INCOMPLETE"),
    ("REGISTERED", "STALE"),
    ("REGISTERED", "UNRESOLVED"),
    ("OBSERVED", "STALE"),
    ("OBSERVED", "INCOMPLETE"),
    ("OBSERVED", "UNRESOLVED"),
    ("INCOMPLETE", "STALE"),
    ("INCOMPLETE", "UNRESOLVED"),
    ("STALE", "UNRESOLVED"),
)


def validate_lifecycle_transition(
    *,
    artifact_id: str,
    from_status: str,
    to_status: str,
    reason_code: str,
) -> Dict[str, Any]:
    """Validate one lifecycle transition without applying it."""

    issues = []

    if not artifact_id:
        issues.append("MISSING_ARTIFACT_ID")

    if from_status not in ALLOWED_LIFECYCLE_STATUSES:
        issues.append("UNSUPPORTED_FROM_STATUS")

    if to_status not in ALLOWED_LIFECYCLE_STATUSES:
        issues.append("UNSUPPORTED_TO_STATUS")

    if not reason_code:
        issues.append("MISSING_REASON_CODE")

    if (
        from_status in ALLOWED_LIFECYCLE_STATUSES
        and to_status in ALLOWED_LIFECYCLE_STATUSES
        and from_status != to_status
        and (from_status, to_status) not in ALLOWED_LIFECYCLE_TRANSITIONS
    ):
        issues.append("TRANSITION_NOT_ALLOWED")

    if from_status == to_status:
        transition_state = "NO_CHANGE"
    elif issues:
        transition_state = "UNRESOLVED"
    else:
        transition_state = "VALID_TRANSITION"

    return {
        "artifact_id": artifact_id,
        "from_status": from_status,
        "to_status": to_status,
        "reason_code": reason_code,
        "transition_state": transition_state,
        "valid": not issues,
        "issues": issues,
        "read_only": True,
        "index_only": True,
        "transition_applied": False,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "operator_review_required": True,
        "auto_pass_allowed": False,
    }


def build_transition_index(
    transitions: Tuple[Mapping[str, Any], ...],
) -> Dict[str, Any]:
    """Build a read-only index of requested lifecycle transitions."""

    indexed = []
    unresolved_count = 0
    no_change_count = 0
    valid_count = 0

    for item in transitions:
        result = validate_lifecycle_transition(
            artifact_id=str(item.get("artifact_id", "")),
            from_status=str(item.get("from_status", "")),
            to_status=str(item.get("to_status", "")),
            reason_code=str(item.get("reason_code", "")),
        )

        if result["transition_state"] == "UNRESOLVED":
            unresolved_count += 1
        elif result["transition_state"] == "NO_CHANGE":
            no_change_count += 1
        elif result["transition_state"] == "VALID_TRANSITION":
            valid_count += 1

        indexed.append(result)

    if unresolved_count:
        index_status = "UNRESOLVED"
    elif no_change_count and valid_count == 0:
        index_status = "NO_CHANGE"
    else:
        index_status = "OBSERVED"

    return {
        "stage": "D2",
        "index_status": index_status,
        "transition_count": len(indexed),
        "valid_transition_count": valid_count,
        "no_change_count": no_change_count,
        "unresolved_count": unresolved_count,
        "transitions": indexed,
        "read_only": True,
        "index_only": True,
        "sidecar_only": True,
        "transition_applied": False,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "operator_review_required": True,
        "auto_pass_allowed": False,
    }
