import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_backtest_metrics import build_calibration_evaluation_baseline

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


def build_risk_bucket_performance_index(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    evaluation = build_calibration_evaluation_baseline(file_path, action_by_symbol, outcome_by_symbol)

    index = {}
    for bucket in evaluation["buckets"]:
        risk_level = bucket["risk_level"]
        if bucket["usable_count"] == 0:
            performance_label = "insufficient_data"
        elif bucket["average_outcome_score"] > 0:
            performance_label = "positive_paper_performance"
        elif bucket["average_outcome_score"] < 0:
            performance_label = "negative_paper_performance"
        else:
            performance_label = "neutral_paper_performance"

        index[risk_level] = {
            "risk_level": risk_level,
            "count": bucket["count"],
            "usable_count": bucket["usable_count"],
            "average_outcome_score": bucket["average_outcome_score"],
            "needs_more_data": bucket["needs_more_data"],
            "performance_label": performance_label,
            "real_world_actions_allowed": False,
        }

    return {
        "ok": True,
        "type": "risk_bucket_performance_index",
        "index_version": "p9_d7_risk_bucket_performance_index_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "bucket_count": len(index),
        "by_risk_level": index,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "risk_bucket_performance_index_paper_only",
        **paper_flags(),
    }


def build_calibration_proposal_contract(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    performance = build_risk_bucket_performance_index(file_path, action_by_symbol, outcome_by_symbol)

    proposals = []
    for risk_level, item in performance["by_risk_level"].items():
        if item["needs_more_data"]:
            proposal = "collect_more_paper_data"
        elif item["performance_label"] == "negative_paper_performance":
            proposal = "future_review_tighten_risk_threshold"
        elif item["performance_label"] == "positive_paper_performance":
            proposal = "future_review_keep_or_relax_paper_threshold"
        else:
            proposal = "future_review_keep_current_paper_threshold"

        proposals.append({
            "risk_level": risk_level,
            "performance_label": item["performance_label"],
            "average_outcome_score": item["average_outcome_score"],
            "usable_count": item["usable_count"],
            "proposal": proposal,
            "proposal_status": "operator_review_required_before_any_future_change",
            "parameter_update_allowed_now": False,
            "real_world_actions_allowed": False,
        })

    return {
        "ok": True,
        "type": "calibration_proposal_contract",
        "contract_version": "p9_d8_calibration_proposal_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "proposal_count": len(proposals),
        "proposals": proposals,
        "source_performance_index": performance,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "calibration_proposal_requires_operator_review_no_parameter_update",
        **paper_flags(),
    }


def build_calibration_ui_contract(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    proposal = build_calibration_proposal_contract(file_path, action_by_symbol, outcome_by_symbol)

    cards = []
    for item in proposal["proposals"]:
        cards.append({
            "risk_level": item["risk_level"],
            "title": "Risk bucket " + item["risk_level"],
            "performance_label": item["performance_label"],
            "average_outcome_score": item["average_outcome_score"],
            "usable_count": item["usable_count"],
            "proposal": item["proposal"],
            "proposal_status": item["proposal_status"],
            "parameter_update_allowed_now": False,
            "real_world_actions_allowed": False,
            "paper_only": True,
        })

    contract = {
        "ok": True,
        "type": "calibration_ui_contract",
        "contract_version": "p9_d9_calibration_ui_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "card_count": len(cards),
        "cards": cards,
        "views": [
            {"view_id": "risk_bucket_performance", "title": "Risk Bucket Performance", "paper_only": True},
            {"view_id": "calibration_proposals", "title": "Calibration Proposals", "paper_only": True},
            {"view_id": "safety", "title": "Calibration Safety", "paper_only": True},
        ],
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "calibration_ui_contract_paper_only_no_parameter_update",
        **paper_flags(),
    }

    contract["validation"] = validate_calibration_ui_contract(contract)
    return contract


def validate_calibration_ui_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("calibration_ui_contract must be a dict")
    if contract.get("type") != "calibration_ui_contract":
        raise ValueError("calibration_ui_contract type is invalid")

    cards = contract.get("cards")
    if not isinstance(cards, list):
        raise ValueError("calibration_ui_contract.cards must be a list")

    checks = {
        "contract_ok": contract.get("ok") is True,
        "has_cards": len(cards) > 0,
        "training_not_started": contract.get("training_status") == "not_trained",
        "calibration_not_started": contract.get("calibration_status") == "not_calibrated",
        "paper_only_preserved": contract.get("paper_only") is True,
        "operator_review_required": contract.get("operator_review_required") is True,
        "no_real_order": contract.get("real_order") is False,
        "no_real_execution": contract.get("real_execution") is False,
        "no_real_money_impact": contract.get("real_money_impact") is False,
        "all_cards_block_updates": all(card.get("parameter_update_allowed_now") is False for card in cards),
        "all_cards_block_real_world_actions": all(card.get("real_world_actions_allowed") is False for card in cards),
        "all_cards_paper_only": all(card.get("paper_only") is True for card in cards),
    }

    return {
        "ok": all(checks.values()),
        "type": "calibration_ui_contract_validation",
        "checks": checks,
        "decision": "calibration_ui_contract_validation_paper_only",
        **paper_flags(),
    }


def write_calibration_proposal_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    performance = build_risk_bucket_performance_index(file_path, action_by_symbol, outcome_by_symbol)
    proposal = build_calibration_proposal_contract(file_path, action_by_symbol, outcome_by_symbol)
    ui = build_calibration_ui_contract(file_path, action_by_symbol, outcome_by_symbol)

    performance_file = directory / "risk_bucket_performance_index.json"
    proposal_file = directory / "calibration_proposal_contract.json"
    ui_file = directory / "calibration_ui_contract.json"

    performance_file.write_text(json.dumps(performance, indent=2, sort_keys=True), encoding="utf-8")
    proposal_file.write_text(json.dumps(proposal, indent=2, sort_keys=True), encoding="utf-8")
    ui_file.write_text(json.dumps(ui, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "calibration_proposal_bundle_written",
        "output_dir": str(directory),
        "performance_file": str(performance_file),
        "proposal_file": str(proposal_file),
        "ui_file": str(ui_file),
        "performance": performance,
        "proposal": proposal,
        "ui": ui,
        **paper_flags(),
    }
