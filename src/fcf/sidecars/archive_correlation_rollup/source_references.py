"""Read-only source artifact references for ARCHIVE-CORRELATION-D2."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from .contract import CORRELATION_ROLLUP_REQUIRED_LINKS

ARTIFACT_REFERENCE_STATUS = (
    "PRESENT",
    "INCOMPLETE",
    "STALE",
    "UNRESOLVED",
)

_REQUIRED_REFERENCE_FIELDS = (
    "link_type",
    "artifact_id",
    "artifact_path",
    "correlation_id",
    "status",
)


def build_artifact_reference(
    *,
    link_type: str,
    artifact_id: str,
    artifact_path: str,
    correlation_id: str | None,
    status: str,
    source_stage: str | None = None,
    checksum_sha256: str | None = None,
    observed_at_utc: str | None = None,
    notes: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Build a read-only source artifact reference.

    This function records metadata only. It does not read, mutate, create,
    backfill, or repair the source artifact.
    """

    if link_type not in CORRELATION_ROLLUP_REQUIRED_LINKS:
        raise ValueError(f"unsupported link_type: {link_type}")

    if status not in ARTIFACT_REFERENCE_STATUS:
        raise ValueError(f"unsupported status: {status}")

    if status == "PRESENT" and not correlation_id:
        raise ValueError("PRESENT reference requires correlation_id")

    if not artifact_id:
        raise ValueError("artifact_id is required")

    if not artifact_path:
        raise ValueError("artifact_path is required")

    return {
        "link_type": link_type,
        "artifact_id": artifact_id,
        "artifact_path": artifact_path,
        "correlation_id": correlation_id,
        "status": status,
        "source_stage": source_stage,
        "checksum_sha256": checksum_sha256,
        "observed_at_utc": observed_at_utc,
        "notes": list(notes or []),
        "read_only": True,
        "source_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_generation_allowed": False,
    }


def validate_artifact_reference(reference: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one artifact reference and return a mark-only result."""

    missing_fields: List[str] = [
        field for field in _REQUIRED_REFERENCE_FIELDS if field not in reference
    ]

    issues: List[str] = []
    if missing_fields:
        issues.append("MISSING_REQUIRED_FIELDS")

    link_type = reference.get("link_type")
    if link_type not in CORRELATION_ROLLUP_REQUIRED_LINKS:
        issues.append("UNSUPPORTED_LINK_TYPE")

    status = reference.get("status")
    if status not in ARTIFACT_REFERENCE_STATUS:
        issues.append("UNSUPPORTED_STATUS")

    if status == "PRESENT" and not reference.get("correlation_id"):
        issues.append("PRESENT_WITHOUT_CORRELATION_ID")

    if reference.get("source_mutation_allowed") is True:
        issues.append("SOURCE_MUTATION_NOT_ALLOWED")

    if reference.get("evidence_backfill_allowed") is True:
        issues.append("EVIDENCE_BACKFILL_NOT_ALLOWED")

    if reference.get("correlation_id_auto_fill_allowed") is True:
        issues.append("CORRELATION_ID_AUTO_FILL_NOT_ALLOWED")

    if reference.get("placeholder_generation_allowed") is True:
        issues.append("PLACEHOLDER_GENERATION_NOT_ALLOWED")

    result_status = "PRESENT" if not issues and status == "PRESENT" else "UNRESOLVED"

    return {
        "valid": not issues,
        "status": result_status,
        "issues": issues,
        "read_only": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
    }


def build_reference_index(
    references: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only index grouped by required rollup link type."""

    index: Dict[str, List[Dict[str, Any]]] = {
        link_type: [] for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS
    }
    validation_results: List[Dict[str, Any]] = []

    for reference in references:
        copied = deepcopy(dict(reference))
        validation = validate_artifact_reference(copied)
        validation_results.append(validation)

        link_type = copied.get("link_type")
        if link_type in index:
            index[link_type].append(copied)

    missing_link_types = [
        link_type for link_type, items in index.items() if not items
    ]

    unresolved_count = sum(1 for item in validation_results if not item["valid"])

    if missing_link_types:
        rollup_status = "INCOMPLETE"
    elif unresolved_count:
        rollup_status = "UNRESOLVED"
    else:
        rollup_status = "COMPLETE"

    return {
        "rollup_status": rollup_status,
        "index": index,
        "missing_link_types": missing_link_types,
        "validation_results": validation_results,
        "read_only": True,
        "index_only": True,
        "source_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_generation_allowed": False,
        "operator_review_required": True,
    }
