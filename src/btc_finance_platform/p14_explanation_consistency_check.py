import json
from pathlib import Path
from typing import Any


UNSAFE_EXPLANATION_PHRASES = (
    "real order allowed",
    "real execution allowed",
    "trading buttons enabled",
    "auto apply allowed",
    "auto trade allowed",
    "api key required",
    "wallet private key required",
    "deployment allowed now",
    "real money impact",
)


def detect_unsafe_explanation_phrases(explanation: str) -> list[str]:
    if not isinstance(explanation, str):
        raise ValueError("explanation must be a string")

    lowered = explanation.lower()
    return [phrase for phrase in UNSAFE_EXPLANATION_PHRASES if phrase in lowered]


def check_field_consistency(
    report: dict[str, Any],
    explanation_claims: dict[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(report, dict):
        raise ValueError("report must be a dict")

    if not isinstance(explanation_claims, dict):
        raise ValueError("explanation_claims must be a dict")

    mismatches = []

    for key, claimed_value in explanation_claims.items():
        if key in report and report.get(key) != claimed_value:
            mismatches.append(
                {
                    "field": key,
                    "python_value": report.get(key),
                    "explanation_claim": claimed_value,
                    "mismatch_type": "field_value_mismatch",
                }
            )

    return mismatches


def build_explanation_consistency_report(
    source_report: dict[str, Any],
    explanation_text: str,
    explanation_claims: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(source_report, dict):
        raise ValueError("source_report must be a dict")

    unsafe_phrases = detect_unsafe_explanation_phrases(explanation_text)
    mismatches = check_field_consistency(source_report, explanation_claims)

    blocked = bool(unsafe_phrases or mismatches)

    if blocked:
        consistency_status = "BLOCKED_FOR_OPERATOR_REVIEW"
    else:
        consistency_status = "CONSISTENT_READY_FOR_OPERATOR_REVIEW"

    return {
        "ok": True,
        "type": "p14_explanation_consistency_report",
        "current_stage": "P14-D37-D39",
        "consistency_status": consistency_status,
        "purpose": "ensure AI explanations do not contradict Python report fields or safety boundaries",
        "source_report_type": source_report.get("type", "unknown"),
        "unsafe_phrase_count": len(unsafe_phrases),
        "unsafe_phrases": unsafe_phrases,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "blocked": blocked,
        "consistency_policy": {
            "python_report_is_source_of_truth": True,
            "ai_explanation_override_allowed": False,
            "auto_approve_explanation_allowed": False,
            "operator_review_required": True,
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
    }


def write_explanation_consistency_report(
    source_report: dict[str, Any],
    explanation_text: str,
    explanation_claims: dict[str, Any],
    path: str | Path,
) -> dict[str, Any]:
    report = build_explanation_consistency_report(
        source_report=source_report,
        explanation_text=explanation_text,
        explanation_claims=explanation_claims,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_explanation_consistency_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "ai_explanation_override_allowed": False,
        "real_world_actions_allowed": False,
    }
