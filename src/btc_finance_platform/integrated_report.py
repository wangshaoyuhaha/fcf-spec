from typing import Any


def render_integrated_report(
    analysis: dict[str, Any],
    risk: dict[str, Any],
    strategy: dict[str, Any],
) -> str:
    if analysis.get("paper_only") is not True:
        raise AssertionError("integrated report requires paper-only analysis")

    if risk.get("paper_only") is not True:
        raise AssertionError("integrated report requires paper-only risk")

    if strategy.get("paper_only") is not True:
        raise AssertionError("integrated report requires paper-only strategy")

    return "\n".join([
        "# BTC Finance Platform Integrated Paper Report",
        "",
        f"Symbol: {analysis['symbol']}",
        f"Scenario: {analysis['scenario']}",
        f"Change Percent: {analysis['change_pct']}%",
        f"Risk Level: {risk['risk_level']}",
        f"Paper Strategy Stance: {strategy['stance']}",
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
    ])
