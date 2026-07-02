import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_pipeline_report_from_json
from btc_finance_platform.paper_operator_workflow import build_operator_workflow_state


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


VALID_OUTCOME_STATUS = {
    "pending_outcome",
    "paper_success",
    "paper_failure",
    "paper_neutral",
    "inconclusive",
}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def normalize_paper_outcome_status(status: str) -> str:
    value = str(status).strip().lower()
    if value not in VALID_OUTCOME_STATUS:
        raise ValueError("paper outcome status is invalid")
    return value


def build_learning_memory_schema() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "learning_memory_schema",
        "schema_version": "p8_d1_learning_memory_schema_v1",
        "required_fields": [
            "memory_id",
            "symbol",
            "asset_class",
            "market",
            "paper_signal",
            "risk_level",
            "risk_score",
            "operator_action",
            "paper_outcome_status",
            "recorded_at_utc",
        ],
        "allowed_outcome_status": sorted(VALID_OUTCOME_STATUS),
        "purpose": "paper_only_learning_memory_and_feedback_dataset",
        "decision": "schema_only_no_training_no_real_trade",
        **paper_flags(),
    }


def _index_by_symbol(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for item in items:
        result[item["symbol"]] = item
    return result


def build_paper_learning_memory_record(
    analysis_item: dict[str, Any],
    workflow_action: dict[str, Any],
    paper_outcome_status: str = "pending_outcome",
) -> dict[str, Any]:
    if not isinstance(analysis_item, dict):
        raise ValueError("analysis_item must be a dict")
    if not isinstance(workflow_action, dict):
        raise ValueError("workflow_action must be a dict")

    symbol = analysis_item["symbol"]
    if workflow_action["symbol"] != symbol:
        raise ValueError("analysis_item and workflow_action symbol mismatch")

    outcome = normalize_paper_outcome_status(paper_outcome_status)
    risk = analysis_item["risk"]

    return {
        "ok": True,
        "type": "paper_learning_memory_record",
        "memory_id": "memory-" + symbol.lower(),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "asset_class": workflow_action["asset_class"],
        "market": workflow_action["market"],
        "paper_signal": analysis_item["signal"],
        "risk_level": risk["level"],
        "risk_score": risk["score"],
        "operator_action": workflow_action["operator_action"],
        "workflow_gate": workflow_action["workflow_gate"],
        "allowed_next_step": workflow_action["allowed_next_step"],
        "paper_outcome_status": outcome,
        "learning_use": "future_feedback_and_calibration_only",
        "real_world_actions_allowed": False,
        "decision": "learning_memory_record_paper_only",
        **paper_flags(),
    }


def build_operator_feedback_dataset(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    pipeline = build_multi_market_pipeline_report_from_json(file_path)
    workflow_state = build_operator_workflow_state(file_path, action_by_symbol)
    outcome_map = outcome_by_symbol or {}

    analysis_items = pipeline["pipeline"]["analysis_result"]["analysis"]["items"]
    actions_by_symbol = _index_by_symbol(workflow_state["actions"])

    records = []
    for item in analysis_items:
        symbol = item["symbol"]
        outcome = outcome_map.get(symbol, "pending_outcome")
        records.append(build_paper_learning_memory_record(
            item,
            actions_by_symbol[symbol],
            outcome,
        ))

    action_counts: dict[str, int] = {}
    outcome_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}

    for record in records:
        action = record["operator_action"]
        outcome = record["paper_outcome_status"]
        risk = record["risk_level"]
        action_counts[action] = action_counts.get(action, 0) + 1
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    dataset = {
        "ok": True,
        "type": "operator_feedback_dataset",
        "dataset_version": "p8_d2_operator_feedback_dataset_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(Path(file_path).name),
        "count": len(records),
        "symbols": [record["symbol"] for record in records],
        "action_counts": action_counts,
        "outcome_counts": outcome_counts,
        "risk_counts": risk_counts,
        "records": records,
        "source_pipeline_report": pipeline,
        "source_workflow_state": workflow_state,
        "decision": "operator_feedback_dataset_paper_only",
        **paper_flags(),
    }

    dataset["validation"] = validate_operator_feedback_dataset(dataset)
    return dataset


def validate_operator_feedback_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(dataset, dict):
        raise ValueError("operator_feedback_dataset must be a dict")
    if dataset.get("type") != "operator_feedback_dataset":
        raise ValueError("operator_feedback_dataset type is invalid")

    records = dataset.get("records")
    if not isinstance(records, list):
        raise ValueError("operator_feedback_dataset.records must be a list")

    checks = {
        "dataset_ok": dataset.get("ok") is True,
        "has_records": len(records) > 0,
        "count_matches_records": dataset.get("count") == len(records),
        "all_records_ok": all(record.get("ok") is True for record in records),
        "all_records_paper_only": all(record.get("paper_only") is True for record in records),
        "all_records_block_real_world_actions": all(
            record.get("real_world_actions_allowed") is False for record in records
        ),
        "paper_only_preserved": dataset.get("paper_only") is True,
        "operator_review_required": dataset.get("operator_review_required") is True,
        "no_real_exchange_api": dataset.get("real_exchange_api") is False,
        "no_real_brokerage_api": dataset.get("real_brokerage_api") is False,
        "no_real_api_key_required": dataset.get("real_api_key_required") is False,
        "no_wallet_private_key_required": dataset.get("wallet_private_key_required") is False,
        "no_real_order": dataset.get("real_order") is False,
        "no_real_execution": dataset.get("real_execution") is False,
        "no_real_balance": dataset.get("real_balance") is False,
        "no_real_position": dataset.get("real_position") is False,
        "no_real_money_impact": dataset.get("real_money_impact") is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_feedback_dataset_validation",
        "checks": checks,
        "decision": "feedback_dataset_validation_paper_only",
        **paper_flags(),
    }


def build_paper_outcome_tracking_contract(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    dataset = build_operator_feedback_dataset(
        file_path,
        action_by_symbol,
        outcome_by_symbol,
    )

    outcome_items = []
    for record in dataset["records"]:
        outcome_items.append({
            "symbol": record["symbol"],
            "asset_class": record["asset_class"],
            "market": record["market"],
            "paper_signal": record["paper_signal"],
            "operator_action": record["operator_action"],
            "paper_outcome_status": record["paper_outcome_status"],
            "tracking_status": "tracked_for_future_backtest",
            "real_world_actions_allowed": False,
        })

    return {
        "ok": True,
        "type": "paper_outcome_tracking_contract",
        "tracking_version": "p8_d3_paper_outcome_tracking_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(outcome_items),
        "symbols": [item["symbol"] for item in outcome_items],
        "outcome_counts": dataset["outcome_counts"],
        "items": outcome_items,
        "source_dataset": dataset,
        "decision": "outcome_tracking_paper_only_for_future_backtest",
        **paper_flags(),
    }


def write_learning_memory_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    schema = build_learning_memory_schema()
    dataset = build_operator_feedback_dataset(file_path, action_by_symbol, outcome_by_symbol)
    tracking = build_paper_outcome_tracking_contract(file_path, action_by_symbol, outcome_by_symbol)

    schema_path = directory / "learning_memory_schema.json"
    dataset_path = directory / "operator_feedback_dataset.json"
    tracking_path = directory / "paper_outcome_tracking_contract.json"

    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")
    dataset_path.write_text(json.dumps(dataset, indent=2, sort_keys=True), encoding="utf-8")
    tracking_path.write_text(json.dumps(tracking, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "learning_memory_bundle_written",
        "output_dir": str(directory),
        "schema_file": str(schema_path),
        "dataset_file": str(dataset_path),
        "tracking_file": str(tracking_path),
        "schema": schema,
        "dataset": dataset,
        "tracking": tracking,
        **paper_flags(),
    }
