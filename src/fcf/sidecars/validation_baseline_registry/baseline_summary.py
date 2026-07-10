"""Validation baseline summary for VALIDATION-BASELINE-D4."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping


def build_validation_baseline_summary(
    *,
    snapshot_index: Mapping[str, Any],
    run_index: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build a read-only validation baseline summary."""

    if not isinstance(snapshot_index, Mapping):
        raise ValueError("snapshot_index is required")
    if not isinstance(run_index, Mapping):
        raise ValueError("run_index is required")

    snapshot_status = snapshot_index.get("snapshot_index_status", "UNRESOLVED")
    run_status = run_index.get("run_index_status", "UNRESOLVED")

    allowed_snapshot = ("VERIFIED", "REGISTERED", "INCOMPLETE", "STALE", "UNRESOLVED")
    allowed_run = ("VERIFIED", "REGISTERED", "INCOMPLETE", "STALE", "UNRESOLVED")

    if snapshot_status not in allowed_snapshot:
        snapshot_status = "UNRESOLVED"
    if run_status not in allowed_run:
        run_status = "UNRESOLVED"

    unresolved_count = (
        snapshot_index.get("status_counts", {}).get("UNRESOLVED", 0)
        + run_index.get("status_counts", {}).get("UNRESOLVED", 0)
    )
    stale_count = (
        snapshot_index.get("status_counts", {}).get("STALE", 0)
        + run_index.get("status_counts", {}).get("STALE", 0)
    )
    incomplete_count = (
        snapshot_index.get("status_counts", {}).get("INCOMPLETE", 0)
        + run_index.get("status_counts", {}).get("INCOMPLETE", 0)
    )
    verified_count = (
        snapshot_index.get("status_counts", {}).get("VERIFIED", 0)
        + run_index.get("status_counts", {}).get("VERIFIED", 0)
    )

    if snapshot_status == "UNRESOLVED" or run_status == "UNRESOLVED":
        summary_status = "UNRESOLVED"
        summary_action = "MARK_UNRESOLVED"
    elif snapshot_status == "STALE" or run_status == "STALE":
        summary_status = "STALE"
        summary_action = "MARK_STALE"
    elif snapshot_status == "INCOMPLETE" or run_status == "INCOMPLETE":
        summary_status = "INCOMPLETE"
        summary_action = "MARK_INCOMPLETE"
    elif snapshot_status == "VERIFIED" or run_status == "VERIFIED":
        summary_status = "VERIFIED"
        summary_action = "QUEUE_OPERATOR_REVIEW"
    else:
        summary_status = "REGISTERED"
        summary_action = "QUEUE_OPERATOR_REVIEW"

    return {
        "stage": "D4",
        "summary_status": summary_status,
        "summary_action": summary_action,
        "snapshot_index_status": snapshot_status,
        "run_index_status": run_status,
        "snapshot_count": snapshot_index.get("snapshot_count", 0),
        "run_record_count": run_index.get("record_count", 0),
        "unresolved_count": unresolved_count,
        "stale_count": stale_count,
        "incomplete_count": incomplete_count,
        "verified_count": verified_count,
        "snapshot_index": deepcopy(dict(snapshot_index)),
        "run_index": deepcopy(dict(run_index)),
        "read_only": True,
        "index_only": True,
        "summary_only": True,
        "sidecar_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
        "ui_dashboard_panel_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def classify_validation_baseline_summary(
    summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Classify summary state without repair, fabrication, or auto-pass."""

    status = summary.get("summary_status", "UNRESOLVED")

    if status in ("VERIFIED", "REGISTERED"):
        action = "QUEUE_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        action = "MARK_INCOMPLETE"
    elif status == "STALE":
        action = "MARK_STALE"
    else:
        action = "MARK_UNRESOLVED"

    return {
        "stage": "D4",
        "summary_status": status,
        "summary_action": action,
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
