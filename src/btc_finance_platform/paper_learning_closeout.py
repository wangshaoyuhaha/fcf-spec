import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_learning_readiness import build_learning_readiness_bundle

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

P8_COMPLETED_SCOPE = [
    "P8-D1 learning memory schema",
    "P8-D2 operator feedback dataset",
    "P8-D3 paper outcome tracking contract",
    "P8-D4 learning event audit trail",
    "P8-D5 feedback-to-calibration handoff",
    "P8-D6 learning memory readable report",
    "P8-D7 learning memory UI contract",
    "P8-D8 learning dataset index",
    "P8-D9 learning memory UI bundle",
    "P8-D10 learning dataset quality gate",
    "P8-D11 calibration readiness gate",
    "P8-D12 learning readiness bundle",
    "P8-D13 P8 learning closeout summary",
    "P8-D14 P8 paper-only learning safety acceptance",
    "P8-D15 P9 backtest and calibration transition anchor",
]

def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)

def get_p8_learning_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p8_learning_capabilities",
        "phase": "P8",
        "status": "completed",
        "completed_scope": list(P8_COMPLETED_SCOPE),
        "capabilities": [
            "learning memory schema",
            "operator feedback dataset",
            "paper outcome tracking",
            "learning event audit trail",
            "feedback-to-calibration handoff",
            "learning memory readable report",
            "learning memory UI contract",
            "learning dataset index",
            "learning readiness gate",
            "calibration readiness gate",
            "P9 backtest and calibration handoff readiness",
        ],
        "training_status": "not_trained_not_calibrated_yet",
        "current_role": "paper-only learning memory and feedback foundation",
        "decision": "P8_learning_layer_completed_paper_only",
        **paper_flags(),
    }

def get_p8_safety_acceptance() -> dict[str, Any]:
    checks = {
        "paper_only": True,
        "no_real_exchange_api": True,
        "no_real_brokerage_api": True,
        "no_real_api_key_required": True,
        "no_wallet_private_key_required": True,
        "no_real_order": True,
        "no_real_execution": True,
        "no_real_balance": True,
        "no_real_position": True,
        "no_real_money_impact": True,
        "operator_review_required": True,
        "no_self_trading": True,
        "no_automatic_live_trading": True,
        "no_bypassing_operator_review": True,
        "no_model_training_yet": True,
        "no_strategy_calibration_yet": True,
    }
    return {
        "ok": all(checks.values()),
        "type": "p8_safety_acceptance",
        "phase": "P8",
        "checks": checks,
        "decision": "P8 accepted for paper-only learning closeout",
        **paper_flags(),
    }

def get_p8_to_p9_transition_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p8_to_p9_transition_anchor",
        "from_phase": "P8 learning memory and feedback dataset",
        "to_phase": "P9 backtest and calibration",
        "p9_candidate_scope": [
            "paper backtest input contract",
            "paper outcome scoring baseline",
            "risk score calibration baseline",
            "regime performance evaluation",
            "calibration report",
            "backtest UI contract",
            "model registry handoff anchor",
        ],
        "allowed": [
            "offline backtest",
            "paper-only calibration",
            "versioned calibration artifacts",
            "operator-reviewed model update proposal",
        ],
        "forbidden": [
            "automatic live trading",
            "real exchange API",
            "real brokerage API",
            "real orders",
            "real execution",
            "real money impact",
            "bypassing operator review",
        ],
        "decision": "ready_for_P9_backtest_and_calibration_paper_only",
        **paper_flags(),
    }

def build_p8_closeout_package(file_path: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    readiness = build_learning_readiness_bundle(file_path, action_by_symbol, outcome_by_symbol)
    capabilities = get_p8_learning_capabilities()
    safety = get_p8_safety_acceptance()
    transition = get_p8_to_p9_transition_anchor()
    return {
        "ok": readiness["ok"] is True and capabilities["ok"] is True and safety["ok"] is True and transition["ok"] is True,
        "type": "p8_closeout_package",
        "phase": "P8",
        "status": "completed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "readiness": readiness,
        "capabilities": capabilities,
        "safety_acceptance": safety,
        "transition_anchor": transition,
        "next_phase": "P9 backtest and calibration",
        "training_status": "not_trained_not_calibrated_yet",
        "decision": "P8_closed_paper_only_ready_for_P9",
        **paper_flags(),
    }

def write_p8_closeout_bundle(file_path: Any, output_dir: Any, action_by_symbol: dict[str, str] | None = None, outcome_by_symbol: dict[str, str] | None = None) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    package = build_p8_closeout_package(file_path, action_by_symbol, outcome_by_symbol)
    package_file = directory / "p8_closeout_package.json"
    safety_file = directory / "p8_safety_acceptance.json"
    transition_file = directory / "p8_to_p9_transition_anchor.json"
    package_file.write_text(json.dumps(package, indent=2, sort_keys=True), encoding="utf-8")
    safety_file.write_text(json.dumps(package["safety_acceptance"], indent=2, sort_keys=True), encoding="utf-8")
    transition_file.write_text(json.dumps(package["transition_anchor"], indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": True,
        "type": "p8_closeout_bundle_written",
        "output_dir": str(directory),
        "package_file": str(package_file),
        "safety_file": str(safety_file),
        "transition_file": str(transition_file),
        "package": package,
        **paper_flags(),
    }
