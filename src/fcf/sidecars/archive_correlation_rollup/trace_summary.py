"""Trace summary for ARCHIVE-CORRELATION-D4."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from .contract import CORRELATION_ROLLUP_REQUIRED_LINKS


def build_trace_summary(matrix_packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a read-only trace summary from an existing coverage matrix."""

    correlation_id = matrix_packet.get("correlation_id")
    if not correlation_id:
        raise ValueError("correlation_id is required")

    coverage_matrix = matrix_packet.get("coverage_matrix")
    if not isinstance(coverage_matrix, Mapping):
        raise ValueError("coverage_matrix is required")

    link_summaries = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        row = coverage_matrix.get(link_type)
        if row is None:
            link_summaries.append(
                {
                    "link_type": link_type,
                    "status": "INCOMPLETE",
                    "covered": False,
                    "artifact_count": 0,
                    "issues": ["MISSING_LINK"],
                }
            )
            continue

        link_summaries.append(
            {
                "link_type": link_type,
                "status": row.get("status", "UNRESOLVED"),
                "covered": row.get("covered") is True,
                "artifact_count": len(row.get("artifact_ids", [])),
                "issues": list(row.get("issues", [])),
            }
        )

    missing_links = list(matrix_packet.get("missing_links", []))
    stale_links = list(matrix_packet.get("stale_links", []))
    unresolved_issues = list(matrix_packet.get("unresolved_issues", []))
    covered_links = list(matrix_packet.get("covered_links", []))

    return {
        "correlation_id": correlation_id,
        "rollup_status": matrix_packet.get("rollup_status", "UNRESOLVED"),
        "required_link_count": len(CORRELATION_ROLLUP_REQUIRED_LINKS),
        "covered_link_count": len(covered_links),
        "missing_link_count": len(missing_links),
        "stale_link_count": len(stale_links),
        "unresolved_issue_count": len(unresolved_issues),
        "link_summaries": link_summaries,
        "missing_links": missing_links,
        "stale_links": stale_links,
        "unresolved_issues": unresolved_issues,
        "read_only": True,
        "index_only": True,
        "summary_only": True,
        "source_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }


def classify_trace_summary(summary_packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify trace state without auto-passing or repairing anything."""

    status = summary_packet.get("rollup_status", "UNRESOLVED")

    if status == "COMPLETE":
        action = "READY_FOR_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        action = "MARK_INCOMPLETE"
    elif status == "STALE":
        action = "MARK_STALE"
    else:
        action = "MARK_UNRESOLVED"

    return {
        "correlation_id": summary_packet.get("correlation_id"),
        "rollup_status": status,
        "trace_action": action,
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "read_only": True,
    }
