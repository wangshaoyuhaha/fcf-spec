from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from btc_finance_platform.operator_evidence_console import build_operator_evidence_console_closeout_checkpoint
from btc_finance_platform.operator_evidence_console import build_operator_evidence_static_export_package


def build_local_evidence_export_manifest(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    return {
        "ok": True,
        "type": "local_evidence_export_manifest",
        "phase": "P17-D1-D3",
        "export_dir": export_dir,
        "export_mode": "LOCAL_STATIC_READ_ONLY",
        "files": [
            {"name": "operator_evidence_export_package.json", "format": "json", "read_only": True},
            {"name": "operator_evidence_report.md", "format": "markdown", "read_only": True},
            {"name": "operator_evidence_closeout.json", "format": "json", "read_only": True},
        ],
        "file_count": 3,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def render_operator_evidence_markdown_report() -> str:
    package = build_operator_evidence_static_export_package()
    section_titles = [section["title"] for section in package["manifest"]["sections"]]
    lines = [
        "# Operator Evidence Console Export Report",
        "",
        f"Release tag: {package['release_tag']}",
        f"Release commit: {package['release_commit']}",
        "Export mode: LOCAL_STATIC_READ_ONLY",
        "",
        "Sections:",
    ]
    lines.extend(f"- {title}" for title in section_titles)
    lines.extend([
        "",
        "Safety:",
        "- paper-only",
        "- local-only",
        "- read-only",
        "- no deploy",
        "- no real trading",
        "- operator review required",
    ])
    return "\n".join(lines) + "\n"


def build_local_evidence_export_files(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    package = build_operator_evidence_static_export_package()
    closeout = build_operator_evidence_console_closeout_checkpoint()
    manifest = build_local_evidence_export_manifest(export_dir)

    files = [
        {
            "path": f"{export_dir}/operator_evidence_export_package.json",
            "content_type": "application/json",
            "read_only": True,
            "content": json.dumps(package, indent=2, sort_keys=True),
        },
        {
            "path": f"{export_dir}/operator_evidence_report.md",
            "content_type": "text/markdown",
            "read_only": True,
            "content": render_operator_evidence_markdown_report(),
        },
        {
            "path": f"{export_dir}/operator_evidence_closeout.json",
            "content_type": "application/json",
            "read_only": True,
            "content": json.dumps(closeout, indent=2, sort_keys=True),
        },
    ]

    return {
        "ok": True,
        "type": "local_evidence_export_files",
        "manifest": manifest,
        "files": files,
        "file_count": len(files),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def write_local_evidence_export_files(export_dir: str | Path) -> dict[str, Any]:
    export_path = Path(export_dir)
    bundle = build_local_evidence_export_files(str(export_path))
    export_path.mkdir(parents=True, exist_ok=True)

    written = []
    for item in bundle["files"]:
        path = Path(item["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item["content"], encoding="utf-8")
        written.append(str(path))

    return {
        "ok": True,
        "type": "local_evidence_export_write_result",
        "export_dir": str(export_path),
        "written_count": len(written),
        "written_files": written,
        "paper_only": True,
        "local_only": True,
        "read_only_export": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }

import hashlib


def build_local_evidence_export_integrity_index(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    bundle = build_local_evidence_export_files(export_dir)
    items = []
    for item in bundle["files"]:
        raw = item["content"].encode("utf-8")
        items.append({
            "path": item["path"],
            "content_type": item["content_type"],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
            "read_only": item["read_only"],
        })

    return {
        "ok": True,
        "type": "local_evidence_export_integrity_index",
        "export_dir": export_dir,
        "file_count": len(items),
        "items": items,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def validate_local_evidence_export_bundle(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    bundle = build_local_evidence_export_files(export_dir)
    integrity = build_local_evidence_export_integrity_index(export_dir)

    file_count_ok = bundle["file_count"] == bundle["manifest"]["file_count"] == integrity["file_count"]
    all_read_only = all(item["read_only"] is True for item in bundle["files"])
    all_hashes_valid = all(len(item["sha256"]) == 64 and item["size_bytes"] > 0 for item in integrity["items"])
    safety_ok = (
        bundle["paper_only"] is True
        and bundle["local_only"] is True
        and bundle["read_only"] is True
        and bundle["deploy_enabled"] is False
        and bundle["real_trading_enabled"] is False
    )

    passed = file_count_ok and all_read_only and all_hashes_valid and safety_ok
    return {
        "ok": passed,
        "type": "local_evidence_export_bundle_validator",
        "status": "PASSED" if passed else "FAILED",
        "file_count_ok": file_count_ok,
        "all_read_only": all_read_only,
        "all_hashes_valid": all_hashes_valid,
        "safety_ok": safety_ok,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def build_local_evidence_export_readable_index(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    manifest = build_local_evidence_export_manifest(export_dir)
    integrity = build_local_evidence_export_integrity_index(export_dir)
    validator = validate_local_evidence_export_bundle(export_dir)

    return {
        "ok": validator["ok"],
        "type": "local_evidence_export_readable_index",
        "title": "P17 Local Evidence Console Export Index",
        "export_dir": export_dir,
        "file_count": manifest["file_count"],
        "files": [item["path"] for item in integrity["items"]],
        "validation_status": validator["status"],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def render_local_evidence_export_index_markdown(export_dir: str = "runtime/operator_evidence_console") -> str:
    index = build_local_evidence_export_readable_index(export_dir)
    lines = [
        "# P17 Local Evidence Export Index",
        "",
        f"Export dir: {index['export_dir']}",
        f"Validation: {index['validation_status']}",
        f"File count: {index['file_count']}",
        "",
        "Files:",
    ]
    lines.extend(f"- {path}" for path in index["files"])
    lines.extend([
        "",
        "Safety:",
        "- paper-only",
        "- local-only",
        "- read-only",
        "- no deploy",
        "- no real trading",
        "- operator review required",
    ])
    return "\n".join(lines) + "\n"


def write_local_evidence_export_readable_index(export_dir: str | Path) -> dict[str, Any]:
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)

    json_path = export_path / "local_evidence_export_index.json"
    md_path = export_path / "local_evidence_export_index.md"

    index = build_local_evidence_export_readable_index(str(export_path))
    json_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_local_evidence_export_index_markdown(str(export_path)), encoding="utf-8")

    return {
        "ok": True,
        "type": "local_evidence_export_readable_index_write_result",
        "written_count": 2,
        "written_files": [str(json_path), str(md_path)],
        "paper_only": True,
        "local_only": True,
        "read_only_export": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def build_local_evidence_export_closeout_checkpoint(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    validator = validate_local_evidence_export_bundle(export_dir)
    readable = build_local_evidence_export_readable_index(export_dir)
    return {
        "ok": validator["ok"] and readable["ok"],
        "type": "local_evidence_export_closeout_checkpoint",
        "phase": "P17-D7-D9",
        "export_dir": export_dir,
        "validation_status": validator["status"],
        "file_count": readable["file_count"],
        "completed": [
            "readable_index_writer",
            "export_closeout_checkpoint",
            "export_handoff_packet",
        ],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_local_evidence_export_handoff_packet(export_dir: str = "runtime/operator_evidence_console") -> dict[str, Any]:
    closeout = build_local_evidence_export_closeout_checkpoint(export_dir)
    return {
        "ok": closeout["ok"],
        "type": "local_evidence_export_handoff_packet",
        "release_tag": "v14-learning-engine-paper",
        "phase": "P17-D7-D9",
        "export_dir": export_dir,
        "handoff_status": "READY_FOR_OPERATOR_REVIEW" if closeout["ok"] else "BLOCKED",
        "closeout": closeout,
        "next_phase_candidate": "P18 Local Evidence Console Navigation",
        "safety_boundary": "paper-only, local-only, read-only, no deploy, no real trading",
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
