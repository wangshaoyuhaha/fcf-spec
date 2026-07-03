import json
from pathlib import Path
from typing import Any

from btc_finance_platform.p13_operator_console_acceptance import build_operator_console_acceptance_summary


def build_p13_branch_closeout_manifest(output_path: str | Path) -> dict[str, Any]:
    acceptance = build_operator_console_acceptance_summary(output_path)

    if acceptance.get("p13_scope_closed") is not True:
        raise ValueError("P13 scope must be closed before branch closeout")

    if acceptance.get("safe_to_execute_real_money") is not False:
        raise ValueError("real money execution must remain blocked")

    if acceptance.get("operator_review_required") is not True:
        raise ValueError("operator review must remain required")

    return {
        "ok": True,
        "type": "p13_branch_closeout_manifest",
        "current_stage": "P13-D16-D18",
        "branch_name": "p13-operator-console",
        "closeout_status": "READY_FOR_BRANCH_REVIEW",
        "p13_operator_console_completed": True,
        "p13_scope_closed": True,
        "ready_for_main_merge_review": True,
        "merge_to_main_completed": False,
        "release_created": False,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "operator_review_required": True,
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
        "acceptance_summary": acceptance,
        "completed_p13_units": [
            "P13-D1-D3 read-only operator console skeleton",
            "P13-D4-D6 operator console launcher",
            "P13-D7-D9 operator console status snapshot",
            "P13-D10-D12 operator review packet",
            "P13-D13-D15 operator console acceptance summary",
            "P13-D16-D18 branch closeout manifest",
        ],
        "next_manual_step": "review branch before merge; do not merge automatically",
    }


def write_p13_branch_closeout_manifest(
    output_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    manifest = build_p13_branch_closeout_manifest(output_path)
    path = Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p13_branch_closeout_manifest_written",
        "manifest_path": str(path),
        "manifest": manifest,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "trading_buttons_enabled": False,
        "real_world_actions_allowed": False,
        "operator_review_required": True,
    }
