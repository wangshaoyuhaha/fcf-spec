import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_learning_ui import build_learning_dataset_index
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_contract
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_manifest

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

def build_learning_dataset_quality_gate(file_path: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    contract = build_learning_memory_ui_contract(file_path, action_by_symbol, outcome_by_symbol)
    index = build_learning_dataset_index(file_path, action_by_symbol, outcome_by_symbol)
    cards = contract["cards"]
    known = {"pending_outcome", "paper_success", "paper_failure", "paper_neutral", "inconclusive"}
    checks = {
        "contract_ok": contract["ok"] is True,
        "contract_validation_ok": contract["validation"]["ok"] is True,
        "index_ok": index["ok"] is True,
        "has_cards": len(cards) > 0,
        "count_matches_index": contract["count"] == index["count"],
        "all_symbols_indexed": all(symbol in index["by_symbol"] for symbol in contract["symbols"]),
        "all_outcomes_known": all(card["paper_outcome_status"] in known for card in cards),
        "all_have_operator_action": all(bool(card["operator_action"]) for card in cards),
        "all_have_risk_score": all("risk_score" in card for card in cards),
        "training_not_started": contract["training_status"] == "not_trained_not_calibrated_yet",
        "paper_only_preserved": contract["paper_only"] is True,
        "operator_review_required": contract["operator_review_required"] is True,
        "no_real_exchange_api": contract["real_exchange_api"] is False,
        "no_real_brokerage_api": contract["real_brokerage_api"] is False,
        "no_real_order": contract["real_order"] is False,
        "no_real_execution": contract["real_execution"] is False,
        "no_real_money_impact": contract["real_money_impact"] is False,
        "all_cards_block_real_world_actions": all(card["real_world_actions_allowed"] is False for card in cards),
    }
    return {
        "ok": all(checks.values()),
        "type": "learning_dataset_quality_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": contract["count"],
        "symbols": contract["symbols"],
        "outcome_counts": contract["outcome_counts"],
        "action_counts": contract["action_counts"],
        "risk_counts": contract["risk_counts"],
        "checks": checks,
        "training_status": contract["training_status"],
        "decision": "learning_dataset_quality_gate_paper_only",
        **paper_flags(),
    }

def build_calibration_readiness_gate(file_path: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    quality = build_learning_dataset_quality_gate(file_path, action_by_symbol, outcome_by_symbol)
    contract = build_learning_memory_ui_contract(file_path, action_by_symbol, outcome_by_symbol)
    non_pending = sum(1 for card in contract["cards"] if card["paper_outcome_status"] != "pending_outcome")
    checks = {
        "quality_gate_passed": quality["ok"] is True,
        "has_learning_rows": contract["count"] > 0,
        "training_not_started": contract["training_status"] == "not_trained_not_calibrated_yet",
        "calibration_not_started": contract["training_status"] == "not_trained_not_calibrated_yet",
        "future_phase_is_p9": contract["next_phase"] == "P9 backtest and calibration",
        "paper_only_preserved": contract["paper_only"] is True,
        "operator_review_required": contract["operator_review_required"] is True,
        "no_real_exchange_api": contract["real_exchange_api"] is False,
        "no_real_brokerage_api": contract["real_brokerage_api"] is False,
        "no_real_order": contract["real_order"] is False,
        "no_real_execution": contract["real_execution"] is False,
        "no_real_money_impact": contract["real_money_impact"] is False,
    }
    return {
        "ok": all(checks.values()),
        "type": "calibration_readiness_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": contract["count"],
        "symbols": contract["symbols"],
        "non_pending_outcome_count": non_pending,
        "training_status": contract["training_status"],
        "next_phase": contract["next_phase"],
        "checks": checks,
        "decision": "calibration_readiness_gate_paper_only_no_training_now",
        **paper_flags(),
    }

def build_learning_readiness_summary(file_path: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    quality = build_learning_dataset_quality_gate(file_path, action_by_symbol, outcome_by_symbol)
    calibration = build_calibration_readiness_gate(file_path, action_by_symbol, outcome_by_symbol)
    manifest = build_learning_memory_ui_manifest(file_path, action_by_symbol, outcome_by_symbol)
    return {
        "ok": quality["ok"] is True and calibration["ok"] is True and manifest["validation"]["ok"] is True,
        "type": "learning_readiness_summary",
        "source_file": str(Path(file_path).name),
        "count": manifest["count"],
        "symbols": manifest["symbols"],
        "quality_gate": quality["gate"],
        "calibration_gate": calibration["gate"],
        "training_status": manifest["training_status"],
        "accepted_for": "future_p9_backtest_and_calibration_handoff",
        "real_world_actions_allowed": False,
        "decision": "learning_readiness_summary_paper_only",
        **paper_flags(),
    }

def build_learning_readiness_bundle(file_path: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    quality = build_learning_dataset_quality_gate(file_path, action_by_symbol, outcome_by_symbol)
    calibration = build_calibration_readiness_gate(file_path, action_by_symbol, outcome_by_symbol)
    summary = build_learning_readiness_summary(file_path, action_by_symbol, outcome_by_symbol)
    manifest = build_learning_memory_ui_manifest(file_path, action_by_symbol, outcome_by_symbol)
    return {
        "ok": quality["ok"] is True and calibration["ok"] is True and summary["ok"] is True and manifest["ok"] is True,
        "type": "learning_readiness_bundle",
        "bundle_version": "p8_d12_learning_readiness_bundle_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "quality_gate": quality,
        "calibration_gate": calibration,
        "summary": summary,
        "manifest": manifest,
        "next_phase": "P9 backtest and calibration",
        "training_status": "not_trained_not_calibrated_yet",
        "decision": "learning_readiness_bundle_paper_only_ready_for_p9",
        **paper_flags(),
    }

def write_learning_readiness_bundle(file_path: Any, output_dir: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    bundle = build_learning_readiness_bundle(file_path, action_by_symbol, outcome_by_symbol)
    bundle_file = directory / "learning_readiness_bundle.json"
    quality_file = directory / "learning_dataset_quality_gate.json"
    calibration_file = directory / "calibration_readiness_gate.json"
    summary_file = directory / "learning_readiness_summary.json"
    bundle_file.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    quality_file.write_text(json.dumps(bundle["quality_gate"], indent=2, sort_keys=True), encoding="utf-8")
    calibration_file.write_text(json.dumps(bundle["calibration_gate"], indent=2, sort_keys=True), encoding="utf-8")
    summary_file.write_text(json.dumps(bundle["summary"], indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": True,
        "type": "learning_readiness_bundle_written",
        "output_dir": str(directory),
        "bundle_file": str(bundle_file),
        "quality_gate_file": str(quality_file),
        "calibration_gate_file": str(calibration_file),
        "summary_file": str(summary_file),
        "bundle": bundle,
        **paper_flags(),
    }
