import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_calibration_proposal import (
    build_calibration_proposal_contract,
    build_calibration_ui_contract,
    build_risk_bucket_performance_index,
)

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


def build_calibration_acceptance_gate(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    performance = build_risk_bucket_performance_index(file_path, action_by_symbol, outcome_by_symbol)
    proposal = build_calibration_proposal_contract(file_path, action_by_symbol, outcome_by_symbol)
    ui = build_calibration_ui_contract(file_path, action_by_symbol, outcome_by_symbol)

    checks = {
        "performance_ok": performance["ok"] is True,
        "proposal_ok": proposal["ok"] is True,
        "ui_ok": ui["ok"] is True,
        "ui_validation_ok": ui["validation"]["ok"] is True,
        "has_proposals": proposal["proposal_count"] > 0,
        "training_not_started": proposal["training_status"] == "not_trained",
        "calibration_not_started": proposal["calibration_status"] == "not_calibrated",
        "all_parameter_updates_blocked": all(
            item["parameter_update_allowed_now"] is False for item in proposal["proposals"]
        ),
        "all_real_world_actions_blocked": all(
            item["real_world_actions_allowed"] is False for item in proposal["proposals"]
        ),
        "paper_only_preserved": proposal["paper_only"] is True,
        "operator_review_required": proposal["operator_review_required"] is True,
        "no_real_order": proposal["real_order"] is False,
        "no_real_execution": proposal["real_execution"] is False,
        "no_real_money_impact": proposal["real_money_impact"] is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "calibration_acceptance_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "gate_version": "p9_d10_calibration_acceptance_gate_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "proposal_count": proposal["proposal_count"],
        "checks": checks,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "calibration_acceptance_gate_paper_only_no_parameter_update",
        **paper_flags(),
    }


def build_backtest_ui_readiness_gate(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    ui = build_calibration_ui_contract(file_path, action_by_symbol, outcome_by_symbol)

    view_ids = [view["view_id"] for view in ui["views"]]

    checks = {
        "ui_ok": ui["ok"] is True,
        "ui_validation_ok": ui["validation"]["ok"] is True,
        "has_cards": ui["card_count"] > 0,
        "has_performance_view": "risk_bucket_performance" in view_ids,
        "has_proposal_view": "calibration_proposals" in view_ids,
        "has_safety_view": "safety" in view_ids,
        "training_not_started": ui["training_status"] == "not_trained",
        "calibration_not_started": ui["calibration_status"] == "not_calibrated",
        "all_cards_block_parameter_updates": all(
            card["parameter_update_allowed_now"] is False for card in ui["cards"]
        ),
        "all_cards_block_real_world_actions": all(
            card["real_world_actions_allowed"] is False for card in ui["cards"]
        ),
        "all_views_paper_only": all(view["paper_only"] is True for view in ui["views"]),
        "paper_only_preserved": ui["paper_only"] is True,
        "operator_review_required": ui["operator_review_required"] is True,
    }

    return {
        "ok": all(checks.values()),
        "type": "backtest_ui_readiness_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "gate_version": "p9_d11_backtest_ui_readiness_gate_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "card_count": ui["card_count"],
        "view_ids": view_ids,
        "checks": checks,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "backtest_ui_readiness_gate_paper_only",
        **paper_flags(),
    }


def build_p9_readiness_bundle(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    acceptance = build_calibration_acceptance_gate(file_path, action_by_symbol, outcome_by_symbol)
    ui_readiness = build_backtest_ui_readiness_gate(file_path, action_by_symbol, outcome_by_symbol)
    proposal = build_calibration_proposal_contract(file_path, action_by_symbol, outcome_by_symbol)

    return {
        "ok": acceptance["ok"] is True and ui_readiness["ok"] is True and proposal["ok"] is True,
        "type": "p9_readiness_bundle",
        "bundle_version": "p9_d12_readiness_bundle_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "acceptance_gate": acceptance,
        "ui_readiness_gate": ui_readiness,
        "proposal_contract": proposal,
        "accepted_for": "future_p9_closeout_and_p10_model_registry_handoff",
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "p9_readiness_bundle_paper_only_no_live_use",
        **paper_flags(),
    }


def write_p9_readiness_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    bundle = build_p9_readiness_bundle(file_path, action_by_symbol, outcome_by_symbol)

    acceptance_file = directory / "calibration_acceptance_gate.json"
    ui_file = directory / "backtest_ui_readiness_gate.json"
    bundle_file = directory / "p9_readiness_bundle.json"

    acceptance_file.write_text(json.dumps(bundle["acceptance_gate"], indent=2, sort_keys=True), encoding="utf-8")
    ui_file.write_text(json.dumps(bundle["ui_readiness_gate"], indent=2, sort_keys=True), encoding="utf-8")
    bundle_file.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p9_readiness_bundle_written",
        "output_dir": str(directory),
        "acceptance_file": str(acceptance_file),
        "ui_file": str(ui_file),
        "bundle_file": str(bundle_file),
        "bundle": bundle,
        **paper_flags(),
    }
