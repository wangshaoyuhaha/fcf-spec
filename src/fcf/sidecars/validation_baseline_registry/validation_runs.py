"""Validation run records for VALIDATION-BASELINE-D2."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from .contract import validate_baseline_record

ALLOWED_VALIDATION_RESULTS = (
    "PASS",
    "FAIL",
    "INCOMPLETE",
    "STALE",
    "UNRESOLVED",
)


def build_validation_run_record(
    *,
    validation_id: str,
    command: str,
    result: str,
    pass_count: int,
    git_branch: str,
    git_head: str,
    git_status: str,
    origin_status: str,
    output_summary: str,
    baseline_status: str = "REGISTERED",
) -> Dict[str, Any]:
    """Build one read-only validation run record."""

    if result not in ALLOWED_VALIDATION_RESULTS:
        raise ValueError(f"unsupported validation result: {result}")

    return {
        "validation_id": validation_id,
        "command": command,
        "result": result,
        "pass_count": pass_count,
        "git_branch": git_branch,
        "git_head": git_head,
        "git_status": git_status,
        "origin_status": origin_status,
        "output_summary": output_summary,
        "baseline_status": baseline_status,
        "read_only": True,
        "index_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }


def validate_validation_run_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a run record without repairing or fabricating it."""

    baseline_validation = validate_baseline_record(record)
    issues: List[str] = list(baseline_validation["issues"])

    if record.get("result") not in ALLOWED_VALIDATION_RESULTS:
        issues.append("UNSUPPORTED_VALIDATION_RESULT")

    if record.get("output_summary") in ("", None):
        issues.append("MISSING_OUTPUT_SUMMARY")

    if record.get("result") == "PASS" and record.get("pass_count") in (None, 0):
        issues.append("PASS_WITHOUT_PASS_COUNT")

    if record.get("validation_result_fabrication_allowed") is True:
        issues.append("VALIDATION_RESULT_FABRICATION_NOT_ALLOWED")

    if record.get("pass_count_fabrication_allowed") is True:
        issues.append("PASS_COUNT_FABRICATION_NOT_ALLOWED")

    if issues:
        result_status = "UNRESOLVED"
    else:
        result_status = baseline_validation["result_status"]

    return {
        "valid": not issues,
        "result_status": result_status,
        "issues": sorted(set(issues)),
        "baseline_validation": deepcopy(baseline_validation),
        "read_only": True,
        "index_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }


def build_validation_run_index(
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only validation run index."""

    indexed_records: List[Dict[str, Any]] = []
    counts = {
        "VERIFIED": 0,
        "REGISTERED": 0,
        "INCOMPLETE": 0,
        "STALE": 0,
        "UNRESOLVED": 0,
    }

    for record in records:
        validation = validate_validation_run_record(record)
        status = validation["result_status"]
        if status not in counts:
            status = "UNRESOLVED"
        counts[status] += 1

        indexed_records.append(
            {
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
                "validation": validation,
                "read_only": True,
                "validation_result_fabrication_allowed": False,
                "pass_count_fabrication_allowed": False,
                "source_artifact_mutation_allowed": False,
                "evidence_backfill_allowed": False,
            }
        )

    if counts["UNRESOLVED"]:
        run_index_status = "UNRESOLVED"
    elif counts["STALE"]:
        run_index_status = "STALE"
    elif counts["INCOMPLETE"]:
        run_index_status = "INCOMPLETE"
    elif counts["VERIFIED"]:
        run_index_status = "VERIFIED"
    else:
        run_index_status = "REGISTERED"

    return {
        "stage": "D2",
        "run_index_status": run_index_status,
        "record_count": len(indexed_records),
        "status_counts": counts,
        "records": indexed_records,
        "read_only": True,
        "index_only": True,
        "sidecar_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
    }
