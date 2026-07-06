"""D4 reason code and risk flag coverage reports for MODEL-GOVERNANCE-APP-1.

This module builds paper-only coverage reports for reason codes and risk flags.
It does not mutate scores, reason codes, risk flags, source artifacts, or core modules.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional


COVERAGE_STATUS_VALUES: List[str] = [
    "COVERAGE_COMPLETE",
    "COVERAGE_PARTIAL",
    "COVERAGE_MISSING",
    "COVERAGE_REVIEW_REQUIRED",
    "COVERAGE_BLOCKED",
]

COVERAGE_ITEM_TYPES: List[str] = [
    "REASON_CODE",
    "RISK_FLAG",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_items(items: Iterable[str]) -> List[str]:
    return sorted({str(item).strip() for item in items if str(item).strip()})


def _coverage_ratio(observed: List[str], governed: List[str]) -> float:
    if not observed:
        return 1.0
    governed_set = set(governed)
    covered = [item for item in observed if item in governed_set]
    return len(covered) / len(observed)


def infer_coverage_status(
    *,
    observed_items: List[str],
    governed_items: List[str],
    blocked_items: Optional[List[str]] = None,
) -> str:
    """Infer paper-only governance coverage status."""

    blocked = _normalize_items(blocked_items or [])
    if blocked:
        return "COVERAGE_BLOCKED"

    if not observed_items:
        return "COVERAGE_MISSING"

    ratio = _coverage_ratio(observed_items, governed_items)
    if ratio == 1.0:
        return "COVERAGE_COMPLETE"
    if ratio == 0.0:
        return "COVERAGE_REVIEW_REQUIRED"

    return "COVERAGE_PARTIAL"


def build_coverage_report(
    *,
    report_id: str,
    item_type: str,
    observed_items: Iterable[str],
    governed_items: Iterable[str],
    source_layers: Optional[List[str]] = None,
    blocked_items: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build one paper-only coverage report."""

    if item_type not in COVERAGE_ITEM_TYPES:
        raise ValueError(f"Unsupported coverage item type: {item_type}")

    observed = _normalize_items(observed_items)
    governed = _normalize_items(governed_items)
    blocked = _normalize_items(blocked_items or [])

    covered = [item for item in observed if item in set(governed)]
    uncovered = [item for item in observed if item not in set(governed)]
    unused_governed = [item for item in governed if item not in set(observed)]
    status = infer_coverage_status(
        observed_items=observed,
        governed_items=governed,
        blocked_items=blocked,
    )

    return {
        "app_id": "MODEL-GOVERNANCE-APP-1",
        "stage_id": "MODEL-GOVERNANCE-D4",
        "report_id": report_id,
        "item_type": item_type,
        "coverage_status": status,
        "created_at_utc": _utc_now_iso(),
        "source_layers": list(source_layers or []),
        "observed_count": len(observed),
        "governed_count": len(governed),
        "covered_count": len(covered),
        "uncovered_count": len(uncovered),
        "unused_governed_count": len(unused_governed),
        "blocked_count": len(blocked),
        "coverage_ratio": _coverage_ratio(observed, governed),
        "observed_items": observed,
        "governed_items": governed,
        "covered_items": covered,
        "uncovered_items": uncovered,
        "unused_governed_items": unused_governed,
        "blocked_items": blocked,
        "notes": list(notes or []),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
    }


