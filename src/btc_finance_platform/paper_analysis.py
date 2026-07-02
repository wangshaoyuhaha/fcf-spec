from typing import Any


def analyze_paper_market(validated_input: dict[str, Any]) -> dict[str, Any]:
    if validated_input.get("paper_only") is not True:
        raise AssertionError("analysis requires paper-only input")

    if validated_input.get("real_exchange_api") is not False:
        raise AssertionError("analysis must not use real exchange API")

    price = float(validated_input["price"])
    reference_price = float(validated_input["reference_price"])
    change_pct = ((price - reference_price) / reference_price) * 100.0

    if change_pct >= 2.0:
        scenario = "PAPER_UPSIDE_MOVE"
    elif change_pct <= -2.0:
        scenario = "PAPER_DOWNSIDE_MOVE"
    else:
        scenario = "PAPER_RANGE_MOVE"

    return {
        "ok": True,
        "type": "paper_market_analysis",
        "symbol": validated_input["symbol"],
        "price": price,
        "reference_price": reference_price,
        "change_pct": round(change_pct, 6),
        "scenario": scenario,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def assert_paper_market_analysis(analysis: dict[str, Any]) -> bool:
    required = {
        "ok": True,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }

    for key, expected in required.items():
        if analysis.get(key) is not expected:
            raise AssertionError(f"invalid paper market analysis flag: {key}")

    return True
