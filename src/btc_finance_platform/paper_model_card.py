import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_model_registry import build_model_registry_baseline

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


def build_paper_model_card(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    registry = build_model_registry_baseline(file_path, action_by_symbol, outcome_by_symbol)
    strategy = registry["strategy_version_record"]

    return {
        "ok": registry["ok"] is True and registry["validation"]["ok"] is True,
        "type": "paper_model_card",
        "card_version": "p10_d4_paper_model_card_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_version_id": strategy["model_version_id"],
        "strategy_version_id": strategy["strategy_version_id"],
        "source_registry_version": registry["registry_version"],
        "source_phase": "P10 model registry and strategy versioning",
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "model_purpose": "paper_only_metadata_record",
        "limitations": [
            "not trained",
            "not calibrated",
            "not deployed",
            "not financial advice",
            "not for real execution",
        ],
        "allowed_use": [
            "paper registry display",
            "operator review",
            "future offline model registry handoff",
        ],
        "forbidden_use": [
            "automatic live trading",
            "real order generation",
            "real execution",
            "real money impact",
            "bypassing operator review",
        ],
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "paper_model_card_no_training_no_deployment",
        **paper_flags(),
    }


def build_operator_model_approval_gate(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    card = build_paper_model_card(file_path, action_by_symbol, outcome_by_symbol)

    checks = {
        "card_ok": card["ok"] is True,
        "training_not_started": card["training_status"] == "not_trained",
        "calibration_not_started": card["calibration_status"] == "not_calibrated",
        "deployment_not_started": card["deployment_status"] == "not_deployed",
        "deployment_blocked": card["deployment_allowed_now"] is False,
        "parameter_updates_blocked": card["parameter_update_allowed_now"] is False,
        "real_world_actions_blocked": card["real_world_actions_allowed"] is False,
        "paper_only_preserved": card["paper_only"] is True,
        "operator_review_required": card["operator_review_required"] is True,
        "no_real_exchange_api": card["real_exchange_api"] is False,
        "no_real_brokerage_api": card["real_brokerage_api"] is False,
        "no_real_order": card["real_order"] is False,
        "no_real_execution": card["real_execution"] is False,
        "no_real_money_impact": card["real_money_impact"] is False,
    }

    return {
        "ok": all(checks.values()),
        "type": "operator_model_approval_gate",
        "gate_version": "p10_d5_operator_model_approval_gate_v1",
        "gate": "pass" if all(checks.values()) else "fail",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_version_id": card["model_version_id"],
        "strategy_version_id": card["strategy_version_id"],
        "checks": checks,
        "approval_status": "operator_review_required_before_future_model_change",
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "operator_model_approval_gate_blocks_live_use",
        **paper_flags(),
    }


def build_model_registry_readable_report(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    card = build_paper_model_card(file_path, action_by_symbol, outcome_by_symbol)
    gate = build_operator_model_approval_gate(file_path, action_by_symbol, outcome_by_symbol)

    lines = [
        "# Paper Model Registry Report",
        "",
        "Status: paper-only model registry report",
        "",
        "Created at UTC: " + datetime.now(timezone.utc).isoformat(),
        "",
        "## Model Card",
        "",
        "- Model version ID: " + card["model_version_id"],
        "- Strategy version ID: " + card["strategy_version_id"],
        "- Training status: " + card["training_status"],
        "- Calibration status: " + card["calibration_status"],
        "- Deployment status: " + card["deployment_status"],
        "- Deployment allowed now: false",
        "- Parameter update allowed now: false",
        "- Real-world actions allowed: false",
        "",
        "## Approval Gate",
        "",
        "- Gate: " + gate["gate"],
        "- Approval status: " + gate["approval_status"],
        "- Deployment allowed now: false",
        "- Operator review required: true",
        "",
        "## Final Notice",
        "",
        "This report does not train a model.",
        "This report does not deploy a model.",
        "This report does not update parameters.",
        "This report must not be used for real execution.",
        "",
    ]

    return {
        "ok": card["ok"] is True and gate["ok"] is True,
        "type": "model_registry_readable_report",
        "report_version": "p10_d6_model_registry_readable_report_v1",
        "model_card": card,
        "approval_gate": gate,
        "markdown": "\n".join(lines),
        "training_status": "not_trained",
        "calibration_status": "not_calibrated",
        "deployment_status": "not_deployed",
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_world_actions_allowed": False,
        "decision": "model_registry_report_paper_only",
        **paper_flags(),
    }


def write_model_card_report_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    card = build_paper_model_card(file_path, action_by_symbol, outcome_by_symbol)
    gate = build_operator_model_approval_gate(file_path, action_by_symbol, outcome_by_symbol)
    report = build_model_registry_readable_report(file_path, action_by_symbol, outcome_by_symbol)

    card_file = directory / "paper_model_card.json"
    gate_file = directory / "operator_model_approval_gate.json"
    report_file = directory / "model_registry_report.md"

    card_file.write_text(json.dumps(card, indent=2, sort_keys=True), encoding="utf-8")
    gate_file.write_text(json.dumps(gate, indent=2, sort_keys=True), encoding="utf-8")
    report_file.write_text(report["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "model_card_report_bundle_written",
        "output_dir": str(directory),
        "card_file": str(card_file),
        "gate_file": str(gate_file),
        "report_file": str(report_file),
        "card": card,
        "gate": gate,
        "report": report,
        **paper_flags(),
    }
