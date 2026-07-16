"""DIFY-UI-HANDOFF-D2 source loader.

This module builds a read-only local source manifest for FCF UI, report,
workflow, and Dify handoff input artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from apps.dify_ui_handoff_app_1.contract import (
    APP_ID,
    SAFETY_FLAGS,
    UPSTREAM_READ_SOURCES,
    validate_dify_ui_handoff_contract,
)


STAGE_ID = "DIFY-UI-HANDOFF-D2"
MANIFEST_VERSION = "1.0.0"

IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache"}


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_relative_path(path: Path, root_path: Path) -> str:
    try:
        return path.relative_to(root_path).as_posix()
    except ValueError:
        return path.as_posix()


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def _inspect_directory(path: Path, root_path: Path) -> Dict[str, Any]:
    files: List[Path] = []
    total_bytes = 0

    if path.exists() and path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file() and not _is_ignored(child):
                files.append(child)
                total_bytes += child.stat().st_size

    sample_files = [
        _normalize_relative_path(child, root_path)
        for child in files[:20]
    ]

    return {
        "file_count": len(files),
        "total_bytes": total_bytes,
        "sample_files": sample_files,
    }


def inspect_dify_ui_source(
    root_path: str,
    source: Mapping[str, Any],
) -> Dict[str, Any]:
    """Inspect one local source without mutating source content."""
    root = Path(root_path).resolve()
    relative_path = source["relative_path"]
    full_path = (root / relative_path).resolve()

    exists = full_path.exists()
    is_file = full_path.is_file()
    is_dir = full_path.is_dir()

    result: Dict[str, Any] = {
        "source_id": source["source_id"],
        "source_kind": source["source_kind"],
        "relative_path": relative_path,
        "required": source.get("required", True),
        "absolute_path": str(full_path),
        "exists": exists,
        "is_file": is_file,
        "is_dir": is_dir,
        "read_only": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
    }

    if exists and is_file:
        stat = full_path.stat()
        result.update(
            {
                "size_bytes": stat.st_size,
                "sha256": _file_sha256(full_path),
                "child_file_count": 0,
                "child_total_bytes": 0,
                "sample_files": [],
            }
        )
    elif exists and is_dir:
        directory_summary = _inspect_directory(full_path, root)
        result.update(
            {
                "size_bytes": None,
                "sha256": None,
                "child_file_count": directory_summary["file_count"],
                "child_total_bytes": directory_summary["total_bytes"],
                "sample_files": directory_summary["sample_files"],
            }
        )
    else:
        result.update(
            {
                "size_bytes": None,
                "sha256": None,
                "child_file_count": 0,
                "child_total_bytes": 0,
                "sample_files": [],
            }
        )

    return result


def build_dify_ui_source_manifest(
    root_path: str = ".",
    sources: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Build the D2 read-only local source manifest."""
    selected_sources = deepcopy(sources) if sources is not None else deepcopy(UPSTREAM_READ_SOURCES)
    contract_validation = validate_dify_ui_handoff_contract()
    inspected_sources = [
        inspect_dify_ui_source(root_path=root_path, source=source)
        for source in selected_sources
    ]

    existing_count = sum(1 for item in inspected_sources if item["exists"])
    missing_count = sum(
        1 for item in inspected_sources if item["required"] and not item["exists"]
    )
    unavailable_optional_count = sum(
        1 for item in inspected_sources if not item["required"] and not item["exists"]
    )
    file_count = sum(1 for item in inspected_sources if item["is_file"])
    directory_count = sum(1 for item in inspected_sources if item["is_dir"])
    child_file_count = sum(item["child_file_count"] for item in inspected_sources)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "manifest_version": MANIFEST_VERSION,
        "created_at_utc": _now_utc(),
        "contract_valid": contract_validation["valid"],
        "contract_issues": list(contract_validation["issues"]),
        "source_count": len(inspected_sources),
        "existing_source_count": existing_count,
        "missing_source_count": missing_count,
        "unavailable_optional_source_count": unavailable_optional_count,
        "file_source_count": file_count,
        "directory_source_count": directory_count,
        "child_file_count": child_file_count,
        "sources": inspected_sources,
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "dify_api_write_allowed": False,
        "automated_dify_app_creation_allowed": False,
    }


def validate_dify_ui_source_manifest(manifest: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate D2 source manifest completeness and safety."""
    issues: List[str] = []

    if manifest.get("app_id") != APP_ID:
        issues.append("app_id mismatch")
    if manifest.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")
    if manifest.get("contract_valid") is not True:
        issues.append("contract_valid must be true")
    if manifest.get("source_count", 0) <= 0:
        issues.append("source_count must be positive")
    if manifest.get("missing_source_count") != 0:
        issues.append("missing_source_count must be zero")
    accounted = (
        manifest.get("existing_source_count", 0)
        + manifest.get("missing_source_count", 0)
        + manifest.get("unavailable_optional_source_count", 0)
    )
    if accounted != manifest.get("source_count"):
        issues.append("source availability accounting mismatch")
    if not manifest.get("sources"):
        issues.append("sources must not be empty")

    required_true_fields = [
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    ]
    required_false_fields = [
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "real_execution_allowed",
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "dify_api_write_allowed",
        "automated_dify_app_creation_allowed",
    ]

    for field in required_true_fields:
        if manifest.get(field) is not True:
            issues.append(field + " must be true")

    for field in required_false_fields:
        if manifest.get(field) is not False:
            issues.append(field + " must be false")

    for source in manifest.get("sources", []):
        if source.get("required") is True and source.get("exists") is not True:
            issues.append(source.get("source_id", "unknown") + " must exist")
        if source.get("read_only") is not True:
            issues.append(source.get("source_id", "unknown") + " must be read_only")
        for field in [
            "source_content_mutation_allowed",
            "source_deletion_allowed",
            "source_overwrite_allowed",
        ]:
            if source.get(field) is not False:
                issues.append(source.get("source_id", "unknown") + " " + field + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": manifest.get("app_id"),
        "stage_id": manifest.get("stage_id"),
        "source_count": manifest.get("source_count"),
        "existing_source_count": manifest.get("existing_source_count"),
        "missing_source_count": manifest.get("missing_source_count"),
        "unavailable_optional_source_count": manifest.get(
            "unavailable_optional_source_count"
        ),
        "child_file_count": manifest.get("child_file_count"),
    }


def summarize_dify_ui_source_manifest(manifest: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Return a compact D2 manifest summary."""
    selected_manifest = dict(manifest) if manifest is not None else build_dify_ui_source_manifest()
    validation = validate_dify_ui_source_manifest(selected_manifest)

    return {
        "app_id": selected_manifest.get("app_id"),
        "stage_id": selected_manifest.get("stage_id"),
        "valid": validation["valid"],
        "source_count": selected_manifest.get("source_count"),
        "existing_source_count": selected_manifest.get("existing_source_count"),
        "missing_source_count": selected_manifest.get("missing_source_count"),
        "unavailable_optional_source_count": selected_manifest.get(
            "unavailable_optional_source_count"
        ),
        "file_source_count": selected_manifest.get("file_source_count"),
        "directory_source_count": selected_manifest.get("directory_source_count"),
        "child_file_count": selected_manifest.get("child_file_count"),
        "paper_only": selected_manifest.get("paper_only"),
        "local_only": selected_manifest.get("local_only"),
        "read_only": selected_manifest.get("read_only"),
        "operator_review_required": selected_manifest.get("operator_review_required"),
        "dify_api_write_allowed": selected_manifest.get("dify_api_write_allowed"),
        "automated_dify_app_creation_allowed": selected_manifest.get("automated_dify_app_creation_allowed"),
    }
