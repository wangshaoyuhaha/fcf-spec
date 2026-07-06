"""RISK-EXPOSURE-D4 paper risk exposure review model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, Iterable, List

from apps.risk_exposure_app_1.contract import APP_ID
from apps.risk_exposure_app_1.exposure_schema import (
    create_paper_risk_exposure_record,
    validate_paper_risk_exposure_record,
)


STAGE_ID = "RISK-EXPOSURE-D4"
MODEL_VERSION = "1.0.0"

DROP_FLAGS = {"DROP_REVIEW", "QUARANTINE_REQUIRED"}
GOVERNANCE_FLAGS = {"GOVERNANCE_BLOCKED", "SIGNAL_VALIDATION_FAILED", "MODEL_GOVERNANCE_REVIEW"}
CORRELATION_FLAGS = {"CORRELATION_REVIEW", "THEME_CLUSTER_REVIEW"}


def _clean_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _normalize_flags(values: Any) -> List[str]:
    return sorted({str(item).strip().upper() for item in values or [] if str(item).strip()})


def _select_risk_state(
    candidate: Dict[str, Any],
    asset_count: int,
    sector_count: int,
    theme_count: int,
    source_manifest: Dict[str, Any],
) -> str:
    flags = set(_normalize_flags(candidate.get("risk_flags")))

    if flags.intersection(DROP_FLAGS):
        return "DROP_RISK_REVIEW"

    if flags.intersection(GOVERNANCE_FLAGS):
        return "GOVERNANCE_RISK_REVIEW"

    if source_manifest.get("missing_source_count", 0) > 0:
        return "SOURCE_GAP_RISK_REVIEW"

    if asset_count >= 3 or sector_count >= 3:
        return "CONCENTRATION_RISK_REVIEW"

    if theme_count >= 2 or flags.intersection(CORRELATION_FLAGS):
        return "CORRELATION_RISK_REVIEW"

    return "PAPER_RISK_REVIEW"


def build_paper_risk_exposure_review(
    candidates: Iterable[Dict[str, Any]],
    source_manifest: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_list = list(candidates)

    asset_counts = Counter(_clean_text(item.get("asset_class"), "UNKNOWN") for item in candidate_list)
    sector_counts = Counter(_clean_text(item.get("sector"), "UNKNOWN") for item in candidate_list)
    theme_counts = Counter(_clean_text(item.get("theme"), "UNKNOWN") for item in candidate_list)

    risk_records: List[Dict[str, Any]] = []

    for index, item in enumerate(candidate_list, start=1):
        candidate_id = _clean_text(item.get("candidate_id"), "candidate-" + str(index).zfill(3))
        symbol = _clean_text(item.get("symbol"), candidate_id)
        asset_class = _clean_text(item.get("asset_class"), "UNKNOWN")
        sector = _clean_text(item.get("sector"), "UNKNOWN")
        theme = _clean_text(item.get("theme"), "UNKNOWN")
        observed_flags = _normalize_flags(item.get("risk_flags"))

        state = _select_risk_state(
            candidate=item,
            asset_count=asset_counts[asset_class],
            sector_count=sector_counts[sector],
            theme_count=theme_counts[theme],
            source_manifest=source_manifest,
        )

        record = create_paper_risk_exposure_record(
            risk_exposure_record_id="risk-exposure-" + candidate_id,
            candidate_id=candidate_id,
            symbol=symbol,
            asset_class=asset_class,
            sector=sector,
            theme=theme,
            risk_exposure_state=state,
            risk_review_reason="paper risk exposure review only",
            observed_risk_flags=observed_flags,
            created_at_utc=str(item.get("created_at_utc") or "2026-07-06T00:00:00+00:00"),
        )
        risk_records.append(record)

    validation_results = [validate_paper_risk_exposure_record(record) for record in risk_records]
    invalid_count = sum(1 for item in validation_results if not item["valid"])

    state_counts = Counter(record["risk_exposure_state"] for record in risk_records)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "model_version": MODEL_VERSION,
        "candidate_count": len(candidate_list),
        "symbol_count": len({record["symbol"] for record in risk_records}),
        "asset_class_counts": dict(asset_counts),
        "sector_counts": dict(sector_counts),
        "theme_counts": dict(theme_counts),
        "state_counts": dict(state_counts),
        "risk_exposure_records": risk_records,
        "risk_exposure_validation_results": validation_results,
        "invalid_risk_exposure_record_count": invalid_count,
        "source_manifest_id": source_manifest.get("stage_id", "RISK-EXPOSURE-D2"),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "real_risk_management_allowed": False,
        "position_management_allowed": False,
        "position_size_suggestion_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "risk_based_rebalance_allowed": False,
        "trade_action_allowed": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
    }


def validate_paper_risk_exposure_review(review: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(review)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("candidate_count") != len(candidate.get("risk_exposure_records", [])):
        issues.append("candidate_count must match risk_exposure_records")

    if candidate.get("invalid_risk_exposure_record_count") != 0:
        issues.append("invalid_risk_exposure_record_count must be zero")

    for true_key in ["operator_review_required", "paper_only", "local_only", "read_only", "sidecar_only"]:
        if candidate.get(true_key) is not True:
            issues.append(true_key + " must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "real_risk_management_allowed",
        "position_management_allowed",
        "position_size_suggestion_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "risk_based_rebalance_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "risk_flag_deletion_allowed",
        "risk_flag_downgrade_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "candidate_count": candidate.get("candidate_count"),
    }
