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
