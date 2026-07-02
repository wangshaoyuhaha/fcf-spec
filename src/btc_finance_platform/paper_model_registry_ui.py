import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_model_card import (
    build_model_registry_readable_report,
    build_operator_model_approval_gate,
    build_paper_model_card,
)
from btc_finance_platform.paper_model_registry import build_model_registry_baseline

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


def build_model_version_index(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    registry = build_model_registry_baseline(file_path, action_by_symbol, outcome_by_symbol)
    card = build_paper_model_card(file_path, action_by_symbol, outcome_by_symbol)
    gate = build_operator_model_approval_gate(file_path, action_by_symbol, outcome_by_symbol)

    record = {
        "model_version_id": card["model_version_id"],
        "strategy_version_id": card["strategy_version_id"],
        "registry_version": registry["registry_version"],
        "card_version": card["card_version"],
        "approval_gate": gate["gate"],
        "training_status": card["training_status"],
        "calibration_status": card["calibration_status"],
        "deployment_status": card["deployment_status"],
        "operator_approval_status": gate["approval_status"],
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "paper_only": True,
    }

    return {
        "ok": registry["ok"] is True and card["ok"] is True and gate["ok"] is True,
        "type": "model_version_index",
        "index_version": "p10_d7_model_version_index_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": 1,
        "records": [record],
        "by_model_version_id": {record["model_version_id"]: record},
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "decision": "model_version_index_paper_only",
        **paper_flags(),
    }


def build_model_registry_ui_contract(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    index = build_model_version_index(file_path, action_by_symbol, outcome_by_symbol)
    report = build_model_registry_readable_report(file_path, action_by_symbol, outcome_by_symbol)

    cards = []
    for record in index["records"]:
        cards.append({
            "card_id": "model_registry_card_" + record["model_version_id"],
            "title": "Paper model " + record["model_version_id"],
            "model_version_id": record["model_version_id"],
            "strategy_version_id": record["strategy_version_id"],
            "approval_gate": record["approval_gate"],
            "training_status": record["training_status"],
            "calibration_status": record["calibration_status"],
            "deployment_status": record["deployment_status"],
            "operator_approval_status": record["operator_approval_status"],
            "deployment_allowed_now": False,
            "parameter_update_allowed_now": False,
            "real_world_actions_allowed": False,
            "paper_only": True,
        })

    contract = {
        "ok": index["ok"] is True and report["ok"] is True,
        "type": "model_registry_ui_contract",
        "contract_version": "p10_d8_model_registry_ui_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "card_count": len(cards),
        "cards": cards,
        "views": [
            {"view_id": "model_versions", "title": "Model Versions", "paper_only": True},
            {"view_id": "approval_gates", "title": "Approval Gates", "paper_only": True},
            {"view_id": "model_registry_report", "title": "Registry Report", "paper_only": True},
            {"view_id": "safety", "title": "Safety", "paper_only": True},
        ],
        "source_index": index,
        "source_report_type": report["type"],
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "model_registry_ui_contract_paper_only",
        **paper_flags(),
    }

    contract["validation"] = validate_model_registry_ui_contract(contract)
    return contract


def validate_model_registry_ui_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("model_registry_ui_contract must be a dict")
    if contract.get("type") != "model_registry_ui_contract":
        raise ValueError("model_registry_ui_contract type is invalid")

    cards = contract.get("cards")
    views = contract.get("views")

    if not isinstance(cards, list):
        raise ValueError("model_registry_ui_contract.cards must be a list")
    if not isinstance(views, list):
        raise ValueError("model_registry_ui_contract.views must be a list")

    view_ids = [view.get("view_id") for view in views]

    checks = {
        "contract_ok": contract.get("ok") is True,
        "has_cards": len(cards) > 0,
        "has_model_versions_view": "model_versions" in view_ids,
        "has_approval_gates_view": "approval_gates" in view_ids,
        "has_report_view": "model_registry_report" in view_ids,
        "has_safety_view": "safety" in view_ids,
        "training_not_started": contract.get("training_status") == "not_trained",
        "calibration_not_started": contract.get("calibration_status") == "not_calibrated",
        "deployment_not_started": contract.get("deployment_status") == "not_deployed",
        "deployment_blocked": contract.get("deployment_allowed_now") is False,
        "parameter_updates_blocked": contract.get("parameter_update_allowed_now") is False,
        "real_world_actions_blocked": contract.get("real_world_actions_allowed") is False,
        "all_cards_paper_only": all(card.get("paper_only") is True for card in cards),
        "all_cards_block_deployment": all(card.get("deployment_allowed_now") is False for card in cards),
        "all_cards_block_parameter_updates": all(card.get("parameter_update_allowed_now") is False for card in cards),
        "all_cards_block_real_world_actions": all(card.get("real_world_actions_allowed") is False for card in cards),
        "all_views_paper_only": all(view.get("paper_only") is True for view in views),
        "paper_only_preserved": contract.get("paper_only") is True,
        "operator_review_required": contract.get("operator_review_required") is True,
        "no_real_order": contract.get("real_order") is False,
        "no_real_execution": contract.get("real_execution") is False,
        "no_real_money_impact": contract.get("real_money_impact") is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "model_registry_ui_contract_validation",
        "checks": checks,
        "decision": "model_registry_ui_validation_paper_only",
        **paper_flags(),
    }


def build_model_registry_ui_manifest(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    index = build_model_version_index(file_path, action_by_symbol, outcome_by_symbol)
    ui = build_model_registry_ui_contract(file_path, action_by_symbol, outcome_by_symbol)

    return {
        "ok": index["ok"] is True and ui["ok"] is True and ui["validation"]["ok"] is True,
        "type": "model_registry_ui_manifest",
        "manifest_version": "p10_d9_model_registry_ui_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_count": index["count"],
        "model_version_ids": [record["model_version_id"] for record in index["records"]],
        "views": ui["views"],
        "card_count": ui["card_count"],
        "validation": ui["validation"],
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "model_registry_ui_manifest_paper_only_ready",
        **paper_flags(),
    }


def write_model_registry_ui_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    index = build_model_version_index(file_path, action_by_symbol, outcome_by_symbol)
    ui = build_model_registry_ui_contract(file_path, action_by_symbol, outcome_by_symbol)
    manifest = build_model_registry_ui_manifest(file_path, action_by_symbol, outcome_by_symbol)

    index_file = directory / "model_version_index.json"
    ui_file = directory / "model_registry_ui_contract.json"
    manifest_file = directory / "model_registry_ui_manifest.json"

    index_file.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    ui_file.write_text(json.dumps(ui, indent=2, sort_keys=True), encoding="utf-8")
    manifest_file.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "model_registry_ui_bundle_written",
        "output_dir": str(directory),
        "index_file": str(index_file),
        "ui_file": str(ui_file),
        "manifest_file": str(manifest_file),
        "index": index,
        "ui": ui,
        "manifest": manifest,
        **paper_flags(),
    }
