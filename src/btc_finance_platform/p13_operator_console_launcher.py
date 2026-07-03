from pathlib import Path
from typing import Any

from btc_finance_platform.p13_operator_console import build_operator_console_state
from btc_finance_platform.p13_operator_console import write_operator_console_html


def default_operator_console_inputs() -> dict[str, Any]:
    return {
        "project_state": {
            "project_name": "BTC finance platform",
            "current_stage": "P13-D4-D6",
            "paper_only": True,
            "operator_review_required": True,
            "ui_mode": "read_only",
            "local_only": True,
            "trading_buttons_enabled": False,
        },
        "validation_summary": {
            "all_checks_passed": True,
            "pytest_passed": True,
            "pytest_count": 439,
        },
        "release_summary": {
            "release_published": True,
            "release_tag": "v12-paper-final-archive",
        },
    }


def build_operator_console_launch_plan(output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    inputs = default_operator_console_inputs()
    state = build_operator_console_state(
        inputs["project_state"],
        inputs["validation_summary"],
        inputs["release_summary"],
    )
    write_result = write_operator_console_html(state, path)

    return {
        "ok": True,
        "type": "p13_operator_console_launch_plan",
        "launch_status": "ready" if state["operator_console_ready"] else "blocked",
        "operator_console_ready": state["operator_console_ready"],
        "output_path": write_result["output_path"],
        "file_url": path.resolve().as_uri(),
        "ui_mode": "read_only",
        "local_only": True,
        "paper_only": True,
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
        "blocked_reasons": state["blocked_reasons"],
    }
