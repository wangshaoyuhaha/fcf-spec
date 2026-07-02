import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_backtest_closeout import build_p9_closeout_package
from btc_finance_platform.paper_calibration_proposal import build_calibration_proposal_contract

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


def build_paper_model_registry_schema() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "paper_model_registry_schema",
        "schema_version": "p10_d1_paper_model_registry_schema_v1",
        "required_fields": [
            "model_version_id",
            "strategy_version_id",
            "source_phase",
            "training_status",
            "calibration_status",
            "deployment_status",
            "operator_approval_status",
            "paper_only",
        ],
        "allowed_training_status": ["not_trained", "offline_trained_pending_review"],
        "allowed_calibration_status": ["not_calibrated", "offline_calibrated_pending_review"],
        "allowed_deployment_status": ["not_deployed", "paper_registry_only"],
        "decision": "schema_only_no_model_training_no_deployment",
        **paper_flags(),
    }


def build_strategy_version_record(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
    strategy_version_id: str = "paper_strategy_v1",
) -> dict[str, Any]:
    closeout = build_p9_closeout_package(file_path, action_by_symbol, outcome_by_symbol)

    return {
        "ok": closeout["ok"] is True,
        "type": "strategy_version_record",
        "record_version": "p10_d2_strategy_version_record_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "strategy_version_id": strategy_version_id,
        "model_version_id": "paper_model_untrained_v1",
        "source_phase": "P9 backtest and calibration",
        "source_decision": closeout["decision"],
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "operator_approval_status": "operator_review_required_before_any_future_model_change",
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "strategy_version_record_paper_only_registry_metadata",
        **paper_flags(),
    }


def build_calibration_proposal_version_record(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    proposal = build_calibration_proposal_contract(file_path, action_by_symbol, outcome_by_symbol)

    return {
        "ok": proposal["ok"] is True,
        "type": "calibration_proposal_version_record",
        "record_version": "p10_d3_calibration_proposal_version_record_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "proposal_count": proposal["proposal_count"],
        "proposal_contract_version": proposal["contract_version"],
        "source_type": proposal["type"],
        "training_status": proposal["training_status"],
        "calibration_status": proposal["calibration_status"],
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "operator_approval_status": "operator_review_required_before_any_future_change",
        "decision": "calibration_proposal_version_record_no_parameter_update",
        **paper_flags(),
    }


def validate_model_registry_baseline(registry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(registry, dict):
        raise ValueError("model_registry_baseline must be a dict")
    if registry.get("type") != "model_registry_baseline":
        raise ValueError("model_registry_baseline type is invalid")

    strategy = registry["strategy_version_record"]
    calibration = registry["calibration_proposal_version_record"]

    checks = {
        "registry_ok": registry.get("ok") is True,
        "schema_ok": registry["schema"]["ok"] is True,
        "strategy_ok": strategy["ok"] is True,
        "calibration_record_ok": calibration["ok"] is True,
        "training_not_started": strategy["training_status"] == "not_trained",
        "calibration_not_started": strategy["calibration_status"] == "not_calibrated",
        "deployment_not_started": strategy["deployment_status"] == "not_deployed",
        "parameter_updates_blocked": strategy["parameter_update_allowed_now"] is False,
        "real_world_actions_blocked": strategy["real_world_actions_allowed"] is False,
        "paper_only_preserved": registry["paper_only"] is True,
        "operator_review_required": registry["operator_review_required"] is True,
        "no_real_exchange_api": registry["real_exchange_api"] is False,
        "no_real_brokerage_api": registry["real_brokerage_api"] is False,
        "no_real_order": registry["real_order"] is False,
        "no_real_execution": registry["real_execution"] is False,
        "no_real_money_impact": registry["real_money_impact"] is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "model_registry_baseline_validation",
        "checks": checks,
        "decision": "model_registry_baseline_validation_paper_only",
        **paper_flags(),
    }


def build_model_registry_baseline(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    schema = build_paper_model_registry_schema()
    strategy = build_strategy_version_record(file_path, action_by_symbol, outcome_by_symbol)
    calibration = build_calibration_proposal_version_record(file_path, action_by_symbol, outcome_by_symbol)

    registry = {
        "ok": schema["ok"] is True and strategy["ok"] is True and calibration["ok"] is True,
        "type": "model_registry_baseline",
        "registry_version": "p10_d1_d3_model_registry_baseline_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "schema": schema,
        "strategy_version_record": strategy,
        "calibration_proposal_version_record": calibration,
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "model_registry_baseline_paper_only_no_training_no_deployment",
        **paper_flags(),
    }

    registry["validation"] = validate_model_registry_baseline(registry)
    return registry


def write_model_registry_baseline_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    registry = build_model_registry_baseline(file_path, action_by_symbol, outcome_by_symbol)

    schema_file = directory / "paper_model_registry_schema.json"
    strategy_file = directory / "strategy_version_record.json"
    calibration_file = directory / "calibration_proposal_version_record.json"
    registry_file = directory / "model_registry_baseline.json"

    schema_file.write_text(json.dumps(registry["schema"], indent=2, sort_keys=True), encoding="utf-8")
    strategy_file.write_text(json.dumps(registry["strategy_version_record"], indent=2, sort_keys=True), encoding="utf-8")
    calibration_file.write_text(json.dumps(registry["calibration_proposal_version_record"], indent=2, sort_keys=True), encoding="utf-8")
    registry_file.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "model_registry_baseline_bundle_written",
        "output_dir": str(directory),
        "schema_file": str(schema_file),
        "strategy_file": str(strategy_file),
        "calibration_file": str(calibration_file),
        "registry_file": str(registry_file),
        "registry": registry,
        **paper_flags(),
    }
