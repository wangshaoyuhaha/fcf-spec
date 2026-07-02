import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_operator_console_report import build_operator_console_markdown_report
from btc_finance_platform.paper_operator_console_report import build_operator_console_ui_manifest


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


def build_operator_console_page_registry(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    manifest = build_operator_console_ui_manifest(file_path, action_by_symbol)

    pages = []
    for view in manifest["views"]:
        pages.append({
            "page_id": view["view_id"],
            "title": view["title"],
            "source_contract": view["source_contract"],
            "render_mode": "static_contract_view",
            "paper_only": True,
            "real_world_actions_allowed": False,
            "required_safety_banner": True,
        })

    return {
        "ok": True,
        "type": "operator_console_page_registry",
        "registry_version": "p7_d10_operator_console_page_registry_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": manifest["source_file"],
        "page_count": len(pages),
        "page_ids": [page["page_id"] for page in pages],
        "pages": pages,
        "source_manifest": manifest,
        "decision": "operator_console_page_registry_paper_only",
        **paper_flags(),
    }


def validate_operator_console_page_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(registry, dict):
        raise ValueError("operator_console_page_registry must be a dict")
    if registry.get("type") != "operator_console_page_registry":
        raise ValueError("operator_console_page_registry type is invalid")

    pages = registry.get("pages")
    if not isinstance(pages, list):
        raise ValueError("operator_console_page_registry.pages must be a list")

    checks = {
        "registry_ok": registry.get("ok") is True,
        "has_pages": len(pages) >= 4,
        "page_count_matches_pages": registry.get("page_count") == len(pages),
        "contains_dashboard": "dashboard" in registry.get("page_ids", []),
        "contains_review_queue": "review_queue" in registry.get("page_ids", []),
        "contains_reports": "reports" in registry.get("page_ids", []),
        "contains_safety": "safety" in registry.get("page_ids", []),
        "all_pages_paper_only": all(page.get("paper_only") is True for page in pages),
        "all_pages_block_real_world_actions": all(
            page.get("real_world_actions_allowed") is False for page in pages
        ),
        "all_pages_require_safety_banner": all(
            page.get("required_safety_banner") is True for page in pages
        ),
        "paper_only_preserved": registry.get("paper_only") is True,
        "operator_review_required": registry.get("operator_review_required") is True,
        "no_real_exchange_api": registry.get("real_exchange_api") is False,
        "no_real_brokerage_api": registry.get("real_brokerage_api") is False,
        "no_real_api_key_required": registry.get("real_api_key_required") is False,
        "no_wallet_private_key_required": registry.get("wallet_private_key_required") is False,
        "no_real_order": registry.get("real_order") is False,
        "no_real_execution": registry.get("real_execution") is False,
        "no_real_money_impact": registry.get("real_money_impact") is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_console_page_registry_validation",
        "checks": checks,
        "decision": "operator_console_page_registry_validation_paper_only",
        **paper_flags(),
    }


def build_operator_console_ui_acceptance_gate(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    manifest = build_operator_console_ui_manifest(file_path, action_by_symbol)
    registry = build_operator_console_page_registry(file_path, action_by_symbol)
    registry_validation = validate_operator_console_page_registry(registry)
    report = build_operator_console_markdown_report(file_path, action_by_symbol)

    checks = {
        "manifest_ok": manifest["ok"] is True,
        "manifest_validation_ok": manifest["validation"]["ok"] is True,
        "registry_ok": registry["ok"] is True,
        "registry_validation_ok": registry_validation["ok"] is True,
        "report_ok": report["ok"] is True,
        "markdown_has_safety_boundary": "## Safety Boundary" in report["markdown"],
        "markdown_blocks_real_world_action": "No real-world trading action is enabled." in report["markdown"],
        "paper_only_preserved": manifest["paper_only"] is True,
        "operator_review_required": manifest["operator_review_required"] is True,
        "no_real_exchange_api": manifest["real_exchange_api"] is False,
        "no_real_brokerage_api": manifest["real_brokerage_api"] is False,
        "no_real_api_key_required": manifest["real_api_key_required"] is False,
        "no_wallet_private_key_required": manifest["wallet_private_key_required"] is False,
        "no_real_order": manifest["real_order"] is False,
        "no_real_execution": manifest["real_execution"] is False,
        "no_real_balance": manifest["real_balance"] is False,
        "no_real_position": manifest["real_position"] is False,
        "no_real_money_impact": manifest["real_money_impact"] is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_console_ui_acceptance_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_version": manifest["manifest_version"],
        "registry_version": registry["registry_version"],
        "page_count": registry["page_count"],
        "page_ids": registry["page_ids"],
        "checks": checks,
        "decision": "operator_console_ui_acceptance_gate_paper_only",
        **paper_flags(),
    }


def build_operator_console_acceptance_summary(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    gate = build_operator_console_ui_acceptance_gate(file_path, action_by_symbol)
    registry = build_operator_console_page_registry(file_path, action_by_symbol)

    return {
        "ok": gate["ok"] is True,
        "type": "operator_console_acceptance_summary",
        "source_file": registry["source_file"],
        "gate": gate["gate"],
        "page_count": registry["page_count"],
        "page_ids": registry["page_ids"],
        "accepted_for": "future_static_ui_handoff" if gate["ok"] else "blocked_until_fixed",
        "real_world_actions_allowed": False,
        "decision": "operator_console_acceptance_summary_paper_only",
        **paper_flags(),
    }


def write_operator_console_acceptance_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    registry = build_operator_console_page_registry(file_path, action_by_symbol)
    gate = build_operator_console_ui_acceptance_gate(file_path, action_by_symbol)
    summary = build_operator_console_acceptance_summary(file_path, action_by_symbol)
    report = build_operator_console_markdown_report(file_path, action_by_symbol)

    registry_path = directory / "operator_console_page_registry.json"
    gate_path = directory / "operator_console_ui_acceptance_gate.json"
    summary_path = directory / "operator_console_acceptance_summary.json"
    report_path = directory / "operator_console_acceptance_report.md"

    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    gate_path.write_text(json.dumps(gate, indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(report["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "operator_console_acceptance_bundle_written",
        "output_dir": str(directory),
        "registry_file": str(registry_path),
        "gate_file": str(gate_path),
        "summary_file": str(summary_path),
        "report_file": str(report_path),
        "registry": registry,
        "gate": gate,
        "summary": summary,
        **paper_flags(),
    }
