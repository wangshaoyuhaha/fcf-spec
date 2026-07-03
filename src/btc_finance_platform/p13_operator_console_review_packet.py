import json
from pathlib import Path
from typing import Any

from btc_finance_platform.p13_operator_console_snapshot import build_operator_console_status_snapshot


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


def build_operator_review_packet(output_path: str | Path) -> dict[str, Any]:
    snapshot = build_operator_console_status_snapshot(output_path)

    for field in MUST_BE_FALSE:
        if snapshot.get(field) is not False:
            raise ValueError(f"unsafe field must remain false: {field}")

    if snapshot.get("operator_review_required") is not True:
        raise ValueError("operator review must remain required")

    return {
        "ok": True,
        "type": "p13_operator_review_packet",
        "current_stage": "P13-D10-D12",
        "review_status": "WAITING_FOR_OPERATOR_REVIEW",
        "operator_action_allowed": "review_only",
        "ai_advice_mode": "paper_decision_draft_only",
        "safe_to_execute_real_money": False,
        "console_snapshot": snapshot,
        "review_checklist": [
            "confirm paper-only boundary",
            "confirm local-only read-only console",
            "confirm no trading buttons",
            "confirm no real exchange API",
            "confirm no brokerage API",
            "confirm no API keys",
            "confirm no wallet private keys",
            "confirm no real orders",
            "confirm no real execution",
            "confirm no real balances or positions",
            "confirm no real money impact",
        ],
        "allowed_actions": [
            "read_snapshot",
            "review_packet",
            "record_operator_review_note",
        ],
        "forbidden_actions": [
            "place_order",
            "execute_trade",
            "connect_exchange",
            "connect_brokerage",
            "use_api_key",
            "use_wallet_private_key",
            "read_real_balance",
            "read_real_position",
            "impact_real_money",
        ],
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "trading_buttons_enabled": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "operator_review_required": True,
    }


def write_operator_review_packet(
    output_path: str | Path,
    packet_path: str | Path,
) -> dict[str, Any]:
    packet = build_operator_review_packet(output_path)
    path = Path(packet_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p13_operator_review_packet_written",
        "packet_path": str(path),
        "packet": packet,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "trading_buttons_enabled": False,
        "real_world_actions_allowed": False,
        "operator_review_required": True,
    }
