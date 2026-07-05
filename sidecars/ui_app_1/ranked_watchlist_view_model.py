"""UI-APP-D3 ranked watchlist view model.

This module converts a ranked watchlist payload into a read-only UI model.
It does not create trade actions, execution actions, or core mutations.
"""

from __future__ import annotations

from typing import Any, Mapping


REQUIRED_CANDIDATE_FIELDS: tuple[str, ...] = (
    "symbol",
    "rank",
    "score_breakdown",
    "reason_codes",
    "risk_flags",
)

FORBIDDEN_ACTION_FIELDS: tuple[str, ...] = (
    "buy_button",
    "sell_button",
    "order_button",
    "trade_button",
    "broker_action",
    "exchange_action",
    "execution_action",
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _candidate_score(candidate: Mapping[str, Any]) -> float | None:
    direct_score = _safe_float(candidate.get("score"))
    if direct_score is not None:
        return direct_score

    score_breakdown = candidate.get("score_breakdown", {})
    if not isinstance(score_breakdown, Mapping):
        return None

    numeric_values = [
        _safe_float(value)
        for value in score_breakdown.values()
        if _safe_float(value) is not None
    ]
    if not numeric_values:
        return None
    return round(sum(numeric_values), 6)


def build_ranked_watchlist_view_model(
    handoff_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a read-only UI view model from an AI-CONTEXT handoff payload."""

    ranked_watchlist = handoff_payload.get("ranked_watchlist", [])
    if not isinstance(ranked_watchlist, list):
        ranked_watchlist = []

    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(ranked_watchlist, start=1):
        if not isinstance(candidate, Mapping):
            continue

        reason_codes = [str(item) for item in _as_list(candidate.get("reason_codes"))]
        risk_flags = [str(item) for item in _as_list(candidate.get("risk_flags"))]

        row = {
            "row_id": f"candidate-{index}",
            "rank": candidate.get("rank", index),
            "symbol": str(candidate.get("symbol", "")),
            "display_name": str(candidate.get("display_name", candidate.get("name", ""))),
            "score": _candidate_score(candidate),
            "score_breakdown": dict(candidate.get("score_breakdown", {}))
            if isinstance(candidate.get("score_breakdown", {}), Mapping)
            else {},
            "reason_codes": reason_codes,
            "risk_flags": risk_flags,
            "data_quality_state": candidate.get("data_quality_state", "UNKNOWN"),
            "confidence_level": candidate.get("confidence_level", "UNKNOWN"),
            "operator_review_required": True,
            "trade_action_enabled": False,
            "buy_button_enabled": False,
            "sell_button_enabled": False,
            "order_button_enabled": False,
            "detail_panel_enabled": True,
        }
        rows.append(row)

    return {
        "view_model_id": "ui_app_1_ranked_watchlist_view_model",
        "stage_id": "UI-APP-D3",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "trade_action_enabled": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "columns": (
            "rank",
            "symbol",
            "display_name",
            "score",
            "data_quality_state",
            "confidence_level",
            "reason_codes",
            "risk_flags",
            "operator_review_required",
        ),
        "rows": rows,
        "row_count": len(rows),
        "empty_state": "NO_RANKED_WATCHLIST_CANDIDATES" if not rows else "",
    }


def validate_ranked_watchlist_view_model(
    view_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the read-only ranked watchlist view model."""

    errors: list[str] = []

    must_be_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for field in must_be_true:
        if view_model.get(field) is not True:
            errors.append(f"expected_true:{field}")

    must_be_false = (
        "operator_review_bypass_allowed",
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
    )
    for field in must_be_false:
        if view_model.get(field) is not False:
            errors.append(f"expected_false:{field}")

    rows = view_model.get("rows", [])
    if not isinstance(rows, list):
        errors.append("rows_must_be_list")
        rows = []

    if view_model.get("row_count") != len(rows):
        errors.append("row_count_mismatch")

    for row_index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            errors.append(f"row_not_object:{row_index}")
            continue

        for field in REQUIRED_CANDIDATE_FIELDS:
            if field not in row:
                errors.append(f"missing_row_field:{row_index}:{field}")

        for field in FORBIDDEN_ACTION_FIELDS:
            if row.get(field) is True:
                errors.append(f"forbidden_row_action:{row_index}:{field}")

        if row.get("operator_review_required") is not True:
            errors.append(f"row_operator_review_not_required:{row_index}")

        if row.get("buy_button_enabled") is not False:
            errors.append(f"row_buy_button_enabled:{row_index}")

        if row.get("sell_button_enabled") is not False:
            errors.append(f"row_sell_button_enabled:{row_index}")

        if row.get("order_button_enabled") is not False:
            errors.append(f"row_order_button_enabled:{row_index}")

    return {
        "ok": not errors,
        "errors": errors,
        "row_count": len(rows),
        "view_model_id": view_model.get("view_model_id"),
        "stage_id": view_model.get("stage_id"),
    }


def summarize_ranked_watchlist_view_model(
    view_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a compact summary for report and workflow panels."""

    validation = validate_ranked_watchlist_view_model(view_model)
    rows = view_model.get("rows", [])
    if not isinstance(rows, list):
        rows = []

    risk_flag_count = 0
    reason_code_count = 0
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        risk_flag_count += len(_as_list(row.get("risk_flags")))
        reason_code_count += len(_as_list(row.get("reason_codes")))

    return {
        "ok": validation["ok"],
        "errors": validation["errors"],
        "row_count": len(rows),
        "risk_flag_count": risk_flag_count,
        "reason_code_count": reason_code_count,
        "operator_review_required": view_model.get("operator_review_required"),
        "trade_action_enabled": view_model.get("trade_action_enabled"),
        "buy_button_enabled": view_model.get("buy_button_enabled"),
        "sell_button_enabled": view_model.get("sell_button_enabled"),
        "order_button_enabled": view_model.get("order_button_enabled"),
    }
