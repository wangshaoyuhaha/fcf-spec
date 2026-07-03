import json
from pathlib import Path
from typing import Any

from btc_finance_platform.p13_operator_console_review_packet import build_operator_review_packet


MUST_BE_FALSE = (
    "trading_buttons_enabled",
    "real_exchange_api",
    "real_brokerage_api",
    "real_api_key_required",
    "wallet_private_key_required",
    "real_order",
    "real_execution",
    "real_balance",
    "real_position",
    "real_money_impact",
    "real_world_actions_allowed",
    "deployment_allowed_now",
)


def build_operator_console_acceptance_summary(output_path: str | Path) -> dict[str, Any]:
    packet = build_operator_review_packet(output_path)

    for field in MUST_BE_FALSE:
        if packet.get(field) is not False:
            raise ValueError(f"unsafe field must remain false: {field}")

    if packet.get("operator_review_required") is not True:
        raise ValueError("operator review must remain required")

    if packet.get("review_status") != "WAITING_FOR_OPERATOR_REVIEW":
        raise ValueError("review status must remain waiting for operator review")

    return {
        "ok": True,
        "type": "p13_operator_console_acceptance_summary",
        "current_stage": "P13-D13-D15",
        "acceptance_status": "ACCEPTED_FOR_READ_ONLY_PAPER_CONSOLE",
        "p13_scope_closed": True,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "no_trading_buttons": True,
        "no_real_exchange_api": True,
        "no_real_brokerage_api": True,
        "no_api_keys": True,
        "no_wallet_private_keys": True,
        "no_real_orders": True,
        "no_real_execution": True,
        "no_real_balances_or_positions": True,
        "no_real_money_impact": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "safe_to_execute_real_money": False,
        "operator_action_allowed": "review_only",
        "ai_advice_mode": "paper_decision_draft_only",
        "closeout_notes": [
            "operator console is local-only",
            "operator console is read-only",
            "operator console is paper-only",
            "operator review remains required",
            "real-money execution remains blocked",
        ],
        "review_packet": packet,
    }


def write_operator_console_acceptance_summary(
    output_path: str | Path,
    summary_path: str | Path,
) -> dict[str, Any]:
    summary = build_operator_console_acceptance_summary(output_path)
    path = Path(summary_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p13_operator_console_acceptance_summary_written",
        "summary_path": str(path),
        "summary": summary,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "trading_buttons_enabled": False,
        "real_world_actions_allowed": False,
        "operator_review_required": True,
    }
