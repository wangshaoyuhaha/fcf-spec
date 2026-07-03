import json
from pathlib import Path
from typing import Any

from btc_finance_platform.p13_operator_console_launcher import build_operator_console_launch_plan


FORBIDDEN_TRUE_FIELDS = (
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


def build_operator_console_status_snapshot(output_path: str | Path) -> dict[str, Any]:
    plan = build_operator_console_launch_plan(output_path)

    for field in FORBIDDEN_TRUE_FIELDS:
        if plan.get(field) is not False:
            raise ValueError(f"unsafe field must remain false: {field}")

    return {
        "ok": True,
        "type": "p13_operator_console_status_snapshot",
        "current_stage": "P13-D7-D9",
        "status_line": "READ_ONLY_LOCAL_PAPER_OPERATOR_REVIEW_REQUIRED",
        "launch_status": plan["launch_status"],
        "operator_console_ready": plan["operator_console_ready"],
        "output_path": plan["output_path"],
        "file_url": plan["file_url"],
        "ui_mode": "read_only",
        "local_only": True,
        "paper_only": True,
        "allowed_actions": [
            "open_local_html",
            "read_status",
            "review_only",
        ],
        "forbidden_actions": [
            "no_trading_buttons",
            "no_real_exchange_api",
            "no_real_brokerage_api",
            "no_api_keys",
            "no_wallet_private_keys",
            "no_real_orders",
            "no_real_execution",
            "no_real_balances",
            "no_real_positions",
            "no_real_money_impact",
        ],
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
        "blocked_reasons": plan["blocked_reasons"],
    }


def write_operator_console_status_snapshot(
    output_path: str | Path,
    snapshot_path: str | Path,
) -> dict[str, Any]:
    snapshot = build_operator_console_status_snapshot(output_path)
    path = Path(snapshot_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "ok": True,
        "type": "p13_operator_console_status_snapshot_written",
        "snapshot_path": str(path),
        "snapshot": snapshot,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "trading_buttons_enabled": False,
        "real_world_actions_allowed": False,
        "operator_review_required": True,
    }
