"""Registry summary for ARTIFACT-LIFECYCLE-D4."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping


def build_lifecycle_registry_summary(
    *,
    snapshot_index: Mapping[str, Any],
    transition_index: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build a read-only summary from snapshot and transition indexes."""

    if not isinstance(snapshot_index, Mapping):
        raise ValueError("snapshot_index is required")
    if not isinstance(transition_index, Mapping):
        raise ValueError("transition_index is required")

    snapshot_status = snapshot_index.get("snapshot_index_status", "UNRESOLVED")
    transition_status = transition_index.get("index_status", "UNRESOLVED")

    if snapshot_status not in ("OBSERVED", "INCOMPLETE", "STALE", "UNRESOLVED"):
        snapshot_status = "UNRESOLVED"

    if transition_status not in ("OBSERVED", "NO_CHANGE", "UNRESOLVED"):
        transition_status = "UNRESOLVED"

    if snapshot_status == "UNRESOLVED" or transition_status == "UNRESOLVED":
        registry_summary_status = "UNRESOLVED"
        registry_action = "MARK_UNRESOLVED"
    elif snapshot_status == "STALE":
        registry_summary_status = "STALE"
        registry_action = "MARK_STALE"
    elif snapshot_status == "INCOMPLETE":
        registry_summary_status = "INCOMPLETE"
        registry_action = "MARK_INCOMPLETE"
    else:
        registry_summary_status = "OBSERVED"
        registry_action = "QUEUE_OPERATOR_REVIEW"

    return {
        "stage": "D4",
        "registry_summary_status": registry_summary_status,
        "registry_action": registry_action,
        "snapshot_index_status": snapshot_status,
        "transition_index_status": transition_status,
        "snapshot_count": snapshot_index.get("snapshot_count", 0),
        "transition_count": transition_index.get("transition_count", 0),
        "unresolved_count": (
            snapshot_index.get("status_counts", {}).get("UNRESOLVED", 0)
            + transition_index.get("unresolved_count", 0)
        ),
        "stale_count": snapshot_index.get("status_counts", {}).get("STALE", 0),
        "incomplete_count": snapshot_index.get("status_counts", {}).get(
            "INCOMPLETE",
            0,
        ),
        "snapshot_index": deepcopy(dict(snapshot_index)),
        "transition_index": deepcopy(dict(transition_index)),
        "read_only": True,
        "index_only": True,
        "summary_only": True,
        "sidecar_only": True,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "transition_applied": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def classify_lifecycle_registry_summary(
    summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Classify summary state without repair, mutation, or auto-pass."""

    status = summary.get("registry_summary_status", "UNRESOLVED")

    if status == "OBSERVED":
        action = "QUEUE_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        action = "MARK_INCOMPLETE"
    elif status == "STALE":
        action = "MARK_STALE"
    else:
        action = "MARK_UNRESOLVED"

    return {
        "stage": "D4",
        "registry_summary_status": status,
        "registry_action": action,
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "transition_applied": False,
        "evidence_backfill_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
