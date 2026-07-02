from typing import Any


def render_batch_report(batch_result: dict[str, Any], summary: dict[str, Any]) -> str:
    if batch_result.get("paper_only") is not True:
        raise AssertionError("batch report requires paper-only batch result")

    if summary.get("paper_only") is not True:
        raise AssertionError("batch report requires paper-only summary")

    lines = [
        "# BTC Finance Platform Batch Paper Report",
        "",
        f"Batch Count: {summary['count']}",
        f"Symbols: {', '.join(summary['symbols'])}",
        f"Risk Counts: {summary['risk_counts']}",
        "",
        "Status: PAPER_ONLY_BATCH_REVIEW_REQUIRED",
        "Action: NO_LIVE_ACTION",
        "",
        "Items:",
    ]

    for result in batch_result["results"]:
        lines.append(
            f"- {result['analysis']['symbol']}: "
            f"{result['analysis']['scenario']} / "
            f"{result['risk']['risk_level']} / "
            f"{result['strategy']['stance']}"
        )

    lines.extend([
        "",
        "Safety:",
        "- no real exchange API",
        "- no real order",
        "- no real execution",
        "- no real money impact",
        "- operator review required",
    ])

    return "\n".join(lines)
