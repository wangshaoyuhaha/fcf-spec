"""Validation baseline snapshot index for VALIDATION-BASELINE-D3."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from .validation_runs import validate_validation_run_record


def build_validation_baseline_snapshot(
    record: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build one read-only validation baseline snapshot."""

    validation = validate_validation_run_record(record)

    return {
        "validation_id": record.get("validation_id"),
        "command": record.get("command"),
        "result": record.get("result"),
        "pass_count": record.get("pass_count"),
        "git_branch": record.get("git_branch"),
        "git_head": record.get("git_head"),
        "git_status": record.get("git_status"),
        "origin_status": record.get("origin_status"),
        "baseline_status": record.get("baseline_status", "REGISTERED"),
        "output_summary": record.get("output_summary"),
        "result_status": validation["result_status"],
        "validation": deepcopy(validation),
        "read_only": True,
        "index_only": True,
        "snapshot_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }


def build_validation_baseline_snapshot_index(
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only validation baseline snapshot index."""

    snapshots: List[Dict[str, Any]] = []
    status_counts: Dict[str, int] = {
        "VERIFIED": 0,
        "REGISTERED": 0,
        "INCOMPLETE": 0,
        "STALE": 0,
        "UNRESOLVED": 0,
    }

    for record in records:
        snapshot = build_validation_baseline_snapshot(record)
        result_status = snapshot["result_status"]
        if result_status not in status_counts:
            result_status = "UNRESOLVED"
        status_counts[result_status] += 1
        snapshots.append(snapshot)

    if status_counts["UNRESOLVED"]:
        snapshot_index_status = "UNRESOLVED"
    elif status_counts["STALE"]:
        snapshot_index_status = "STALE"
    elif status_counts["INCOMPLETE"]:
        snapshot_index_status = "INCOMPLETE"
    elif status_counts["VERIFIED"]:
        snapshot_index_status = "VERIFIED"
    else:
        snapshot_index_status = "REGISTERED"

    return {
        "stage": "D3",
        "snapshot_index_status": snapshot_index_status,
        "snapshot_count": len(snapshots),
        "status_counts": status_counts,
        "snapshots": snapshots,
        "read_only": True,
        "index_only": True,
        "snapshot_only": True,
        "sidecar_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }
