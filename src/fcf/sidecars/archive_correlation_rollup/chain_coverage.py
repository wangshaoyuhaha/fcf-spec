"""Correlation chain coverage matrix for ARCHIVE-CORRELATION-D3."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from .contract import CORRELATION_ROLLUP_REQUIRED_LINKS
from .source_references import validate_artifact_reference


def build_chain_coverage_matrix(
    *,
    correlation_id: str,
    references: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only coverage matrix for one correlation_id."""

    if not correlation_id:
        raise ValueError("correlation_id is required")

    matrix: Dict[str, Dict[str, Any]] = {}
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        matrix[link_type] = {
            "link_type": link_type,
            "covered": False,
            "status": "INCOMPLETE",
            "artifact_ids": [],
            "artifact_paths": [],
            "issues": ["MISSING_LINK"],
        }

    unresolved_issues: List[str] = []
    stale_links: List[str] = []

    for raw_reference in references:
        reference = deepcopy(dict(raw_reference))
        link_type = reference.get("link_type")

        if link_type not in matrix:
            unresolved_issues.append("UNSUPPORTED_LINK_TYPE")
            continue

        if reference.get("correlation_id") != correlation_id:
            matrix[link_type]["issues"] = ["CORRELATION_ID_MISMATCH"]
            unresolved_issues.append("CORRELATION_ID_MISMATCH")
            continue

        validation = validate_artifact_reference(reference)
        artifact_id = reference.get("artifact_id")
        artifact_path = reference.get("artifact_path")
        source_status = reference.get("status")

        matrix[link_type]["artifact_ids"].append(artifact_id)
        matrix[link_type]["artifact_paths"].append(artifact_path)

        if validation["valid"] and source_status == "PRESENT":
            matrix[link_type]["covered"] = True
            matrix[link_type]["status"] = "PRESENT"
            matrix[link_type]["issues"] = []
        elif source_status == "STALE":
            matrix[link_type]["covered"] = False
            matrix[link_type]["status"] = "STALE"
            matrix[link_type]["issues"] = validation["issues"] or ["STALE_REFERENCE"]
            stale_links.append(link_type)
        else:
            matrix[link_type]["covered"] = False
            matrix[link_type]["status"] = "UNRESOLVED"
            matrix[link_type]["issues"] = validation["issues"] or ["UNRESOLVED_REFERENCE"]
            unresolved_issues.extend(matrix[link_type]["issues"])

    missing_links = []
    covered_links = []

    for link_type, row in matrix.items():
        if row["status"] == "INCOMPLETE":
            missing_links.append(link_type)
        if row["covered"] is True:
            covered_links.append(link_type)

    if stale_links:
        rollup_status = "STALE"
    elif unresolved_issues:
        rollup_status = "UNRESOLVED"
    elif missing_links:
        rollup_status = "INCOMPLETE"
    else:
        rollup_status = "COMPLETE"

    return {
        "correlation_id": correlation_id,
        "rollup_status": rollup_status,
        "coverage_matrix": matrix,
        "covered_links": covered_links,
        "missing_links": missing_links,
        "stale_links": sorted(set(stale_links)),
        "unresolved_issues": sorted(set(unresolved_issues)),
        "read_only": True,
        "index_only": True,
        "source_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }


def summarize_chain_coverage(matrix_packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Summarize coverage without changing source evidence."""

    coverage_matrix = matrix_packet["coverage_matrix"]
    total_required = len(CORRELATION_ROLLUP_REQUIRED_LINKS)
    covered_count = 0

    for row in coverage_matrix.values():
        if row["covered"] is True:
            covered_count += 1

    return {
        "correlation_id": matrix_packet["correlation_id"],
        "rollup_status": matrix_packet["rollup_status"],
        "total_required_links": total_required,
        "covered_link_count": covered_count,
        "missing_link_count": len(matrix_packet["missing_links"]),
        "stale_link_count": len(matrix_packet["stale_links"]),
        "unresolved_issue_count": len(matrix_packet["unresolved_issues"]),
        "coverage_ratio": covered_count / total_required,
        "read_only": True,
        "index_only": True,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }

