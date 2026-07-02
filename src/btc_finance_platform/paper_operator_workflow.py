import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_operator_console import build_operator_console_contract
from btc_finance_platform.paper_operator_console import build_operator_review_queue


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


VALID_OPERATOR_ACTIONS = {"pending", "approved", "rejected"}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def normalize_operator_action(action: str) -> str:
    value = str(action).strip().lower()
    if value not in VALID_OPERATOR_ACTIONS:
        raise ValueError("operator action must be pending, approved, or rejected")
    return value


def build_operator_review_action(
    queue_item: dict[str, Any],
    operator_action: str = "pending",
    operator_note: str = "",
) -> dict[str, Any]:
    if not isinstance(queue_item, dict):
        raise ValueError("queue_item must be a dict")

    action = normalize_operator_action(operator_action)

    if action == "approved":
        workflow_gate = "paper_review_approved"
        allowed_next_step = "archive_paper_review_result"
    elif action == "rejected":
        workflow_gate = "paper_review_rejected"
        allowed_next_step = "archive_rejection_and_wait"
    else:
        workflow_gate = "paper_review_pending"
        allowed_next_step = "wait_for_operator_review"

    return {
        "ok": True,
        "type": "operator_review_action",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "queue_id": queue_item["queue_id"],
        "symbol": queue_item["symbol"],
        "asset_class": queue_item["asset_class"],
        "market": queue_item["market"],
        "operator_action": action,
        "operator_note": str(operator_note),
        "workflow_gate": workflow_gate,
        "allowed_next_step": allowed_next_step,
        "real_world_actions_allowed": False,
        "blocked_real_world_actions": queue_item["blocked_real_world_actions"],
        "decision": "operator_review_action_paper_only",
        **paper_flags(),
    }


def build_operator_workflow_state(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    review_queue = build_operator_review_queue(file_path)
    action_map = action_by_symbol or {}

    actions = []
    for item in review_queue["items"]:
        symbol = item["symbol"]
        action = action_map.get(symbol, "pending")
        actions.append(build_operator_review_action(item, action))

    action_counts: dict[str, int] = {}
    for item in actions:
        action = item["operator_action"]
        action_counts[action] = action_counts.get(action, 0) + 1

    all_reviewed = all(item["operator_action"] in {"approved", "rejected"} for item in actions)

    return {
        "ok": True,
        "type": "operator_workflow_state",
        "workflow_version": "p7_d4_operator_workflow_state_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(actions),
        "symbols": [item["symbol"] for item in actions],
        "action_counts": action_counts,
        "all_reviewed": all_reviewed,
        "review_queue": review_queue,
        "actions": actions,
        "decision": "operator_workflow_state_paper_only",
        **paper_flags(),
    }


def build_operator_workflow_summary(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    state = build_operator_workflow_state(file_path, action_by_symbol)

    return {
        "ok": True,
        "type": "operator_workflow_summary",
        "count": state["count"],
        "symbols": state["symbols"],
        "action_counts": state["action_counts"],
        "all_reviewed": state["all_reviewed"],
        "allowed_global_next_step": "paper_archive_only" if state["all_reviewed"] else "continue_operator_review",
        "real_world_actions_allowed": False,
        "decision": "operator_workflow_summary_paper_only",
        **paper_flags(),
    }


def validate_operator_workflow_state(state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise ValueError("operator_workflow_state must be a dict")
    if state.get("type") != "operator_workflow_state":
        raise ValueError("operator_workflow_state type is invalid")

    actions = state.get("actions")
    if not isinstance(actions, list):
        raise ValueError("operator_workflow_state.actions must be a list")

    checks = {
        "state_ok": state.get("ok") is True,
        "has_actions": len(actions) > 0,
        "count_matches_actions": state.get("count") == len(actions),
        "paper_only_preserved": state.get("paper_only") is True,
        "operator_review_required": state.get("operator_review_required") is True,
        "no_real_exchange_api": state.get("real_exchange_api") is False,
        "no_real_brokerage_api": state.get("real_brokerage_api") is False,
        "no_real_api_key_required": state.get("real_api_key_required") is False,
        "no_wallet_private_key_required": state.get("wallet_private_key_required") is False,
        "no_real_order": state.get("real_order") is False,
        "no_real_execution": state.get("real_execution") is False,
        "no_real_balance": state.get("real_balance") is False,
        "no_real_position": state.get("real_position") is False,
        "no_real_money_impact": state.get("real_money_impact") is False,
        "all_actions_block_real_world_actions": all(
            item.get("real_world_actions_allowed") is False
            for item in actions
        ),
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_workflow_state_validation",
        "checks": checks,
        "decision": "operator_workflow_validation_paper_only",
        **paper_flags(),
    }


def build_cli_to_ui_artifact_export_bridge(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    console = build_operator_console_contract(file_path)
    state = build_operator_workflow_state(file_path, action_by_symbol)
    summary = build_operator_workflow_summary(file_path, action_by_symbol)
    validation = validate_operator_workflow_state(state)

    return {
        "ok": console["ok"] is True and state["ok"] is True and summary["ok"] is True and validation["ok"] is True,
        "type": "cli_to_ui_artifact_export_bridge",
        "bridge_version": "p7_d6_cli_to_ui_bridge_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "console_contract_version": console["contract_version"],
        "workflow_version": state["workflow_version"],
        "console": console,
        "workflow_state": state,
        "workflow_summary": summary,
        "workflow_validation": validation,
        "export_targets": [
            "operator_console_contract.json",
            "operator_workflow_state.json",
            "operator_workflow_summary.json",
            "cli_to_ui_artifact_export_bridge.json",
        ],
        "decision": "cli_to_ui_bridge_paper_only",
        **paper_flags(),
    }


def write_operator_workflow_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    bridge = build_cli_to_ui_artifact_export_bridge(file_path, action_by_symbol)
    console_path = directory / "operator_console_contract.json"
    state_path = directory / "operator_workflow_state.json"
    summary_path = directory / "operator_workflow_summary.json"
    bridge_path = directory / "cli_to_ui_artifact_export_bridge.json"

    console_path.write_text(json.dumps(bridge["console"], indent=2, sort_keys=True), encoding="utf-8")
    state_path.write_text(json.dumps(bridge["workflow_state"], indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(json.dumps(bridge["workflow_summary"], indent=2, sort_keys=True), encoding="utf-8")
    bridge_path.write_text(json.dumps(bridge, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "operator_workflow_bundle_written",
        "output_dir": str(directory),
        "console_file": str(console_path),
        "state_file": str(state_path),
        "summary_file": str(summary_path),
        "bridge_file": str(bridge_path),
        "bridge": bridge,
        **paper_flags(),
    }
