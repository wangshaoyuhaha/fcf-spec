import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_MEMORY_KEYS = (
    "api_key",
    "secret_key",
    "private_key",
    "wallet_private_key",
    "exchange_credential",
    "brokerage_credential",
    "real_balance",
    "real_position",
)


def _contains_forbidden_key(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    return any(key in text for key in FORBIDDEN_MEMORY_KEYS)


def build_learning_memory_event(
    event_type: str,
    summary: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not event_type:
        raise ValueError("event_type is required")

    if not summary:
        raise ValueError("summary is required")

    evidence = evidence or {}

    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a dict")

    candidate = {
        "event_type": event_type,
        "summary": summary,
        "evidence": evidence,
    }

    if _contains_forbidden_key(candidate):
        raise ValueError("forbidden sensitive memory detected")

    return {
        "ok": True,
        "type": "p13_learning_memory_event",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "summary": summary,
        "evidence": evidence,
        "learning_mode": "audit_and_proposal_only",
        "memory_scope": "local_json_ledger",
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "patch_auto_apply_allowed": False,
        "trading_buttons_enabled": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def append_learning_memory_event(
    ledger_path: str | Path,
    event_type: str,
    summary: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
    else:
        ledger = {
            "ok": True,
            "type": "p13_ai_learning_memory_ledger",
            "ledger_scope": "local_only",
            "paper_only": True,
            "operator_review_required": True,
            "events": [],
        }

    if ledger.get("type") != "p13_ai_learning_memory_ledger":
        raise ValueError("invalid ledger type")

    event = build_learning_memory_event(event_type, summary, evidence)
    ledger["events"].append(event)
    ledger["event_count"] = len(ledger["events"])
    ledger["real_world_actions_allowed"] = False
    ledger["patch_auto_apply_allowed"] = False
    ledger["trading_buttons_enabled"] = False

    path.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p13_ai_learning_memory_ledger_appended",
        "ledger_path": str(path),
        "event_count": ledger["event_count"],
        "latest_event": event,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "patch_auto_apply_allowed": False,
    }
