from typing import Any

from btc_finance_platform.analysis_flow import run_paper_analysis_flow
from btc_finance_platform.batch_input import validate_paper_input_batch


def run_paper_analysis_batch(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    batch = validate_paper_input_batch(payloads)

    results = [
        run_paper_analysis_flow({
            "symbol": item["symbol"],
            "price": item["price"],
            "reference_price": item["reference_price"],
        })
        for item in batch["items"]
    ]

    return {
        "ok": True,
        "type": "paper_analysis_batch_result",
        "count": len(results),
        "results": results,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }


def summarize_batch_results(batch_result: dict[str, Any]) -> dict[str, Any]:
    if batch_result.get("paper_only") is not True:
        raise AssertionError("batch summary requires paper-only result")

    results = batch_result["results"]
    risk_counts: dict[str, int] = {}

    for result in results:
        risk_level = result["risk"]["risk_level"]
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1

    return {
        "ok": True,
        "type": "paper_batch_summary",
        "count": len(results),
        "risk_counts": risk_counts,
        "symbols": [result["analysis"]["symbol"] for result in results],
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
