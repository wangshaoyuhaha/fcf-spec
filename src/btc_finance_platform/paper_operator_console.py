import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_multi_market_closeout import build_p6_closeout_package
from btc_finance_platform.paper_multi_market_report import build_multi_market_ui_contract


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


def build_paper_ui_safety_banner() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "paper_ui_safety_banner",
        "title": "PAPER ONLY OPERATOR CONSOLE",
        "messages": [
            "This console is paper-only.",
            "No real exchange or brokerage connection is enabled.",
            "No real orders, execution, balances, positions, or money impact are allowed.",
            "Operator review remains required.",
        ],
        "severity": "critical_safety_notice",
        "decision": "ui_banner_paper_only",
        **paper_flags(),
    }


def build_operator_dashboard_summary(file_path: Any) -> dict[str, Any]:
    closeout = build_p6_closeout_package(file_path)
    ui_contract = build_multi_market_ui_contract(file_path)

    return {
        "ok": closeout["ok"] is True and ui_contract["ok"] is True,
        "type": "operator_dashboard_summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "P7",
        "source_phase": "P6",
        "source_file": str(Path(file_path).name),
        "next_phase": closeout["next_phase"],
        "count": ui_contract["count"],
        "symbols": ui_contract["symbols"],
        "asset_class_counts": ui_contract["asset_class_counts"],
        "market_counts": ui_contract["market_counts"],
        "status_counts": ui_contract["status_counts"],
        "safety_banner": build_paper_ui_safety_banner(),
        "decision": "operator_dashboard_summary_paper_only",
        **paper_flags(),
    }


def build_operator_review_queue(file_path: Any) -> dict[str, Any]:
    ui_contract = build_multi_market_ui_contract(file_path)

    queue_items = []
    for index, card in enumerate(ui_contract["cards"], start=1):
        queue_items.append({
            "queue_id": "review-" + str(index).zfill(3),
            "symbol": card["symbol"],
            "asset_class": card["asset_class"],
            "market": card["market"],
            "status": card["status"],
            "risk_level": card["risk_level"],
            "risk_score": card["risk_score"],
            "regime": card["regime"],
            "signal": card["signal"],
            "allowed_action": card["allowed_action"],
            "operator_action": "review_paper_item_only",
            "real_world_actions_allowed": False,
            "blocked_real_world_actions": card["blocked_real_world_actions"],
        })

    return {
        "ok": True,
        "type": "operator_review_queue",
        "queue_version": "p7_d2_operator_review_queue_v1",
        "count": len(queue_items),
        "symbols": [item["symbol"] for item in queue_items],
        "items": queue_items,
        "decision": "operator_review_queue_paper_only",
        **paper_flags(),
    }


def build_report_viewer_index(file_path: Any) -> dict[str, Any]:
    dashboard = build_operator_dashboard_summary(file_path)

    reports = [
        {
            "report_id": "multi_market_report",
            "title": "Multi-Market Paper Report",
            "source": "P6 multi-market readable report",
            "format": "markdown_and_json_contract",
            "paper_only": True,
        },
        {
            "report_id": "readiness_bundle",
            "title": "Multi-Market Readiness Bundle",
            "source": "P6 readiness gate",
            "format": "json_contract",
            "paper_only": True,
        },
        {
            "report_id": "operator_review_queue",
            "title": "Operator Review Queue",
            "source": "P7 operator console contract",
            "format": "json_contract",
            "paper_only": True,
        },
    ]

    return {
        "ok": True,
        "type": "report_viewer_index",
        "source_file": dashboard["source_file"],
        "report_count": len(reports),
        "reports": reports,
        "decision": "report_viewer_index_paper_only",
        **paper_flags(),
    }


def validate_operator_console_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("operator_console_contract must be a dict")
    if contract.get("type") != "operator_console_contract":
        raise ValueError("operator_console_contract type is invalid")

    dashboard = contract.get("dashboard")
    review_queue = contract.get("review_queue")
    report_index = contract.get("report_index")

    checks = {
        "contract_ok": contract.get("ok") is True,
        "dashboard_ok": isinstance(dashboard, dict) and dashboard.get("ok") is True,
        "review_queue_ok": isinstance(review_queue, dict) and review_queue.get("ok") is True,
        "report_index_ok": isinstance(report_index, dict) and report_index.get("ok") is True,
        "queue_count_matches_dashboard": review_queue.get("count") == dashboard.get("count"),
        "paper_only_preserved": contract.get("paper_only") is True,
        "operator_review_required": contract.get("operator_review_required") is True,
        "no_real_exchange_api": contract.get("real_exchange_api") is False,
        "no_real_brokerage_api": contract.get("real_brokerage_api") is False,
        "no_real_api_key_required": contract.get("real_api_key_required") is False,
        "no_wallet_private_key_required": contract.get("wallet_private_key_required") is False,
        "no_real_order": contract.get("real_order") is False,
        "no_real_execution": contract.get("real_execution") is False,
        "no_real_balance": contract.get("real_balance") is False,
        "no_real_position": contract.get("real_position") is False,
        "no_real_money_impact": contract.get("real_money_impact") is False,
        "all_queue_items_block_real_world_actions": all(
            item.get("real_world_actions_allowed") is False
            for item in review_queue.get("items", [])
        ),
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_console_contract_validation",
        "checks": checks,
        "decision": "operator_console_validation_paper_only",
        **paper_flags(),
    }


def build_operator_console_contract(file_path: Any) -> dict[str, Any]:
    dashboard = build_operator_dashboard_summary(file_path)
    review_queue = build_operator_review_queue(file_path)
    report_index = build_report_viewer_index(file_path)

    contract = {
        "ok": dashboard["ok"] is True and review_queue["ok"] is True and report_index["ok"] is True,
        "type": "operator_console_contract",
        "contract_version": "p7_d1_operator_console_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dashboard": dashboard,
        "review_queue": review_queue,
        "report_index": report_index,
        "decision": "operator_console_contract_paper_only",
        **paper_flags(),
    }

    contract["validation"] = validate_operator_console_contract(contract)
    return contract


def write_operator_console_bundle(file_path: Any, output_dir: Any) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    contract = build_operator_console_contract(file_path)
    dashboard_path = directory / "operator_dashboard_summary.json"
    queue_path = directory / "operator_review_queue.json"
    index_path = directory / "report_viewer_index.json"
    contract_path = directory / "operator_console_contract.json"

    dashboard_path.write_text(json.dumps(contract["dashboard"], indent=2, sort_keys=True), encoding="utf-8")
    queue_path.write_text(json.dumps(contract["review_queue"], indent=2, sort_keys=True), encoding="utf-8")
    index_path.write_text(json.dumps(contract["report_index"], indent=2, sort_keys=True), encoding="utf-8")
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "operator_console_bundle_written",
        "output_dir": str(directory),
        "dashboard_file": str(dashboard_path),
        "review_queue_file": str(queue_path),
        "report_index_file": str(index_path),
        "contract_file": str(contract_path),
        "contract": contract,
        **paper_flags(),
    }
