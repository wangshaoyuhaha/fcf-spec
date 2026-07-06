"""PORTFOLIO-REVIEW-D4 paper portfolio review model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, Iterable, List

from apps.portfolio_review_app_1.contract import APP_ID
from apps.portfolio_review_app_1.exposure_schema import (
    create_paper_exposure_record,
    validate_paper_exposure_record,
)


STAGE_ID = "PORTFOLIO-REVIEW-D4"
MODEL_VERSION = "1.0.0"


def _clean_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _select_state(candidate: Dict[str, Any], asset_count: int, sector_count: int, source_manifest: Dict[str, Any]) -> str:
    risk_flags = {str(item).upper() for item in candidate.get("risk_flags", [])}

    if "DROP_REVIEW" in risk_flags or "QUARANTINE_REQUIRED" in risk_flags:
        return "DROP_REVIEW"

    if source_manifest.get("missing_source_count", 0) > 0:
        return "SOURCE_GAP_REVIEW"

    if asset_count >= 3 or sector_count >= 3:
        return "CONCENTRATION_REVIEW"

    if asset_count == 1 and sector_count == 1:
        return "DIVERSIFICATION_REVIEW"

    return "PAPER_EXPOSURE_REVIEW"


def build_paper_portfolio_review(
    candidates: Iterable[Dict[str, Any]],
    source_manifest: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_list = list(candidates)

    asset_counts = Counter(_clean_text(item.get("asset_class"), "UNKNOWN") for item in candidate_list)
    sector_counts = Counter(_clean_text(item.get("sector"), "UNKNOWN") for item in candidate_list)
    theme_counts = Counter(_clean_text(item.get("theme"), "UNKNOWN") for item in candidate_list)

    exposure_records: List[Dict[str, Any]] = []

    for index, item in enumerate(candidate_list, start=1):
        candidate_id = _clean_text(item.get("candidate_id"), "candidate-" + str(index).zfill(3))
        symbol = _clean_text(item.get("symbol"), candidate_id)
        asset_class = _clean_text(item.get("asset_class"), "UNKNOWN")
        sector = _clean_text(item.get("sector"), "UNKNOWN")
        theme = _clean_text(item.get("theme"), "UNKNOWN")

        state = _select_state(
            candidate=item,
            asset_count=asset_counts[asset_class],
            sector_count=sector_counts[sector],
            source_manifest=source_manifest,
        )

        record = create_paper_exposure_record(
            exposure_record_id="exposure-" + candidate_id,
            candidate_id=candidate_id,
            symbol=symbol,
            asset_class=asset_class,
            sector=sector,
            theme=theme,
            paper_exposure_state=state,
            review_reason="paper portfolio exposure review only",
            created_at_utc=str(item.get("created_at_utc") or "2026-07-06T00:00:00+00:00"),
        )
        exposure_records.append(record)

    validation_results = [validate_paper_exposure_record(record) for record in exposure_records]
    invalid_count = sum(1 for item in validation_results if not item["valid"])

    state_counts = Counter(record["paper_exposure_state"] for record in exposure_records)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "model_version": MODEL_VERSION,
        "candidate_count": len(candidate_list),
        "symbol_count": len({record["symbol"] for record in exposure_records}),
        "asset_class_counts": dict(asset_counts),
        "sector_counts": dict(sector_counts),
        "theme_counts": dict(theme_counts),
        "state_counts": dict(state_counts),
        "exposure_records": exposure_records,
        "exposure_validation_results": validation_results,
        "invalid_exposure_record_count": invalid_count,
        "source_manifest_id": source_manifest.get("stage_id", "PORTFOLIO-REVIEW-D2"),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "position_management_allowed": False,
        "position_size_suggestion_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "portfolio_rebalance_allowed": False,
        "trade_action_allowed": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
    }


def validate_paper_portfolio_review(review: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(review)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("candidate_count") != len(candidate.get("exposure_records", [])):
        issues.append("candidate_count must match exposure_records")

    if candidate.get("invalid_exposure_record_count") != 0:
        issues.append("invalid_exposure_record_count must be zero")

    for true_key in ["operator_review_required", "paper_only", "local_only", "read_only", "sidecar_only"]:
        if candidate.get(true_key) is not True:
            issues.append(true_key + " must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "position_management_allowed",
        "position_size_suggestion_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "portfolio_rebalance_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
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