def build_reason_code_coverage_report(
    *,
    report_id: str,
    observed_reason_codes: Iterable[str],
    governed_reason_codes: Iterable[str],
    source_layers: Optional[List[str]] = None,
    blocked_reason_codes: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a paper-only reason code coverage report."""

    return build_coverage_report(
        report_id=report_id,
        item_type="REASON_CODE",
        observed_items=observed_reason_codes,
        governed_items=governed_reason_codes,
        source_layers=source_layers,
        blocked_items=blocked_reason_codes,
        notes=notes,
    )


def build_risk_flag_coverage_report(
    *,
    report_id: str,
    observed_risk_flags: Iterable[str],
    governed_risk_flags: Iterable[str],
    source_layers: Optional[List[str]] = None,
    blocked_risk_flags: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a paper-only risk flag coverage report."""

    return build_coverage_report(
        report_id=report_id,
        item_type="RISK_FLAG",
        observed_items=observed_risk_flags,
        governed_items=governed_risk_flags,
        source_layers=source_layers,
        blocked_items=blocked_risk_flags,
        notes=notes,
    )


def build_governance_coverage_packet(
    *,
    packet_id: str,
    reason_code_report: Mapping[str, Any],
    risk_flag_report: Mapping[str, Any],
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a combined paper-only governance coverage packet."""

    report_statuses = {
        reason_code_report.get("coverage_status", "COVERAGE_REVIEW_REQUIRED"),
        risk_flag_report.get("coverage_status", "COVERAGE_REVIEW_REQUIRED"),
    }

    if "COVERAGE_BLOCKED" in report_statuses:
        packet_status = "GOVERNANCE_COVERAGE_BLOCKED"
    elif "COVERAGE_REVIEW_REQUIRED" in report_statuses:
        packet_status = "GOVERNANCE_COVERAGE_REVIEW_REQUIRED"
    elif "COVERAGE_PARTIAL" in report_statuses:
        packet_status = "GOVERNANCE_COVERAGE_PARTIAL"
    elif "COVERAGE_MISSING" in report_statuses:
        packet_status = "GOVERNANCE_COVERAGE_REVIEW_REQUIRED"
    else:
        packet_status = "GOVERNANCE_COVERAGE_READY_FOR_OPERATOR_REVIEW"

    return {
        "app_id": "MODEL-GOVERNANCE-APP-1",
        "stage_id": "MODEL-GOVERNANCE-D4",
        "packet_id": packet_id,
        "packet_status": packet_status,
        "created_at_utc": _utc_now_iso(),
        "reason_code_report": dict(reason_code_report),
        "risk_flag_report": dict(risk_flag_report),
        "notes": list(notes or []),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "source_content_mutation_allowed": False,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
    }


def validate_governance_coverage_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a D4 coverage packet boundary."""

    required_fields = [
        "app_id",
        "stage_id",
        "packet_id",
        "packet_status",
        "reason_code_report",
        "risk_flag_report",
        "operator_review_required",
        "trade_action_enabled",
        "real_execution_allowed",
    ]

    missing_fields = [field for field in required_fields if field not in packet]
    unsafe_true_fields = [
        field
        for field in [
            "score_mutation_allowed",
            "reason_code_mutation_allowed",
            "risk_flag_deletion_allowed",
            "source_content_mutation_allowed",
            "trade_action_enabled",
            "real_execution_allowed",
            "future_return_prediction_allowed",
            "guaranteed_performance_claim_allowed",
        ]
        if packet.get(field) is True
    ]

    return {
        "schema_id": "MODEL-GOVERNANCE-D4-COVERAGE-PACKET",
        "is_valid": not missing_fields and not unsafe_true_fields,
        "missing_fields": missing_fields,
        "unsafe_true_fields": unsafe_true_fields,
        "operator_review_required": packet.get("operator_review_required") is True,
        "trade_action_enabled": packet.get("trade_action_enabled") is True,
        "real_execution_allowed": packet.get("real_execution_allowed") is True,
    }


def summarize_governance_coverage_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return compact D4 coverage summary."""

    reason_report = packet["reason_code_report"]
    risk_report = packet["risk_flag_report"]
    return {
        "app_id": packet["app_id"],
        "stage_id": packet["stage_id"],
        "packet_id": packet["packet_id"],
        "packet_status": packet["packet_status"],
        "reason_code_coverage_status": reason_report["coverage_status"],
        "risk_flag_coverage_status": risk_report["coverage_status"],
        "reason_code_uncovered_count": reason_report["uncovered_count"],
        "risk_flag_uncovered_count": risk_report["uncovered_count"],
        "operator_review_required": packet["operator_review_required"],
        "score_mutation_allowed": packet["score_mutation_allowed"],
        "reason_code_mutation_allowed": packet["reason_code_mutation_allowed"],
        "risk_flag_deletion_allowed": packet["risk_flag_deletion_allowed"],
        "trade_action_enabled": packet["trade_action_enabled"],
        "real_execution_allowed": packet["real_execution_allowed"],
    }
