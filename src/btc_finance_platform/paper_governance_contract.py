import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_governance_report import build_governance_markdown_report


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
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


def require_governance_markdown_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("governance_markdown_report must be a dict")
    if report.get("ok") is not True:
        raise ValueError("governance_markdown_report must be ok")
    if report.get("type") != "governance_markdown_report":
        raise ValueError("governance_markdown_report type is invalid")
    return report


def build_governance_ui_card(
    governor_decision: dict[str, Any],
    policy_gate: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(governor_decision, dict):
        raise ValueError("governor_decision must be a dict")
    if not isinstance(policy_gate, dict):
        raise ValueError("policy_gate must be a dict")

    symbol = governor_decision["symbol"]
    gate = governor_decision["gate"]
    policy_gate_value = policy_gate["gate"]

    if gate == "blocked_for_escalation":
        status = "needs_manual_review"
    elif policy_gate_value == "pass":
        status = "paper_review_allowed"
    else:
        status = "policy_check_failed"

    return {
        "ok": True,
        "type": "governance_ui_card",
        "symbol": symbol,
        "status": status,
        "governor_gate": gate,
        "policy_gate": policy_gate_value,
        "allowed_action": governor_decision["allowed_action"],
        "risk_level": governor_decision["risk_level"],
        "risk_score": governor_decision["risk_score"],
        "regime": governor_decision["regime"]["regime"],
        "signal": governor_decision["signal"],
        "blocked_reasons": governor_decision["blocked_reasons"],
        "warnings": governor_decision["warnings"],
        "blocked_real_world_actions": policy_gate["blocked_real_world_actions"],
        "decision": "ui_card_paper_only_no_real_trade",
        **paper_flags(),
    }


def validate_governance_ui_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("governance_ui_contract must be a dict")
    if contract.get("type") != "governance_ui_contract":
        raise ValueError("governance_ui_contract type is invalid")

    cards = contract.get("cards")
    if not isinstance(cards, list):
        raise ValueError("governance_ui_contract.cards must be a list")

    checks = {
        "contract_ok": contract.get("ok") is True,
        "has_cards": len(cards) > 0,
        "count_matches_cards": contract.get("count") == len(cards),
        "paper_only_preserved": contract.get("paper_only") is True,
        "operator_review_required": contract.get("operator_review_required") is True,
        "no_real_exchange_api": contract.get("real_exchange_api") is False,
        "no_real_api_key_required": contract.get("real_api_key_required") is False,
        "no_wallet_private_key_required": contract.get("wallet_private_key_required") is False,
        "no_real_order": contract.get("real_order") is False,
        "no_real_execution": contract.get("real_execution") is False,
        "no_real_balance": contract.get("real_balance") is False,
        "no_real_position": contract.get("real_position") is False,
        "no_real_money_impact": contract.get("real_money_impact") is False,
        "all_cards_paper_only": all(card.get("paper_only") is True for card in cards),
        "all_cards_block_real_order": all(card.get("real_order") is False for card in cards),
    }

    return {
        "ok": all(checks.values()),
        "type": "governance_ui_contract_validation",
        "checks": checks,
        "decision": "contract_validation_paper_only",
        **paper_flags(),
    }


def build_governance_ui_contract(
    file_paths: list[Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    report = build_governance_markdown_report(file_paths, operator_status)
    report = require_governance_markdown_report(report)
    audit_trail = report["audit_trail"]
    governance_report = audit_trail["governance_report"]

    cards = []
    for governor_decision, policy_gate in zip(
        governance_report["governor_decisions"],
        governance_report["policy_gates"],
    ):
        cards.append(build_governance_ui_card(governor_decision, policy_gate))

    status_counts: dict[str, int] = {}
    for card in cards:
        status = card["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    contract = {
        "ok": True,
        "type": "governance_ui_contract",
        "contract_version": "p5_d10_governance_ui_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "operator_status": operator_status,
        "count": len(cards),
        "symbols": [card["symbol"] for card in cards],
        "status_counts": status_counts,
        "summary": report["summary"],
        "cards": cards,
        "markdown": report["markdown"],
        "decision": "governance_ui_contract_paper_only",
        **paper_flags(),
    }

    contract["validation"] = validate_governance_ui_contract(contract)
    return contract


def build_governance_decision_index(
    file_paths: list[Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    contract = build_governance_ui_contract(file_paths, operator_status)

    by_symbol = {}
    review_queue = []

    for card in contract["cards"]:
        by_symbol[card["symbol"]] = {
            "symbol": card["symbol"],
            "status": card["status"],
            "governor_gate": card["governor_gate"],
            "policy_gate": card["policy_gate"],
            "risk_level": card["risk_level"],
            "regime": card["regime"],
            "allowed_action": card["allowed_action"],
        }
        review_queue.append(card["symbol"])

    return {
        "ok": True,
        "type": "governance_decision_index",
        "count": contract["count"],
        "symbols": contract["symbols"],
        "by_symbol": by_symbol,
        "review_queue": review_queue,
        "status_counts": contract["status_counts"],
        "decision": "decision_index_paper_only",
        **paper_flags(),
    }


def write_governance_contract_bundle(
    file_paths: list[Any],
    output_dir: Any,
    operator_status: str = "pending",
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    contract = build_governance_ui_contract(file_paths, operator_status)
    index = build_governance_decision_index(file_paths, operator_status)

    contract_path = directory / "governance_ui_contract.json"
    index_path = directory / "governance_decision_index.json"
    markdown_path = directory / "governance_ui_contract.md"

    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(contract["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "governance_contract_bundle_written",
        "output_dir": str(directory),
        "contract_file": str(contract_path),
        "index_file": str(index_path),
        "markdown_file": str(markdown_path),
        "contract": contract,
        "index": index,
        **paper_flags(),
    }
