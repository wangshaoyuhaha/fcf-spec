"""WATCHLIST-LIFECYCLE-D2 read-only source loader.

This loader builds local source metadata for the watchlist lifecycle sidecar.
It does not mutate source content, scores, reason codes, risk flags, or core files.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from apps.watchlist_lifecycle_app_1.contract import (
    APP_ID,
    UPSTREAM_READ_SOURCES,
    validate_watchlist_lifecycle_contract,
)


STAGE_ID = "WATCHLIST-LIFECYCLE-D2"
SOURCE_LOADER_VERSION = "1.0.0"

DEFAULT_SOURCE_CANDIDATES: List[Dict[str, str]] = [
    {"app_id": "DATA-APP-1", "source_kind": "docs", "relative_path": "docs/data_app_1"},
    {"app_id": "STOCK-APP-1", "source_kind": "docs", "relative_path": "docs/stock_app_1"},
    {"app_id": "AI-CONTEXT-1", "source_kind": "docs", "relative_path": "docs/ai_context_1"},
    {"app_id": "UI-APP-1", "source_kind": "docs", "relative_path": "docs/ui_app_1"},
    {"app_id": "OPERATOR-REVIEW-APP-1", "source_kind": "docs", "relative_path": "docs/operator_review_app_1"},
    {"app_id": "REPORT-ARCHIVE-APP-1", "source_kind": "docs", "relative_path": "docs/report_archive_app_1"},
    {"app_id": "DATA-QUALITY-OPS-APP-1", "source_kind": "docs", "relative_path": "docs/data_quality_ops_app_1"},
    {"app_id": "MARKET-SCENARIO-APP-1", "source_kind": "docs", "relative_path": "docs/market_scenario_app_1"},
    {"app_id": "BACKTEST-REVIEW-APP-1", "source_kind": "docs", "relative_path": "docs/backtest_review_app_1"},
    {"app_id": "SIGNAL-VALIDATION-APP-1", "source_kind": "docs", "relative_path": "docs/signal_validation_app_1"},
    {"app_id": "MODEL-GOVERNANCE-APP-1", "source_kind": "docs", "relative_path": "docs/model_governance_app_1"},
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

    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError("relative_path must stay inside source root") from exc

    return candidate


def inspect_source_candidate(
    root_path: str,
    app_id: str,
    source_kind: str,
    relative_path: str,
) -> Dict[str, Any]:
    """Inspect one local source candidate without returning source content."""
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
        record["modified_at_utc"] = datetime.fromtimestamp(
            candidate.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()
        return record

    if candidate.is_dir():
        files = [item for item in candidate.rglob("*") if item.is_file()]
        record["status"] = "PRESENT"
        record["path_type"] = "directory"
        record["size_bytes"] = sum(item.stat().st_size for item in files)
        record["file_count"] = len(files)
        record["modified_at_utc"] = datetime.fromtimestamp(
            candidate.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()
        return record

    return record


def build_watchlist_lifecycle_source_manifest(
    root_path: Optional[str] = None,
    candidates: Optional[Iterable[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Build a read-only source metadata manifest for D2."""
    contract_result = validate_watchlist_lifecycle_contract()
    if not contract_result["valid"]:
        raise ValueError("D1 contract is invalid: " + "; ".join(contract_result["issues"]))

    root = str(Path(root_path or ".").resolve())
    selected_candidates = list(candidates if candidates is not None else DEFAULT_SOURCE_CANDIDATES)

    source_records = [
        inspect_source_candidate(
            root_path=root,
            app_id=item["app_id"],
            source_kind=item["source_kind"],
            relative_path=item["relative_path"],
        )
        for item in selected_candidates
    ]

    represented_sources = sorted({item["app_id"] for item in source_records})
    missing_upstream_sources = sorted(set(UPSTREAM_READ_SOURCES) - set(represented_sources))

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
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "operator_review_required": True,
        "source_records": source_records,
        "source_record_count": len(source_records),
        "present_source_count": sum(1 for item in source_records if item["status"] == "PRESENT"),
        "missing_source_count": sum(1 for item in source_records if item["status"] == "MISSING"),
        "represented_upstream_sources": represented_sources,
        "missing_upstream_sources": missing_upstream_sources,
    }


def validate_watchlist_lifecycle_source_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the D2 source metadata manifest."""
    candidate = deepcopy(manifest)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("read_only") is not True:
        issues.append("manifest must be read_only")

    for false_key in [
        "content_loaded",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    records = candidate.get("source_records", [])
    represented_sources = {item.get("app_id") for item in records}
    missing_sources = sorted(set(UPSTREAM_READ_SOURCES) - represented_sources)
    if missing_sources:
        issues.append("missing upstream source records: " + ",".join(missing_sources))

    for record in records:
        label = record.get("app_id", "unknown")
        if record.get("content_loaded") is not False:
            issues.append(label + " content_loaded must be false")
        if record.get("read_only") is not True:
            issues.append(label + " read_only must be true")
        for false_key in [
            "source_content_mutation_allowed",
            "source_deletion_allowed",
            "source_overwrite_allowed",
        ]:
            if record.get(false_key) is not False:
                issues.append(label + " " + false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "source_record_count": candidate.get("source_record_count"),
    }
