import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_DIRECTIONS = {"long", "short", "flat", "observe"}

FORBIDDEN_KEYS = (
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
    return any(key in text for key in FORBIDDEN_KEYS)


def _validate_expert_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise ValueError("expert proposal must be a dict")

    if _contains_forbidden_key(proposal):
        raise ValueError("forbidden sensitive field detected")

    expert_id = proposal.get("expert_id")
    direction = proposal.get("direction")
    confidence = proposal.get("confidence")

    if not expert_id:
        raise ValueError("expert_id is required")

    if direction not in ALLOWED_DIRECTIONS:
        raise ValueError("direction is invalid")

    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be numeric")

    if confidence < 0 or confidence > 1:
        raise ValueError("confidence must be between 0 and 1")

    return {
        "expert_id": str(expert_id),
        "direction": direction,
        "confidence": float(confidence),
        "paper_entry": proposal.get("paper_entry"),
        "paper_stop": proposal.get("paper_stop"),
        "paper_take_profit": proposal.get("paper_take_profit"),
        "rationale": proposal.get("rationale", ""),
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def build_shadow_ledger_event(
    decision_id: str,
    regime: str,
    expert_proposals: list[dict[str, Any]],
    selected_expert_id: str | None = None,
) -> dict[str, Any]:
    if not decision_id:
        raise ValueError("decision_id is required")

    if not regime:
        raise ValueError("regime is required")

    if not isinstance(expert_proposals, list) or not expert_proposals:
        raise ValueError("expert_proposals must be a non-empty list")

    proposals = [_validate_expert_proposal(item) for item in expert_proposals]
    expert_ids = {item["expert_id"] for item in proposals}

    if selected_expert_id is not None and selected_expert_id not in expert_ids:
        raise ValueError("selected_expert_id must exist in expert proposals")

    return {
        "ok": True,
        "type": "p14_shadow_ledger_event",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "decision_id": decision_id,
        "regime": regime,
        "selected_expert_id": selected_expert_id,
        "expert_proposals": proposals,
        "proposal_count": len(proposals),
        "counterfactual_learning_enabled": True,
        "learning_mode": "shadow_paper_only",
        "paper_only": True,
        "local_only": True,
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
    }


def append_shadow_ledger_event(
    ledger_path: str | Path,
    decision_id: str,
    regime: str,
    expert_proposals: list[dict[str, Any]],
    selected_expert_id: str | None = None,
) -> dict[str, Any]:
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
    else:
        ledger = {
            "ok": True,
            "type": "p14_shadow_ledger",
            "ledger_scope": "local_only_paper_shadow",
            "events": [],
            "paper_only": True,
            "operator_review_required": True,
        }

    if ledger.get("type") != "p14_shadow_ledger":
        raise ValueError("invalid shadow ledger type")

    event = build_shadow_ledger_event(
        decision_id,
        regime,
        expert_proposals,
        selected_expert_id,
    )

    ledger["events"].append(event)
    ledger["event_count"] = len(ledger["events"])
    ledger["real_world_actions_allowed"] = False
    ledger["trading_buttons_enabled"] = False
    ledger["real_order"] = False
    ledger["real_execution"] = False

    path.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_shadow_ledger_appended",
        "ledger_path": str(path),
        "event_count": ledger["event_count"],
        "latest_event": event,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
    }


def summarize_shadow_ledger(ledger_path: str | Path) -> dict[str, Any]:
    path = Path(ledger_path)

    if not path.exists():
        return {
            "ok": True,
            "type": "p14_shadow_ledger_summary",
            "event_count": 0,
            "regime_counts": {},
            "expert_counts": {},
            "paper_only": True,
            "real_world_actions_allowed": False,
        }

    ledger = json.loads(path.read_text(encoding="utf-8"))
    if ledger.get("type") != "p14_shadow_ledger":
        raise ValueError("invalid shadow ledger type")

    regime_counts: dict[str, int] = {}
    expert_counts: dict[str, int] = {}

    for event in ledger.get("events", []):
        regime = event.get("regime", "unknown")
        regime_counts[regime] = regime_counts.get(regime, 0) + 1

        for proposal in event.get("expert_proposals", []):
            expert_id = proposal.get("expert_id", "unknown")
            expert_counts[expert_id] = expert_counts.get(expert_id, 0) + 1

    return {
        "ok": True,
        "type": "p14_shadow_ledger_summary",
        "event_count": len(ledger.get("events", [])),
        "regime_counts": regime_counts,
        "expert_counts": expert_counts,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
    }
