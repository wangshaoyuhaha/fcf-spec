"""Artifact lifecycle snapshot index for ARTIFACT-LIFECYCLE-D3."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from .contract import validate_lifecycle_record


def build_artifact_state_snapshot(
    record: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build one read-only lifecycle state snapshot."""

    validation = validate_lifecycle_record(record)

    return {
        "artifact_id": record.get("artifact_id"),
        "artifact_type": record.get("artifact_type"),
        "artifact_path": record.get("artifact_path"),
        "lifecycle_status": record.get("lifecycle_status"),
        "result_status": validation["result_status"],
        "validation": deepcopy(validation),
        "read_only": True,
        "index_only": True,
        "snapshot_only": True,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }


def build_artifact_state_snapshot_index(
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build read-only lifecycle state snapshots for existing artifacts."""

    snapshots: List[Dict[str, Any]] = []
    status_counts: Dict[str, int] = {
        "OBSERVED": 0,
        "INCOMPLETE": 0,
        "STALE": 0,
        "UNRESOLVED": 0,
    }

    for record in records:
        snapshot = build_artifact_state_snapshot(record)
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
    else:
        snapshot_index_status = "OBSERVED"

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
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }
