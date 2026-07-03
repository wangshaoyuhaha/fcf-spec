import json
from pathlib import Path
from typing import Any


FORBIDDEN_PATCH_TARGETS = (
    "exchange_api",
    "brokerage_api",
    "api_key",
    "wallet_private_key",
    "real_order",
    "real_execution",
    "real_balance",
    "real_position",
    "private_key",
    "secret_key",
)


def _contains_forbidden_patch_target(payload: dict[str, Any]) -> bool:
    scan_parts: list[str] = []

    if isinstance(payload, dict):
        for key in ("proposal_id", "title", "rationale"):
            value = payload.get(key)
            if value:
                scan_parts.append(str(value))

        for key in ("target_files", "test_plan", "risk_notes"):
            value = payload.get(key, [])
            if isinstance(value, list):
                scan_parts.extend(str(item) for item in value)
            elif value:
                scan_parts.append(str(value))
    else:
        scan_parts.append(str(payload))

    text = "\n".join(scan_parts).lower()
    return any(item in text for item in FORBIDDEN_PATCH_TARGETS)


def build_patch_proposal(
    proposal_id: str,
    title: str,
    rationale: str,
    target_files: list[str],
    test_plan: list[str],
    risk_notes: list[str] | None = None,
) -> dict[str, Any]:
    if not proposal_id:
        raise ValueError("proposal_id is required")

    if not title:
        raise ValueError("title is required")

    if not rationale:
        raise ValueError("rationale is required")

    if not isinstance(target_files, list) or not target_files:
        raise ValueError("target_files must be a non-empty list")

    if not isinstance(test_plan, list) or not test_plan:
        raise ValueError("test_plan must be a non-empty list")

    risk_notes = risk_notes or []

    candidate = {
        "proposal_id": proposal_id,
        "title": title,
        "rationale": rationale,
        "target_files": target_files,
        "test_plan": test_plan,
        "risk_notes": risk_notes,
    }

    if _contains_forbidden_patch_target(candidate):
        raise ValueError("forbidden patch target detected")

    return {
        "ok": True,
        "type": "p14_patch_proposal",
        "proposal_id": proposal_id,
        "title": title,
        "rationale": rationale,
        "target_files": target_files,
        "test_plan": test_plan,
        "risk_notes": risk_notes,
        "proposal_status": "READY_FOR_SCENARIO_AND_OPERATOR_REVIEW",
        "ai_patch_design_allowed": True,
        "patch_auto_apply_allowed": False,
        "auto_commit_allowed": False,
        "auto_merge_allowed": False,
        "auto_release_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
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
    }


def validate_patch_proposal_gate(proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a dict")

    if proposal.get("type") != "p14_patch_proposal":
        raise ValueError("invalid patch proposal type")

    if _contains_forbidden_patch_target(proposal):
        raise ValueError("forbidden patch target detected")

    required_false_fields = (
        "patch_auto_apply_allowed",
        "auto_commit_allowed",
        "auto_merge_allowed",
        "auto_release_allowed",
        "real_world_actions_allowed",
        "real_order",
        "real_execution",
        "real_money_impact",
    )

    failed_fields = [
        field for field in required_false_fields
        if proposal.get(field) is not False
    ]

    if proposal.get("operator_review_required") is not True:
        failed_fields.append("operator_review_required")

    gate_status = "passed" if not failed_fields else "blocked"

    return {
        "ok": True,
        "type": "p14_patch_proposal_gate",
        "proposal_id": proposal.get("proposal_id"),
        "gate_status": gate_status,
        "failed_fields": failed_fields,
        "scenario_review_required": True,
        "operator_review_required": True,
        "patch_auto_apply_allowed": False,
        "auto_commit_allowed": False,
        "auto_merge_allowed": False,
        "auto_release_allowed": False,
        "paper_only": True,
        "local_only": True,
        "real_world_actions_allowed": False,
    }


def write_patch_proposal(
    proposal: dict[str, Any],
    path: str | Path,
) -> dict[str, Any]:
    gate = validate_patch_proposal_gate(proposal)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "ok": True,
        "type": "p14_patch_proposal_record",
        "proposal": proposal,
        "gate": gate,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "patch_auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }

    output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_patch_proposal_record_written",
        "output_path": str(output),
        "record": record,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "patch_auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }

