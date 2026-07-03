import json
from pathlib import Path
from typing import Any


def classify_scenario_result(
    paper_return_pct: float,
    max_paper_drawdown_pct: float,
    liquidity_stress: bool = False,
    fail_drawdown_threshold: float = 0.30,
    warn_drawdown_threshold: float = 0.15,
) -> str:
    if not isinstance(paper_return_pct, (int, float)):
        raise ValueError("paper_return_pct must be numeric")

    if not isinstance(max_paper_drawdown_pct, (int, float)):
        raise ValueError("max_paper_drawdown_pct must be numeric")

    if max_paper_drawdown_pct < 0 or max_paper_drawdown_pct > 1:
        raise ValueError("max_paper_drawdown_pct must be between 0 and 1")

    if max_paper_drawdown_pct >= fail_drawdown_threshold:
        return "fail"

    if liquidity_stress and paper_return_pct < 0:
        return "fail"

    if max_paper_drawdown_pct >= warn_drawdown_threshold:
        return "warn"

    if paper_return_pct < 0:
        return "warn"

    return "pass"


def evaluate_scenario(
    scenario: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(scenario, dict):
        raise ValueError("scenario must be a dict")

    scenario_id = scenario.get("scenario_id")
    if not scenario_id:
        raise ValueError("scenario_id is required")

    paper_return_pct = float(scenario.get("paper_return_pct", 0.0))
    max_paper_drawdown_pct = float(scenario.get("max_paper_drawdown_pct", 0.0))
    liquidity_stress = bool(scenario.get("liquidity_stress", False))

    result = classify_scenario_result(
        paper_return_pct=paper_return_pct,
        max_paper_drawdown_pct=max_paper_drawdown_pct,
        liquidity_stress=liquidity_stress,
    )

    return {
        "ok": True,
        "type": "p14_scenario_result",
        "scenario_id": str(scenario_id),
        "scenario_name": str(scenario.get("scenario_name", scenario_id)),
        "regime": str(scenario.get("regime", "unknown")),
        "shock_type": str(scenario.get("shock_type", "unknown")),
        "paper_return_pct": paper_return_pct,
        "max_paper_drawdown_pct": max_paper_drawdown_pct,
        "liquidity_stress": liquidity_stress,
        "scenario_result": result,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def build_scenario_engine_report(
    proposal_id: str,
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    if not proposal_id:
        raise ValueError("proposal_id is required")

    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a non-empty list")

    rows = [evaluate_scenario(scenario) for scenario in scenarios]
    fail_count = sum(1 for row in rows if row["scenario_result"] == "fail")
    warn_count = sum(1 for row in rows if row["scenario_result"] == "warn")

    if fail_count > 0:
        acceptance_status = "BLOCKED_BY_SCENARIO_FAILURE"
    elif warn_count > 0:
        acceptance_status = "READY_FOR_HEIGHTENED_OPERATOR_REVIEW"
    else:
        acceptance_status = "READY_FOR_OPERATOR_REVIEW"

    return {
        "ok": True,
        "type": "p14_scenario_engine_report",
        "current_stage": "P14-D28-D30",
        "proposal_id": proposal_id,
        "report_status": acceptance_status,
        "purpose": "stress test paper proposals before operator review",
        "scenario_count": len(rows),
        "fail_count": fail_count,
        "warn_count": warn_count,
        "rows": rows,
        "scenario_policy": {
            "scenario_test_required": True,
            "auto_accept_allowed": False,
            "auto_reject_allowed": False,
            "operator_review_required": True,
        },
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
    }


def write_scenario_engine_report(
    proposal_id: str,
    scenarios: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_scenario_engine_report(proposal_id, scenarios)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_scenario_engine_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_accept_allowed": False,
        "real_world_actions_allowed": False,
    }
