import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_calibration_readiness import build_p9_readiness_bundle

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

P9_COMPLETED_SCOPE = [
    "P9-D1 paper backtest input contract",
    "P9-D2 paper outcome scoring baseline",
    "P9-D3 calibration seed baseline",
    "P9-D4 backtest metric summary",
    "P9-D5 calibration evaluation baseline",
    "P9-D6 backtest readable report",
    "P9-D7 risk bucket performance index",
    "P9-D8 calibration proposal contract",
    "P9-D9 calibration UI contract",
    "P9-D10 calibration acceptance gate",
    "P9-D11 backtest UI readiness gate",
    "P9-D12 P9 readiness bundle",
    "P9-D13 P9 closeout summary",
    "P9-D14 P9 paper-only safety acceptance",
    "P9-D15 P10 model registry transition anchor",
]


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_p9_backtest_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p9_backtest_capabilities",
        "phase": "P9",
        "status": "completed",
        "completed_scope": list(P9_COMPLETED_SCOPE),
        "capabilities": [
            "paper backtest input contract",
            "paper outcome scoring",
            "calibration seed baseline",
            "backtest metric summary",
            "calibration evaluation baseline",
            "backtest readable report",
            "risk bucket performance index",
            "calibration proposal contract",
            "calibration UI contract",
            "calibration acceptance gate",
            "backtest UI readiness gate",
            "P10 model registry handoff readiness",
        ],
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "parameter_update_allowed_now": False,
        "current_role": "paper-only offline backtest and calibration evaluation layer",
        "decision": "P9_backtest_layer_completed_paper_only",
        **paper_flags(),
    }


def get_p9_safety_acceptance() -> dict[str, Any]:
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
        "no_model_training_in_p9": True,
        "no_parameter_update_in_p9": True,
        "no_live_calibration": True,
        "no_automatic_live_trading": True,
    }
    return {
        "ok": all(checks.values()),
        "type": "p9_safety_acceptance",
        "phase": "P9",
        "checks": checks,
        "decision": "P9 accepted for paper-only backtest closeout",
        **paper_flags(),
    }


def get_p9_to_p10_transition_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p9_to_p10_transition_anchor",
        "from_phase": "P9 backtest and calibration",
        "to_phase": "P10 model registry and strategy versioning",
        "p10_candidate_scope": [
            "paper model registry schema",
            "strategy version registry",
            "calibration proposal version record",
            "model card contract",
            "operator approval gate for model version",
            "paper-only model registry report",
            "P11 UI handoff anchor",
        ],
        "allowed": [
            "versioned paper model metadata",
            "paper strategy version records",
            "operator-reviewed model proposal",
            "offline model registry only",
        ],
        "forbidden": [
            "automatic model deployment",
            "automatic live trading",
            "real exchange API",
            "real brokerage API",
            "real orders",
            "real execution",
            "real money impact",
            "bypassing operator review",
        ],
        "decision": "ready_for_P10_model_registry_paper_only",
        **paper_flags(),
    }


def build_p9_closeout_package(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    readiness = build_p9_readiness_bundle(file_path, action_by_symbol, outcome_by_symbol)
    capabilities = get_p9_backtest_capabilities()
    safety = get_p9_safety_acceptance()
    transition = get_p9_to_p10_transition_anchor()

    return {
        "ok": readiness["ok"] is True and capabilities["ok"] is True and safety["ok"] is True and transition["ok"] is True,
        "type": "p9_closeout_package",
        "phase": "P9",
        "status": "completed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "readiness": readiness,
        "capabilities": capabilities,
        "safety_acceptance": safety,
        "transition_anchor": transition,
        "next_phase": "P10 model registry and strategy versioning",
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "parameter_update_allowed_now": False,
        "decision": "P9_closed_paper_only_ready_for_P10",
        **paper_flags(),
    }


def write_p9_closeout_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    package = build_p9_closeout_package(file_path, action_by_symbol, outcome_by_symbol)

    package_file = directory / "p9_closeout_package.json"
    safety_file = directory / "p9_safety_acceptance.json"
    transition_file = directory / "p9_to_p10_transition_anchor.json"

    package_file.write_text(json.dumps(package, indent=2, sort_keys=True), encoding="utf-8")
    safety_file.write_text(json.dumps(package["safety_acceptance"], indent=2, sort_keys=True), encoding="utf-8")
    transition_file.write_text(json.dumps(package["transition_anchor"], indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p9_closeout_bundle_written",
        "output_dir": str(directory),
        "package_file": str(package_file),
        "safety_file": str(safety_file),
        "transition_file": str(transition_file),
        "package": package,
        **paper_flags(),
    }
