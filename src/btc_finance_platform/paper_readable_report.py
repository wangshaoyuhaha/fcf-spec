import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_review_packet import build_paper_analysis_review_packet


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


def _require_review_packet(packet: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("review_packet must be a dict")
    if packet.get("ok") is not True:
        raise ValueError("review_packet must be ok")
    if packet.get("type") != "paper_analysis_review_packet":
        raise ValueError("review_packet type is invalid")
    return packet


def build_paper_report_summary(packet: dict[str, Any]) -> dict[str, Any]:
    packet = _require_review_packet(packet)
    review_items = packet["review_items"]

    risk_counts: dict[str, int] = {}
    signal_counts: dict[str, int] = {}

    for item in review_items:
        risk = item["risk_level"]
        signal = item["signal"]
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
        signal_counts[signal] = signal_counts.get(signal, 0) + 1

    return {
        "ok": True,
        "type": "paper_report_summary",
        "count": packet["count"],
        "symbols": packet["symbols"],
        "priority_counts": packet["priority_counts"],
        "risk_counts": risk_counts,
        "signal_counts": signal_counts,
        "requires_operator_review": True,
        "decision": "summary_only_no_real_trade",
        **paper_flags(),
    }


def build_symbol_markdown_section(review_item: dict[str, Any]) -> str:
    if not isinstance(review_item, dict):
        raise ValueError("review_item must be a dict")

    lines = [
        "### " + str(review_item["symbol"]),
        "",
        "- Priority: " + str(review_item["priority"]),
        "- Signal: " + str(review_item["signal"]),
        "- Risk level: " + str(review_item["risk_level"]),
        "- Risk score: " + str(review_item["risk_score"]),
        "- Deviation direction: " + str(review_item["deviation_direction"]),
        "- Deviation magnitude: " + str(review_item["deviation_magnitude"]),
        "- Momentum direction: " + str(review_item["momentum_direction"]),
        "- Operator action: " + str(review_item["operator_action"]),
        "- Decision: " + str(review_item["decision"]),
        "",
        "Rationale:",
    ]

    for reason in review_item["rationale"]:
        lines.append("- " + str(reason))

    lines.append("")
    return "\n".join(lines)


def build_paper_analysis_markdown_report(file_paths: list[Any]) -> dict[str, Any]:
    packet = build_paper_analysis_review_packet(file_paths)
    packet = _require_review_packet(packet)
    summary = build_paper_report_summary(packet)

    lines = [
        "# Paper Analysis Report",
        "",
        "Status: paper-only report",
        "",
        "Created at UTC: " + datetime.now(timezone.utc).isoformat(),
        "",
        "## Safety Boundary",
        "",
        "- Paper-only: true",
        "- Real exchange API: false",
        "- Real API key required: false",
        "- Wallet private key required: false",
        "- Real order: false",
        "- Real execution: false",
        "- Real balance: false",
        "- Real position: false",
        "- Real money impact: false",
        "- Operator review required: true",
        "",
        "## Summary",
        "",
        "- Count: " + str(summary["count"]),
        "- Symbols: " + ", ".join(summary["symbols"]),
        "- Priority counts: " + json.dumps(summary["priority_counts"], sort_keys=True),
        "- Risk counts: " + json.dumps(summary["risk_counts"], sort_keys=True),
        "- Signal counts: " + json.dumps(summary["signal_counts"], sort_keys=True),
        "",
        "## Review Items",
        "",
    ]

    for item in packet["review_items"]:
        lines.append(build_symbol_markdown_section(item))

    lines.extend([
        "## Final Notice",
        "",
        "This report is not financial advice.",
        "This report is not a real trading signal.",
        "This report must not be used for real execution.",
        "Human operator review remains required.",
        "",
    ])

    markdown = "\n".join(lines)

    return {
        "ok": True,
        "type": "paper_analysis_markdown_report",
        "summary": summary,
        "markdown": markdown,
        "packet": packet,
        "decision": "markdown_report_only_no_real_trade",
        **paper_flags(),
    }


def write_paper_analysis_markdown_report(
    file_paths: list[Any],
    output_path: Any,
) -> dict[str, Any]:
    report = build_paper_analysis_markdown_report(file_paths)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_analysis_markdown_report_written",
        "output_file": str(path),
        "report": report,
        **paper_flags(),
    }


def write_paper_analysis_report_bundle(
    file_paths: list[Any],
    output_dir: Any,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    report = build_paper_analysis_markdown_report(file_paths)
    markdown_path = directory / "paper_analysis_report.md"
    json_path = directory / "paper_analysis_report.json"

    markdown_path.write_text(report["markdown"], encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_analysis_report_bundle_written",
        "output_dir": str(directory),
        "markdown_file": str(markdown_path),
        "json_file": str(json_path),
        "report": report,
        **paper_flags(),
    }
