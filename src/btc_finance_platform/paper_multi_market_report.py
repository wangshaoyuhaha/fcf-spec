import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_pipeline_report_from_json


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


def require_multi_market_pipeline_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("multi_market_pipeline_report must be a dict")
    if report.get("ok") is not True:
        raise ValueError("multi_market_pipeline_report must be ok")
    if report.get("type") != "multi_market_pipeline_report":
        raise ValueError("multi_market_pipeline_report type is invalid")
    return report


def build_multi_market_report_summary(file_path: Any) -> dict[str, Any]:
    report = require_multi_market_pipeline_report(
        build_multi_market_pipeline_report_from_json(file_path)
    )
    governance = report["governance"]

    return {
        "ok": True,
        "type": "multi_market_report_summary",
        "source_file": report["source_file"],
        "count": report["count"],
        "symbols": report["symbols"],
        "asset_class_counts": report["asset_class_counts"],
        "market_counts": report["market_counts"],
        "gate_counts": governance["gate_counts"],
        "regime_counts": governance["regime_counts"],
        "decision": "multi_market_summary_paper_only",
        **paper_flags(),
    }


def build_multi_market_ui_card(
    market_item: dict[str, Any],
    governor_decision: dict[str, Any],
    policy_gate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(market_item, dict):
        raise ValueError("market_item must be a dict")
    if not isinstance(governor_decision, dict):
        raise ValueError("governor_decision must be a dict")
    if not isinstance(policy_gate, dict):
        raise ValueError("policy_gate must be a dict")

    if governor_decision["gate"] == "blocked_for_escalation":
        status = "needs_manual_review"
    elif policy_gate["gate"] == "pass":
        status = "paper_review_allowed"
    else:
        status = "policy_check_failed"

    return {
        "ok": True,
        "type": "multi_market_ui_card",
        "symbol": market_item["symbol"],
        "asset_class": market_item["asset_class"],
        "market": market_item["market"],
        "status": status,
        "risk_level": governor_decision["risk_level"],
        "risk_score": governor_decision["risk_score"],
        "regime": governor_decision["regime"]["regime"],
        "signal": governor_decision["signal"],
        "governor_gate": governor_decision["gate"],
        "policy_gate": policy_gate["gate"],
        "allowed_action": governor_decision["allowed_action"],
        "blocked_reasons": governor_decision["blocked_reasons"],
        "blocked_real_world_actions": policy_gate["blocked_real_world_actions"],
        "decision": "multi_market_ui_card_paper_only",
        **paper_flags(),
    }


def build_multi_market_ui_contract(file_path: Any) -> dict[str, Any]:
    report = require_multi_market_pipeline_report(
        build_multi_market_pipeline_report_from_json(file_path)
    )
    market_items = report["pipeline"]["loaded_contract"]["contract"]["items"]
    governance = report["governance"]

    cards = []
    for market_item, governor_decision, policy_gate in zip(
        market_items,
        governance["governor_decisions"],
        governance["policy_gates"],
    ):
        cards.append(build_multi_market_ui_card(
            market_item,
            governor_decision,
            policy_gate,
        ))

    status_counts: dict[str, int] = {}
    for card in cards:
        status = card["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    contract = {
        "ok": True,
        "type": "multi_market_ui_contract",
        "contract_version": "p6_d7_multi_market_ui_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": report["source_file"],
        "count": len(cards),
        "symbols": [card["symbol"] for card in cards],
        "asset_class_counts": report["asset_class_counts"],
        "market_counts": report["market_counts"],
        "status_counts": status_counts,
        "cards": cards,
        "decision": "multi_market_ui_contract_paper_only",
        **paper_flags(),
    }

    contract["validation"] = validate_multi_market_ui_contract(contract)
    return contract


def validate_multi_market_ui_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("multi_market_ui_contract must be a dict")
    if contract.get("type") != "multi_market_ui_contract":
        raise ValueError("multi_market_ui_contract type is invalid")

    cards = contract.get("cards")
    if not isinstance(cards, list):
        raise ValueError("multi_market_ui_contract.cards must be a list")

    checks = {
        "contract_ok": contract.get("ok") is True,
        "has_cards": len(cards) > 0,
        "count_matches_cards": contract.get("count") == len(cards),
        "paper_only_preserved": contract.get("paper_only") is True,
        "operator_review_required": contract.get("operator_review_required") is True,
        "no_real_exchange_api": contract.get("real_exchange_api") is False,
        "no_real_brokerage_api": contract.get("real_brokerage_api") is False,
        "no_real_api_key_required": contract.get("real_api_key_required") is False,
        "no_wallet_private_key_required": contract.get("wallet_private_key_required") is False,
        "no_real_order": contract.get("real_order") is False,
        "no_real_execution": contract.get("real_execution") is False,
        "no_real_money_impact": contract.get("real_money_impact") is False,
        "all_cards_paper_only": all(card.get("paper_only") is True for card in cards),
        "all_cards_no_real_order": all(card.get("real_order") is False for card in cards),
    }

    return {
        "ok": all(checks.values()),
        "type": "multi_market_ui_contract_validation",
        "checks": checks,
        "decision": "multi_market_contract_validation_paper_only",
        **paper_flags(),
    }


def build_multi_market_markdown_report(file_path: Any) -> dict[str, Any]:
    summary = build_multi_market_report_summary(file_path)
    contract = build_multi_market_ui_contract(file_path)

    lines = [
        "# Multi-Market Paper Report",
        "",
        "Status: paper-only multi-market report",
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
        "## Summary",
        "",
        "- Count: " + str(summary["count"]),
        "- Symbols: " + ", ".join(summary["symbols"]),
        "- Asset class counts: " + json.dumps(summary["asset_class_counts"], sort_keys=True),
        "- Market counts: " + json.dumps(summary["market_counts"], sort_keys=True),
        "- Gate counts: " + json.dumps(summary["gate_counts"], sort_keys=True),
        "- Regime counts: " + json.dumps(summary["regime_counts"], sort_keys=True),
        "",
        "## Cards",
        "",
    ]

    for card in contract["cards"]:
        lines.extend([
            "### " + card["symbol"],
            "",
            "- Asset class: " + card["asset_class"],
            "- Market: " + card["market"],
            "- Status: " + card["status"],
            "- Risk level: " + card["risk_level"],
            "- Risk score: " + str(card["risk_score"]),
            "- Regime: " + card["regime"],
            "- Signal: " + card["signal"],
            "- Governor gate: " + card["governor_gate"],
            "- Policy gate: " + card["policy_gate"],
            "- Allowed action: " + card["allowed_action"],
            "",
        ])

    lines.extend([
        "## Final Notice",
        "",
        "This report is not financial advice.",
        "This report is not a real trading signal.",
        "This report must not be used for real execution.",
        "Stocks, ETFs, and crypto entries are paper-only contract inputs.",
        "",
    ])

    return {
        "ok": True,
        "type": "multi_market_markdown_report",
        "summary": summary,
        "contract": contract,
        "markdown": "\n".join(lines),
        "decision": "multi_market_markdown_report_paper_only",
        **paper_flags(),
    }


def write_multi_market_report_bundle(file_path: Any, output_dir: Any) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    report = build_multi_market_markdown_report(file_path)
    contract = report["contract"]

    markdown_path = directory / "multi_market_report.md"
    contract_path = directory / "multi_market_ui_contract.json"
    summary_path = directory / "multi_market_summary.json"

    markdown_path.write_text(report["markdown"], encoding="utf-8")
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(json.dumps(report["summary"], indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "multi_market_report_bundle_written",
        "output_dir": str(directory),
        "markdown_file": str(markdown_path),
        "contract_file": str(contract_path),
        "summary_file": str(summary_path),
        "report": report,
        **paper_flags(),
    }
