from typing import Any


def render_paper_report(analysis: dict[str, Any]) -> str:
    if analysis.get("paper_only") is not True:
        raise AssertionError("report requires paper-only analysis")

    if analysis.get("real_order") is not False:
        raise AssertionError("report must not include real order")

    lines = [
        "# BTC Finance Platform Paper Report",
        "",
        f"Symbol: {analysis['symbol']}",
        f"Price: {analysis['price']}",
        f"Reference Price: {analysis['reference_price']}",
        f"Paper Change Percent: {analysis['change_pct']}%",
        f"Scenario: {analysis['scenario']}",
        "",
        "Status: PAPER_ONLY_REVIEW_REQUIRED",
        "Action: NO_LIVE_ACTION",
        "",
        "Safety:",
        "- no real exchange API",
        "- no real order",
        "- no real execution",
        "- no real money impact",
        "- operator review required",
    ]

    return "\n".join(lines)
