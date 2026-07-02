import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_backtest_baseline import build_paper_backtest_baseline
from btc_finance_platform.paper_backtest_baseline import build_calibration_seed_baseline

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


def build_backtest_metric_summary(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    backtest = build_paper_backtest_baseline(file_path, action_by_symbol, outcome_by_symbol)
    rows = backtest["rows"]

    success_count = sum(1 for row in rows if row["paper_outcome_status"] == "paper_success")
    failure_count = sum(1 for row in rows if row["paper_outcome_status"] == "paper_failure")
    neutral_count = sum(1 for row in rows if row["paper_outcome_status"] == "paper_neutral")
    pending_count = sum(1 for row in rows if row["paper_outcome_status"] == "pending_outcome")
    usable_count = backtest["usable_count"]

    success_rate = success_count / usable_count if usable_count else 0.0
    failure_rate = failure_count / usable_count if usable_count else 0.0

    return {
        "ok": True,
        "type": "backtest_metric_summary",
        "metric_version": "p9_d4_backtest_metric_summary_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "usable_count": usable_count,
        "success_count": success_count,
        "failure_count": failure_count,
        "neutral_count": neutral_count,
        "pending_count": pending_count,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "average_outcome_score": backtest["average_outcome_score"],
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "backtest_metrics_paper_only_no_live_use",
        **paper_flags(),
    }


def build_calibration_evaluation_baseline(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    seed = build_calibration_seed_baseline(file_path, action_by_symbol, outcome_by_symbol)
    metrics = build_backtest_metric_summary(file_path, action_by_symbol, outcome_by_symbol)

    buckets = []
    for risk_level, bucket in seed["by_risk_level"].items():
        usable_count = bucket["usable_count"]
        average_score = bucket["average_outcome_score"]
        needs_more_data = usable_count < 3
        suggested_action = "collect_more_paper_outcomes" if needs_more_data else "eligible_for_future_offline_calibration_review"

        buckets.append({
            "risk_level": risk_level,
            "count": bucket["count"],
            "usable_count": usable_count,
            "average_outcome_score": average_score,
            "needs_more_data": needs_more_data,
            "suggested_action": suggested_action,
            "real_world_actions_allowed": False,
        })

    return {
        "ok": True,
        "type": "calibration_evaluation_baseline",
        "evaluation_version": "p9_d5_calibration_evaluation_baseline_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "bucket_count": len(buckets),
        "buckets": buckets,
        "source_metrics": metrics,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "calibration_evaluation_paper_only_no_parameter_update",
        **paper_flags(),
    }


def build_backtest_readable_report(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    metrics = build_backtest_metric_summary(file_path, action_by_symbol, outcome_by_symbol)
    evaluation = build_calibration_evaluation_baseline(file_path, action_by_symbol, outcome_by_symbol)

    lines = [
        "# Paper Backtest And Calibration Evaluation Report",
        "",
        "Status: paper-only offline evaluation",
        "",
        "Created at UTC: " + datetime.now(timezone.utc).isoformat(),
        "",
        "## Metrics",
        "",
        "- Count: " + str(metrics["count"]),
        "- Usable count: " + str(metrics["usable_count"]),
        "- Success count: " + str(metrics["success_count"]),
        "- Failure count: " + str(metrics["failure_count"]),
        "- Pending count: " + str(metrics["pending_count"]),
        "- Success rate: " + str(metrics["success_rate"]),
        "- Failure rate: " + str(metrics["failure_rate"]),
        "- Average outcome score: " + str(metrics["average_outcome_score"]),
        "- Training status: " + metrics["training_status"],
        "- Calibration status: " + metrics["calibration_status"],
        "",
        "## Calibration Buckets",
        "",
    ]

    for bucket in evaluation["buckets"]:
        lines.extend([
            "### " + bucket["risk_level"],
            "",
            "- Count: " + str(bucket["count"]),
            "- Usable count: " + str(bucket["usable_count"]),
            "- Average outcome score: " + str(bucket["average_outcome_score"]),
            "- Needs more data: " + str(bucket["needs_more_data"]),
            "- Suggested action: " + bucket["suggested_action"],
            "- Real-world actions allowed: false",
            "",
        ])

    lines.extend([
        "## Final Notice",
        "",
        "This report does not train a model.",
        "This report does not update strategy parameters.",
        "This report must not be used for real execution.",
        "",
    ])

    return {
        "ok": True,
        "type": "backtest_readable_report",
        "report_version": "p9_d6_backtest_readable_report_v1",
        "metrics": metrics,
        "evaluation": evaluation,
        "markdown": "\n".join(lines),
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "decision": "backtest_report_paper_only_no_live_use",
        **paper_flags(),
    }


def write_backtest_metrics_report_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    metrics = build_backtest_metric_summary(file_path, action_by_symbol, outcome_by_symbol)
    evaluation = build_calibration_evaluation_baseline(file_path, action_by_symbol, outcome_by_symbol)
    report = build_backtest_readable_report(file_path, action_by_symbol, outcome_by_symbol)

    metrics_file = directory / "backtest_metric_summary.json"
    evaluation_file = directory / "calibration_evaluation_baseline.json"
    report_file = directory / "backtest_readable_report.md"

    metrics_file.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    evaluation_file.write_text(json.dumps(evaluation, indent=2, sort_keys=True), encoding="utf-8")
    report_file.write_text(report["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "backtest_metrics_report_bundle_written",
        "output_dir": str(directory),
        "metrics_file": str(metrics_file),
        "evaluation_file": str(evaluation_file),
        "report_file": str(report_file),
        "metrics": metrics,
        "evaluation": evaluation,
        "report": report,
        **paper_flags(),
    }
