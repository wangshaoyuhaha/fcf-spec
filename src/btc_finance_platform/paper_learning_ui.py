import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_learning_audit import build_feedback_to_calibration_handoff
from btc_finance_platform.paper_learning_audit import build_learning_memory_markdown_report
from btc_finance_platform.paper_learning_audit import build_learning_memory_summary


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


def build_learning_memory_ui_card(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("calibration row must be a dict")

    outcome = row["paper_outcome_status"]
    if outcome == "paper_success":
        display_status = "paper_success_recorded"
    elif outcome == "paper_failure":
        display_status = "paper_failure_recorded"
    elif outcome == "pending_outcome":
        display_status = "awaiting_paper_outcome"
    else:
        display_status = "paper_outcome_recorded"

    return {
        "ok": True,
        "type": "learning_memory_ui_card",
        "symbol": row["symbol"],
        "asset_class": row["asset_class"],
        "market": row["market"],
        "paper_signal": row["paper_signal"],
        "risk_level": row["risk_level"],
        "risk_score": row["risk_score"],
        "operator_action": row["operator_action"],
        "paper_outcome_status": outcome,
        "display_status": display_status,
        "calibration_use": row["calibration_use"],
        "training_status": "not_trained_not_calibrated_yet",
        "real_world_actions_allowed": False,
        "decision": "learning_memory_ui_card_paper_only",
        **paper_flags(),
    }


def build_learning_memory_ui_contract(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    summary = build_learning_memory_summary(file_path, action_by_symbol, outcome_by_symbol)
    handoff = build_feedback_to_calibration_handoff(file_path, action_by_symbol, outcome_by_symbol)
    cards = [build_learning_memory_ui_card(row) for row in handoff["rows"]]

    display_status_counts: dict[str, int] = {}
    for card in cards:
        status = card["display_status"]
        display_status_counts[status] = display_status_counts.get(status, 0) + 1

    contract = {
        "ok": True,
        "type": "learning_memory_ui_contract",
        "contract_version": "p8_d7_learning_memory_ui_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": summary["source_file"],
        "count": len(cards),
        "symbols": [card["symbol"] for card in cards],
        "action_counts": summary["action_counts"],
        "outcome_counts": summary["outcome_counts"],
        "risk_counts": summary["risk_counts"],
        "display_status_counts": display_status_counts,
        "training_status": summary["training_status"],
        "next_phase": summary["next_phase"],
        "cards": cards,
        "decision": "learning_memory_ui_contract_paper_only",
        **paper_flags(),
    }

    contract["validation"] = validate_learning_memory_ui_contract(contract)
    return contract


def validate_learning_memory_ui_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("learning_memory_ui_contract must be a dict")
    if contract.get("type") != "learning_memory_ui_contract":
        raise ValueError("learning_memory_ui_contract type is invalid")

    cards = contract.get("cards")
    if not isinstance(cards, list):
        raise ValueError("learning_memory_ui_contract.cards must be a list")

    checks = {
        "contract_ok": contract.get("ok") is True,
        "has_cards": len(cards) > 0,
        "count_matches_cards": contract.get("count") == len(cards),
        "training_not_started": contract.get("training_status") == "not_trained_not_calibrated_yet",
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
        "all_cards_block_real_world_actions": all(
            card.get("real_world_actions_allowed") is False for card in cards
        ),
    }

    return {
        "ok": all(checks.values()),
        "type": "learning_memory_ui_contract_validation",
        "checks": checks,
        "decision": "learning_memory_ui_contract_validation_paper_only",
        **paper_flags(),
    }


def build_learning_dataset_index(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    contract = build_learning_memory_ui_contract(file_path, action_by_symbol, outcome_by_symbol)

    by_symbol = {}
    by_outcome: dict[str, list[str]] = {}
    by_action: dict[str, list[str]] = {}

    for card in contract["cards"]:
        symbol = card["symbol"]
        outcome = card["paper_outcome_status"]
        action = card["operator_action"]
        by_symbol[symbol] = {
            "symbol": symbol,
            "asset_class": card["asset_class"],
            "market": card["market"],
            "risk_level": card["risk_level"],
            "risk_score": card["risk_score"],
            "operator_action": action,
            "paper_outcome_status": outcome,
            "training_status": card["training_status"],
        }
        by_outcome.setdefault(outcome, []).append(symbol)
        by_action.setdefault(action, []).append(symbol)

    return {
        "ok": True,
        "type": "learning_dataset_index",
        "index_version": "p8_d8_learning_dataset_index_v1",
        "count": contract["count"],
        "symbols": contract["symbols"],
        "by_symbol": by_symbol,
        "by_outcome": by_outcome,
        "by_action": by_action,
        "training_status": contract["training_status"],
        "decision": "learning_dataset_index_paper_only",
        **paper_flags(),
    }


def build_learning_memory_ui_manifest(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    contract = build_learning_memory_ui_contract(file_path, action_by_symbol, outcome_by_symbol)
    index = build_learning_dataset_index(file_path, action_by_symbol, outcome_by_symbol)

    manifest = {
        "ok": True,
        "type": "learning_memory_ui_manifest",
        "manifest_version": "p8_d9_learning_memory_ui_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "views": [
            {"view_id": "learning_summary", "title": "Learning Summary", "paper_only": True},
            {"view_id": "feedback_dataset", "title": "Feedback Dataset", "paper_only": True},
            {"view_id": "outcome_tracking", "title": "Outcome Tracking", "paper_only": True},
            {"view_id": "calibration_handoff", "title": "Calibration Handoff", "paper_only": True},
            {"view_id": "safety", "title": "Learning Safety Boundary", "paper_only": True},
        ],
        "contract_version": contract["contract_version"],
        "index_version": index["index_version"],
        "training_status": contract["training_status"],
        "count": contract["count"],
        "symbols": contract["symbols"],
        "decision": "learning_memory_ui_manifest_paper_only",
        **paper_flags(),
    }

    manifest["validation"] = validate_learning_memory_ui_manifest(manifest)
    return manifest


def validate_learning_memory_ui_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("learning_memory_ui_manifest must be a dict")
    if manifest.get("type") != "learning_memory_ui_manifest":
        raise ValueError("learning_memory_ui_manifest type is invalid")

    views = manifest.get("views")
    if not isinstance(views, list):
        raise ValueError("learning_memory_ui_manifest.views must be a list")

    checks = {
        "manifest_ok": manifest.get("ok") is True,
        "has_views": len(views) >= 5,
        "all_views_paper_only": all(view.get("paper_only") is True for view in views),
        "training_not_started": manifest.get("training_status") == "not_trained_not_calibrated_yet",
        "paper_only_preserved": manifest.get("paper_only") is True,
        "operator_review_required": manifest.get("operator_review_required") is True,
        "no_real_exchange_api": manifest.get("real_exchange_api") is False,
        "no_real_brokerage_api": manifest.get("real_brokerage_api") is False,
        "no_real_order": manifest.get("real_order") is False,
        "no_real_execution": manifest.get("real_execution") is False,
        "no_real_money_impact": manifest.get("real_money_impact") is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "learning_memory_ui_manifest_validation",
        "checks": checks,
        "decision": "learning_memory_ui_manifest_validation_paper_only",
        **paper_flags(),
    }


def write_learning_memory_ui_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    contract = build_learning_memory_ui_contract(file_path, action_by_symbol, outcome_by_symbol)
    index = build_learning_dataset_index(file_path, action_by_symbol, outcome_by_symbol)
    manifest = build_learning_memory_ui_manifest(file_path, action_by_symbol, outcome_by_symbol)
    report = build_learning_memory_markdown_report(file_path, action_by_symbol, outcome_by_symbol)

    contract_path = directory / "learning_memory_ui_contract.json"
    index_path = directory / "learning_dataset_index.json"
    manifest_path = directory / "learning_memory_ui_manifest.json"
    report_path = directory / "learning_memory_ui_report.md"

    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(report["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "learning_memory_ui_bundle_written",
        "output_dir": str(directory),
        "contract_file": str(contract_path),
        "index_file": str(index_path),
        "manifest_file": str(manifest_path),
        "report_file": str(report_path),
        "contract": contract,
        "index": index,
        "manifest": manifest,
        **paper_flags(),
    }
