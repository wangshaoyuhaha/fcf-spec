import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_learning_audit import build_feedback_to_calibration_handoff

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


def build_paper_backtest_input_contract(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    handoff = build_feedback_to_calibration_handoff(
        file_path,
        action_by_symbol,
        outcome_by_symbol,
    )

    rows = []
    for row in handoff["rows"]:
        rows.append({
            "symbol": row["symbol"],
            "asset_class": row["asset_class"],
            "market": row["market"],
            "paper_signal": row["paper_signal"],
            "risk_level": row["risk_level"],
            "risk_score": row["risk_score"],
            "operator_action": row["operator_action"],
            "paper_outcome_status": row["paper_outcome_status"],
            "backtest_use": "offline_paper_backtest_only",
            "real_world_actions_allowed": False,
        })

    return {
        "ok": True,
        "type": "paper_backtest_input_contract",
        "contract_version": "p9_d1_paper_backtest_input_contract_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "symbols": [row["symbol"] for row in rows],
        "rows": rows,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "paper_backtest_input_contract_only",
        **paper_flags(),
    }


def score_paper_outcome(row: dict[str, Any]) -> dict[str, Any]:
    status = row["paper_outcome_status"]

    if status == "paper_success":
        score = 1.0
        usable = True
    elif status == "paper_failure":
        score = -1.0
        usable = True
    elif status == "paper_neutral":
        score = 0.0
        usable = True
    else:
        score = 0.0
        usable = False

    return {
        "ok": True,
        "type": "paper_outcome_score",
        "symbol": row["symbol"],
        "paper_outcome_status": status,
        "outcome_score": score,
        "usable_for_calibration": usable,
        "real_world_actions_allowed": False,
        "decision": "paper_outcome_scored_for_offline_backtest",
        **paper_flags(),
    }


def build_paper_backtest_baseline(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    contract = build_paper_backtest_input_contract(
        file_path,
        action_by_symbol,
        outcome_by_symbol,
    )

    scored_rows = []
    usable_scores = []

    for row in contract["rows"]:
        score = score_paper_outcome(row)
        scored = dict(row)
        scored["outcome_score"] = score["outcome_score"]
        scored["usable_for_calibration"] = score["usable_for_calibration"]
        scored_rows.append(scored)
        if score["usable_for_calibration"]:
            usable_scores.append(score["outcome_score"])

    average_score = sum(usable_scores) / len(usable_scores) if usable_scores else 0.0

    return {
        "ok": True,
        "type": "paper_backtest_baseline",
        "baseline_version": "p9_d2_paper_backtest_baseline_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(scored_rows),
        "usable_count": len(usable_scores),
        "average_outcome_score": average_score,
        "rows": scored_rows,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "paper_backtest_baseline_no_model_training",
        **paper_flags(),
    }


def build_calibration_seed_baseline(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    backtest = build_paper_backtest_baseline(
        file_path,
        action_by_symbol,
        outcome_by_symbol,
    )

    by_risk_level: dict[str, dict[str, Any]] = {}

    for row in backtest["rows"]:
        risk_level = row["risk_level"]
        bucket = by_risk_level.setdefault(
            risk_level,
            {
                "risk_level": risk_level,
                "count": 0,
                "usable_count": 0,
                "score_sum": 0.0,
                "average_outcome_score": 0.0,
            },
        )

        bucket["count"] += 1
        if row["usable_for_calibration"]:
            bucket["usable_count"] += 1
            bucket["score_sum"] += row["outcome_score"]

    for bucket in by_risk_level.values():
        if bucket["usable_count"]:
            bucket["average_outcome_score"] = bucket["score_sum"] / bucket["usable_count"]

    return {
        "ok": True,
        "type": "calibration_seed_baseline",
        "seed_version": "p9_d3_calibration_seed_baseline_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "by_risk_level": by_risk_level,
        "source_backtest": backtest,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "calibration_seed_ready_for_future_offline_calibration",
        **paper_flags(),
    }


def write_paper_backtest_baseline_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    contract = build_paper_backtest_input_contract(file_path, action_by_symbol, outcome_by_symbol)
    backtest = build_paper_backtest_baseline(file_path, action_by_symbol, outcome_by_symbol)
    seed = build_calibration_seed_baseline(file_path, action_by_symbol, outcome_by_symbol)

    contract_file = directory / "paper_backtest_input_contract.json"
    backtest_file = directory / "paper_backtest_baseline.json"
    seed_file = directory / "calibration_seed_baseline.json"

    contract_file.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    backtest_file.write_text(json.dumps(backtest, indent=2, sort_keys=True), encoding="utf-8")
    seed_file.write_text(json.dumps(seed, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_backtest_baseline_bundle_written",
        "output_dir": str(directory),
        "contract_file": str(contract_file),
        "backtest_file": str(backtest_file),
        "seed_file": str(seed_file),
        "contract": contract,
        "backtest": backtest,
        "seed": seed,
        **paper_flags(),
    }
