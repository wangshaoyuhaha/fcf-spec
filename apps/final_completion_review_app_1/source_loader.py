"""FINAL-COMPLETION-REVIEW-D2 read-only source loader."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from apps.final_completion_review_app_1.contract import (
    APP_ID,
    UPSTREAM_READ_SOURCES,
    validate_final_completion_contract,
)


STAGE_ID = "FINAL-COMPLETION-REVIEW-D2"
SOURCE_LOADER_VERSION = "1.0.0"

DEFAULT_SOURCE_CANDIDATES: List[Dict[str, str]] = [
    {"app_id": "DATA-APP-1", "source_kind": "docs", "relative_path": "docs/data_app_1"},
    {"app_id": "STOCK-APP-1", "source_kind": "docs", "relative_path": "docs/stock_app_1"},
    {"app_id": "AI-CONTEXT-1", "source_kind": "docs", "relative_path": "docs/ai_context_1"},
    {"app_id": "UI-APP-1", "source_kind": "docs", "relative_path": "docs/ui_app_1"},
    {"app_id": "OPERATOR-REVIEW-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_OPERATOR_REVIEW_APP_1_FINAL.md"},
    {"app_id": "REPORT-ARCHIVE-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_REPORT_ARCHIVE_APP_1_FINAL.md"},
    {"app_id": "DATA-QUALITY-OPS-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_DATA_QUALITY_OPS_APP_1_FINAL.md"},
    {"app_id": "MARKET-SCENARIO-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_MARKET_SCENARIO_APP_1_FINAL.md"},
    {"app_id": "BACKTEST-REVIEW-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_BACKTEST_REVIEW_APP_1_FINAL.md"},
    {"app_id": "SIGNAL-VALIDATION-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_SIGNAL_VALIDATION_APP_1_FINAL.md"},
    {"app_id": "MODEL-GOVERNANCE-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_MODEL_GOVERNANCE_APP_1_FINAL.md"},
    {"app_id": "WATCHLIST-LIFECYCLE-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_WATCHLIST_LIFECYCLE_APP_1_FINAL.md"},
    {"app_id": "PORTFOLIO-REVIEW-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_PORTFOLIO_REVIEW_APP_1_FINAL.md"},
    {"app_id": "RISK-EXPOSURE-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_RISK_EXPOSURE_APP_1_FINAL.md"},
    {"app_id": "DECISION-AUDIT-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_DECISION_AUDIT_APP_1_FINAL.md"},
    {"app_id": "RESEARCH-WORKFLOW-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_RESEARCH_WORKFLOW_APP_1_FINAL.md"},
    {"app_id": "DASHBOARD-STATUS-APP-1", "source_kind": "current_state", "relative_path": "FCF_CURRENT_STATE_DASHBOARD_STATUS_APP_1_FINAL.md"},
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_child(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute():
        raise ValueError("relative_path must not be absolute")
    root_resolved = root.resolve()
    candidate = (root_resolved / relative).resolve()
    candidate.relative_to(root_resolved)
    return candidate


def inspect_final_completion_source(root_path: str, app_id: str, source_kind: str, relative_path: str) -> Dict[str, Any]:
    root = Path(root_path)
    candidate = _safe_child(root, relative_path)

    record: Dict[str, Any] = {
        "app_id": app_id,
        "source_kind": source_kind,
        "relative_path": relative_path,
        "exists": candidate.exists(),
        "status": "MISSING",
        "path_type": "missing",
        "size_bytes": 0,
        "file_count": 0,
        "sha256": None,
        "modified_at_utc": None,
        "content_loaded": False,
        "read_only": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
    }

    if candidate.is_file():
        record["status"] = "PRESENT"
        record["path_type"] = "file"
        record["size_bytes"] = candidate.stat().st_size
        record["file_count"] = 1
        record["sha256"] = _file_sha256(candidate)
        record["modified_at_utc"] = datetime.fromtimestamp(candidate.stat().st_mtime, tz=timezone.utc).isoformat()
        return record

    if candidate.is_dir():
        files = [item for item in candidate.rglob("*") if item.is_file()]
        record["status"] = "PRESENT"
        record["path_type"] = "directory"
        record["size_bytes"] = sum(item.stat().st_size for item in files)
        record["file_count"] = len(files)
        record["modified_at_utc"] = datetime.fromtimestamp(candidate.stat().st_mtime, tz=timezone.utc).isoformat()
        return record

    return record


def build_final_completion_source_manifest(
    root_path: Optional[str] = None,
    candidates: Optional[Iterable[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    contract_result = validate_final_completion_contract()
    if not contract_result["valid"]:
        raise ValueError("D1 contract is invalid: " + "; ".join(contract_result["issues"]))

    root = str(Path(root_path or ".").resolve())
    selected_candidates = list(candidates if candidates is not None else DEFAULT_SOURCE_CANDIDATES)

    source_records = [
        inspect_final_completion_source(
            root_path=root,
            app_id=item["app_id"],
            source_kind=item["source_kind"],
            relative_path=item["relative_path"],
        )
        for item in selected_candidates
    ]

    represented = sorted({item["app_id"] for item in source_records})

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "source_loader_version": SOURCE_LOADER_VERSION,
        "generated_at_utc": _utc_now(),
        "source_root": root,
        "read_only": True,
        "content_loaded": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "auto_completion_approval_allowed": False,
        "workflow_execution_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "operator_review_required": True,
        "source_records": source_records,
        "source_record_count": len(source_records),
        "present_source_count": sum(1 for item in source_records if item["status"] == "PRESENT"),
        "missing_source_count": sum(1 for item in source_records if item["status"] == "MISSING"),
        "represented_upstream_sources": represented,
        "missing_upstream_sources": sorted(set(UPSTREAM_READ_SOURCES) - set(represented)),
    }


def validate_final_completion_source_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(manifest)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("read_only") is not True:
        issues.append("read_only must be true")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "content_loaded",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "auto_completion_approval_allowed",
        "workflow_execution_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    represented = {item.get("app_id") for item in candidate.get("source_records", [])}
    missing = sorted(set(UPSTREAM_READ_SOURCES) - represented)
    if missing:
        issues.append("missing upstream source records: " + ",".join(missing))

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "source_record_count": candidate.get("source_record_count"),
    }
