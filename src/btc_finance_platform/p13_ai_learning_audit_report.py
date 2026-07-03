import json
from pathlib import Path
from typing import Any


def load_learning_ledger(path: str | Path) -> dict[str, Any]:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return {
            "ok": True,
            "type": "p13_ai_learning_memory_ledger",
            "ledger_scope": "local_only",
            "paper_only": True,
            "operator_review_required": True,
            "events": [],
            "event_count": 0,
        }

    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    if data.get("type") != "p13_ai_learning_memory_ledger":
        raise ValueError("invalid learning ledger type")
    return data


def build_ai_learning_audit_report(ledger_path: str | Path) -> dict[str, Any]:
    ledger = load_learning_ledger(ledger_path)
    events = ledger.get("events", [])

    if not isinstance(events, list):
        raise ValueError("ledger events must be a list")

    return {
        "ok": True,
        "type": "p13_ai_learning_audit_report",
        "current_stage": "P13-D25-D27",
        "audit_status": "READY_FOR_OPERATOR_REVIEW",
        "event_count": len(events),
        "learning_mode": "audit_and_proposal_only",
        "self_audit_enabled": True,
        "bug_detection_scope": [
            "missing_required_fields",
            "invalid_ledger_type",
            "unsafe_real_action_flags",
            "sensitive_memory_rejection",
            "regression_test_failure",
        ],
        "bug_detection_limitations": [
            "cannot_prove_absence_of_all_bugs",
            "cannot_predict_black_swan_market_events",
            "cannot_validate_unseen_strategy_logic_without_tests",
        ],
        "patch_policy": {
            "patch_proposal_allowed": True,
            "patch_auto_apply_allowed": False,
            "auto_merge_allowed": False,
            "auto_release_allowed": False,
            "operator_review_required": True,
        },
        "memory_policy": {
            "memory_required_for_learning": True,
            "memory_scope": "local_json_ledger",
            "forbidden_memory": [
                "api_keys",
                "wallet_private_keys",
                "real_exchange_credentials",
                "real_brokerage_credentials",
                "real_balances",
                "real_positions",
            ],
        },
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "operator_review_required": True,
        "trading_buttons_enabled": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "ledger_summary": {
            "ledger_type": ledger.get("type"),
            "ledger_scope": ledger.get("ledger_scope", "local_only"),
            "event_count": len(events),
        },
    }


def write_ai_learning_audit_report(
    ledger_path: str | Path,
    report_path: str | Path,
) -> dict[str, Any]:
    report = build_ai_learning_audit_report(ledger_path)
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p13_ai_learning_audit_report_written",
        "report_path": str(path),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "patch_auto_apply_allowed": False,
    }
