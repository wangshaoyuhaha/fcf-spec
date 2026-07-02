import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_operator_workflow import build_cli_to_ui_artifact_export_bridge
from btc_finance_platform.paper_operator_workflow import build_operator_workflow_summary


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_brokerage_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def build_operator_console_readable_summary(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    bridge = build_cli_to_ui_artifact_export_bridge(file_path, action_by_symbol)
    workflow_summary = build_operator_workflow_summary(file_path, action_by_symbol)
    console = bridge["console"]
    dashboard = console["dashboard"]

    return {
        "ok": bridge["ok"] is True and workflow_summary["ok"] is True,
        "type": "operator_console_readable_summary",
        "source_file": dashboard["source_file"],
        "count": dashboard["count"],
        "symbols": dashboard["symbols"],
        "asset_class_counts": dashboard["asset_class_counts"],
        "market_counts": dashboard["market_counts"],
        "status_counts": dashboard["status_counts"],
        "action_counts": workflow_summary["action_counts"],
        "all_reviewed": workflow_summary["all_reviewed"],
        "allowed_global_next_step": workflow_summary["allowed_global_next_step"],
        "real_world_actions_allowed": False,
        "decision": "operator_console_summary_paper_only",
        **paper_flags(),
    }


def build_operator_console_markdown_report(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    bridge = build_cli_to_ui_artifact_export_bridge(file_path, action_by_symbol)
    summary = build_operator_console_readable_summary(file_path, action_by_symbol)
    workflow_state = bridge["workflow_state"]

    lines = [
        "# Operator Console Paper Report",
        "",
        "Status: paper-only operator console report",
        "",
        "Created at UTC: " + datetime.now(timezone.utc).isoformat(),
        "",
        "## Safety Boundary",
        "",
        "- Paper-only: true",
        "- Real exchange API: false",
        "- Real brokerage API: false",
        "- Real API key required: false",
        "- Wallet private key required: false",
        "- Real order: false",
        "- Real execution: false",
        "- Real balance: false",
        "- Real position: false",
        "- Real money impact: false",
        "- Operator review required: true",
        "",
        "## Dashboard Summary",
        "",
        "- Count: " + str(summary["count"]),
        "- Symbols: " + ", ".join(summary["symbols"]),
        "- Asset class counts: " + json.dumps(summary["asset_class_counts"], sort_keys=True),
        "- Market counts: " + json.dumps(summary["market_counts"], sort_keys=True),
        "- Status counts: " + json.dumps(summary["status_counts"], sort_keys=True),
        "- Action counts: " + json.dumps(summary["action_counts"], sort_keys=True),
        "- All reviewed: " + str(summary["all_reviewed"]),
        "- Allowed global next step: " + summary["allowed_global_next_step"],
        "",
        "## Review Actions",
        "",
    ]

    for item in workflow_state["actions"]:
        lines.extend([
            "### " + item["symbol"],
            "",
            "- Queue ID: " + item["queue_id"],
            "- Asset class: " + item["asset_class"],
            "- Market: " + item["market"],
            "- Operator action: " + item["operator_action"],
            "- Workflow gate: " + item["workflow_gate"],
            "- Allowed next step: " + item["allowed_next_step"],
            "- Real-world actions allowed: false",
            "",
        ])

    lines.extend([
        "## Final Notice",
        "",
        "This console report is not financial advice.",
        "This console report is not a real trading signal.",
        "Approved only means paper review approved.",
        "No real-world trading action is enabled.",
        "",
    ])

    return {
        "ok": True,
        "type": "operator_console_markdown_report",
        "summary": summary,
        "markdown": "\n".join(lines),
        "bridge": bridge,
        "decision": "operator_console_markdown_report_paper_only",
        **paper_flags(),
    }


def build_operator_console_ui_manifest(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    bridge = build_cli_to_ui_artifact_export_bridge(file_path, action_by_symbol)
    summary = build_operator_console_readable_summary(file_path, action_by_symbol)
    console = bridge["console"]

    manifest = {
        "ok": True,
        "type": "operator_console_ui_manifest",
        "manifest_version": "p7_d7_operator_console_ui_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": summary["source_file"],
        "views": [
            {
                "view_id": "dashboard",
                "title": "Dashboard",
                "source_contract": "operator_dashboard_summary.json",
                "paper_only": True,
            },
            {
                "view_id": "review_queue",
                "title": "Review Queue",
                "source_contract": "operator_workflow_state.json",
                "paper_only": True,
            },
            {
                "view_id": "reports",
                "title": "Reports",
                "source_contract": "report_viewer_index.json",
                "paper_only": True,
            },
            {
                "view_id": "safety",
                "title": "Safety Boundary",
                "source_contract": "operator_console_report.md",
                "paper_only": True,
            },
        ],
        "summary": summary,
        "console_contract_version": console["contract_version"],
        "workflow_version": bridge["workflow_version"],
        "decision": "operator_console_ui_manifest_paper_only",
        **paper_flags(),
    }

    manifest["validation"] = validate_operator_console_ui_manifest(manifest)
    return manifest


def validate_operator_console_ui_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("operator_console_ui_manifest must be a dict")
    if manifest.get("type") != "operator_console_ui_manifest":
        raise ValueError("operator_console_ui_manifest type is invalid")

    views = manifest.get("views")
    if not isinstance(views, list):
        raise ValueError("operator_console_ui_manifest.views must be a list")

    checks = {
        "manifest_ok": manifest.get("ok") is True,
        "has_views": len(views) >= 3,
        "all_views_paper_only": all(view.get("paper_only") is True for view in views),
        "paper_only_preserved": manifest.get("paper_only") is True,
        "operator_review_required": manifest.get("operator_review_required") is True,
        "no_real_exchange_api": manifest.get("real_exchange_api") is False,
        "no_real_brokerage_api": manifest.get("real_brokerage_api") is False,
        "no_real_api_key_required": manifest.get("real_api_key_required") is False,
        "no_wallet_private_key_required": manifest.get("wallet_private_key_required") is False,
        "no_real_order": manifest.get("real_order") is False,
        "no_real_execution": manifest.get("real_execution") is False,
        "no_real_balance": manifest.get("real_balance") is False,
        "no_real_position": manifest.get("real_position") is False,
        "no_real_money_impact": manifest.get("real_money_impact") is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_console_ui_manifest_validation",
        "checks": checks,
        "decision": "operator_console_manifest_validation_paper_only",
        **paper_flags(),
    }


def write_operator_console_static_export_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    report = build_operator_console_markdown_report(file_path, action_by_symbol)
    manifest = build_operator_console_ui_manifest(file_path, action_by_symbol)
    bridge = report["bridge"]

    report_path = directory / "operator_console_report.md"
    manifest_path = directory / "operator_console_ui_manifest.json"
    bridge_path = directory / "cli_to_ui_artifact_export_bridge.json"
    summary_path = directory / "operator_console_readable_summary.json"

    report_path.write_text(report["markdown"], encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    bridge_path.write_text(json.dumps(bridge, indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(json.dumps(report["summary"], indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "operator_console_static_export_bundle_written",
        "output_dir": str(directory),
        "report_file": str(report_path),
        "manifest_file": str(manifest_path),
        "bridge_file": str(bridge_path),
        "summary_file": str(summary_path),
        "report": report,
        "manifest": manifest,
        **paper_flags(),
    }
