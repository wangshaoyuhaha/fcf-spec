import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_analysis_pipeline import build_paper_analysis_pipeline_report


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
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


def _require_pipeline_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("pipeline_report must be a dict")
    if report.get("ok") is not True:
        raise ValueError("pipeline_report must be ok")
    if report.get("type") != "paper_analysis_pipeline_report":
        raise ValueError("pipeline_report type is invalid")
    return report


def _priority_from_analysis_item(item: dict[str, Any]) -> str:
    risk_level = item["risk"]["level"]
    magnitude = item["deviation"]["magnitude"]

    if risk_level == "high":
        return "high"
    if risk_level == "medium" or magnitude in {"medium", "large"}:
        return "medium"
    return "low"


def build_symbol_review_item(analysis_item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(analysis_item, dict):
        raise ValueError("analysis_item must be a dict")

    symbol = analysis_item["symbol"]
    signal = analysis_item["signal"]
    risk = analysis_item["risk"]
    deviation = analysis_item["deviation"]
    momentum = analysis_item["momentum"]

    rationale = [
        "symbol=" + str(symbol),
        "signal=" + str(signal),
        "risk_level=" + str(risk["level"]),
        "risk_score=" + str(risk["score"]),
        "deviation_direction=" + str(deviation["direction"]),
        "deviation_magnitude=" + str(deviation["magnitude"]),
        "momentum_direction=" + str(momentum["direction"]),
    ]

    return {
        "ok": True,
        "type": "symbol_operator_review_item",
        "symbol": symbol,
        "priority": _priority_from_analysis_item(analysis_item),
        "signal": signal,
        "risk_level": risk["level"],
        "risk_score": risk["score"],
        "deviation_direction": deviation["direction"],
        "deviation_magnitude": deviation["magnitude"],
        "momentum_direction": momentum["direction"],
        "rationale": rationale,
        "operator_action": "review_paper_signal_only",
        "decision": "no_real_trade_review_only",
        **paper_flags(),
    }


def build_operator_review_checklist(pipeline_report: dict[str, Any]) -> dict[str, Any]:
    report = _require_pipeline_report(pipeline_report)

    checks = {
        "pipeline_report_ok": report["ok"] is True,
        "has_items": report["count"] > 0,
        "paper_only_preserved": report["paper_only"] is True,
        "no_real_exchange_api": report["real_exchange_api"] is False,
        "no_real_api_key_required": report["real_api_key_required"] is False,
        "no_wallet_private_key_required": report["wallet_private_key_required"] is False,
        "no_real_order": report["real_order"] is False,
        "no_real_execution": report["real_execution"] is False,
        "no_real_balance": report["real_balance"] is False,
        "no_real_position": report["real_position"] is False,
        "no_real_money_impact": report["real_money_impact"] is False,
        "operator_review_required": report["operator_review_required"] is True,
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_review_checklist",
        "checks": checks,
        "required_action": "human_operator_review_before_any_future_step",
        "allowed_action": "paper_review_only",
        "blocked_actions": [
            "real_exchange_api",
            "real_api_key",
            "wallet_private_key",
            "real_order",
            "real_execution",
            "real_balance",
            "real_position",
            "real_money_impact",
            "automatic_live_trading",
        ],
        **paper_flags(),
    }


def build_paper_analysis_review_packet(file_paths: list[Any]) -> dict[str, Any]:
    pipeline_report = build_paper_analysis_pipeline_report(file_paths)
    report = _require_pipeline_report(pipeline_report)
    analysis_items = report["pipeline"]["pipeline_result"]["analysis"]["items"]
    review_items = [build_symbol_review_item(item) for item in analysis_items]
    checklist = build_operator_review_checklist(report)

    priority_counts: dict[str, int] = {}
    for item in review_items:
        priority = item["priority"]
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    return {
        "ok": checklist["ok"] is True and all(item["ok"] for item in review_items),
        "type": "paper_analysis_review_packet",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(review_items),
        "symbols": report["symbols"],
        "priority_counts": priority_counts,
        "review_items": review_items,
        "checklist": checklist,
        "pipeline_report": report,
        "decision": "operator_review_packet_only_no_real_trade",
        **paper_flags(),
    }


def write_paper_analysis_review_packet(file_paths: list[Any], output_path: Any) -> dict[str, Any]:
    packet = build_paper_analysis_review_packet(file_paths)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_analysis_review_packet_written",
        "output_file": str(path),
        "packet": packet,
        **paper_flags(),
    }
