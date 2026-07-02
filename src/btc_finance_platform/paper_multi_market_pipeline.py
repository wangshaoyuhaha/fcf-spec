import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_analysis_logic import analyze_paper_batch
from btc_finance_platform.paper_multi_market import build_multi_market_batch_contract
from btc_finance_platform.paper_multi_market import extract_analysis_compatible_items
from btc_finance_platform.paper_risk_governance import build_policy_gate_for_governor_decision
from btc_finance_platform.paper_risk_governance import build_risk_governor_decision


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


def load_multi_market_json_items(file_path: Any) -> list[dict[str, Any]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("multi-market fixture not found: " + str(path))
    if not path.is_file():
        raise ValueError("multi-market path must be a file")

    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(raw, dict) and "items" in raw:
        raw = raw["items"]

    if not isinstance(raw, list):
        raise ValueError("multi-market json must be a list or dict with items")
    if not raw:
        raise ValueError("multi-market json must not be empty")

    return raw


def build_multi_market_contract_from_json(file_path: Any) -> dict[str, Any]:
    items = load_multi_market_json_items(file_path)
    contract = build_multi_market_batch_contract(items)

    return {
        "ok": True,
        "type": "multi_market_contract_from_json",
        "source_file": Path(file_path).name,
        "contract": contract,
        "count": contract["count"],
        "symbols": contract["symbols"],
        "asset_class_counts": contract["asset_class_counts"],
        "market_counts": contract["market_counts"],
        "decision": "json_to_multi_market_contract_paper_only",
        **paper_flags(),
    }


def run_multi_market_paper_analysis_from_contract(batch_contract: dict[str, Any]) -> dict[str, Any]:
    analysis_items = extract_analysis_compatible_items(batch_contract)
    analysis = analyze_paper_batch(analysis_items)

    return {
        "ok": analysis["ok"] is True,
        "type": "multi_market_paper_analysis_result",
        "count": analysis["count"],
        "symbols": analysis["symbols"],
        "asset_class_counts": batch_contract["asset_class_counts"],
        "market_counts": batch_contract["market_counts"],
        "analysis_items": analysis_items,
        "analysis": analysis,
        "source_contract": batch_contract,
        "decision": "multi_market_analysis_paper_only_no_real_trade",
        **paper_flags(),
    }


def run_multi_market_paper_analysis_from_json(file_path: Any) -> dict[str, Any]:
    loaded = build_multi_market_contract_from_json(file_path)
    result = run_multi_market_paper_analysis_from_contract(loaded["contract"])

    return {
        "ok": result["ok"] is True,
        "type": "multi_market_json_to_paper_analysis",
        "source_file": loaded["source_file"],
        "loaded_contract": loaded,
        "analysis_result": result,
        "count": result["count"],
        "symbols": result["symbols"],
        "asset_class_counts": result["asset_class_counts"],
        "market_counts": result["market_counts"],
        "decision": "multi_market_json_pipeline_paper_only",
        **paper_flags(),
    }


def build_multi_market_governance_summary_from_analysis(analysis_result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(analysis_result, dict):
        raise ValueError("analysis_result must be a dict")
    if analysis_result.get("type") != "multi_market_paper_analysis_result":
        raise ValueError("analysis_result type is invalid")
    if analysis_result.get("ok") is not True:
        raise ValueError("analysis_result must be ok")

    analysis_items = analysis_result["analysis"]["items"]
    governor_decisions = [build_risk_governor_decision(item) for item in analysis_items]
    policy_gates = [build_policy_gate_for_governor_decision(item) for item in governor_decisions]

    gate_counts: dict[str, int] = {}
    regime_counts: dict[str, int] = {}

    for decision in governor_decisions:
        gate = decision["gate"]
        regime = decision["regime"]["regime"]
        gate_counts[gate] = gate_counts.get(gate, 0) + 1
        regime_counts[regime] = regime_counts.get(regime, 0) + 1

    return {
        "ok": all(item["ok"] for item in policy_gates),
        "type": "multi_market_governance_summary",
        "count": len(governor_decisions),
        "symbols": [item["symbol"] for item in governor_decisions],
        "asset_class_counts": analysis_result["asset_class_counts"],
        "market_counts": analysis_result["market_counts"],
        "gate_counts": gate_counts,
        "regime_counts": regime_counts,
        "governor_decisions": governor_decisions,
        "policy_gates": policy_gates,
        "decision": "multi_market_governance_summary_paper_only",
        **paper_flags(),
    }


def build_multi_market_pipeline_report_from_json(file_path: Any) -> dict[str, Any]:
    pipeline = run_multi_market_paper_analysis_from_json(file_path)
    governance = build_multi_market_governance_summary_from_analysis(pipeline["analysis_result"])

    return {
        "ok": pipeline["ok"] is True and governance["ok"] is True,
        "type": "multi_market_pipeline_report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": pipeline["source_file"],
        "count": pipeline["count"],
        "symbols": pipeline["symbols"],
        "asset_class_counts": pipeline["asset_class_counts"],
        "market_counts": pipeline["market_counts"],
        "pipeline": pipeline,
        "governance": governance,
        "decision": "multi_market_report_paper_only_no_real_trade",
        **paper_flags(),
    }


def write_multi_market_pipeline_report(file_path: Any, output_path: Any) -> dict[str, Any]:
    report = build_multi_market_pipeline_report_from_json(file_path)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "multi_market_pipeline_report_written",
        "output_file": str(path),
        "report": report,
        **paper_flags(),
    }
