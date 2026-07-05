"""UI-APP-D4 risk, reason, and operator review panels.

This module renders read-only panel models from the ranked watchlist view model
and AI-CONTEXT handoff payload. It never creates trade actions.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


PANEL_SAFETY_FIELDS: dict[str, Any] = {
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
}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _rows_from_view_model(view_model: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = view_model.get("rows", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, Mapping)]


def _counter_entries(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"code": code, "count": count}
        for code, count in sorted(counter.items())
    ]


def build_reason_codes_panel(
    view_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a read-only reason codes panel."""

    rows = _rows_from_view_model(view_model)
    counter: Counter[str] = Counter()
    candidate_map: dict[str, list[str]] = {}

    for row in rows:
        symbol = str(row.get("symbol", ""))
        codes = [str(item) for item in _as_list(row.get("reason_codes"))]
        candidate_map[symbol] = codes
        counter.update(codes)

    return {
        "panel_id": "reason_codes_panel",
        "stage_id": "UI-APP-D4",
        **PANEL_SAFETY_FIELDS,
        "title": "Reason Codes",
        "description": "Read-only reason code summary from upstream sidecars.",
        "total_reason_code_count": sum(counter.values()),
        "unique_reason_code_count": len(counter),
        "reason_code_counts": _counter_entries(counter),
        "candidate_reason_codes": candidate_map,
        "empty_state": "NO_REASON_CODES" if not counter else "",
    }


def build_risk_flags_panel(
    view_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a read-only risk flags panel."""

    rows = _rows_from_view_model(view_model)
    counter: Counter[str] = Counter()
    candidate_map: dict[str, list[str]] = {}

    for row in rows:
        symbol = str(row.get("symbol", ""))
        flags = [str(item) for item in _as_list(row.get("risk_flags"))]
        candidate_map[symbol] = flags
        counter.update(flags)

    high_attention_flags = [
        item
        for item in sorted(counter)
        if item in {
            "LOW_CONFIDENCE",
            "OPERATOR_REVIEW_REQUIRED",
            "DATA_QUALITY_LIMITED",
            "QUARANTINE_REVIEW_REQUIRED",
            "MISSING_REASON_CODES",
        }
    ]

    return {
        "panel_id": "risk_flags_panel",
        "stage_id": "UI-APP-D4",
        **PANEL_SAFETY_FIELDS,
        "title": "Risk Flags",
        "description": "Read-only risk flag summary for operator review.",
        "total_risk_flag_count": sum(counter.values()),
        "unique_risk_flag_count": len(counter),
        "risk_flag_counts": _counter_entries(counter),
        "high_attention_flags": high_attention_flags,
        "candidate_risk_flags": candidate_map,
        "empty_state": "NO_RISK_FLAGS" if not counter else "",
    }


def build_operator_review_panel(
    handoff_payload: Mapping[str, Any],
    view_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a read-only operator review panel."""

    rows = _rows_from_view_model(view_model)
    summary = handoff_payload.get("operator_review_summary", {})
    if not isinstance(summary, Mapping):
        summary = {}

    pending_symbols: list[str] = []
    for row in rows:
        if row.get("operator_review_required") is True:
            pending_symbols.append(str(row.get("symbol", "")))

    return {
        "panel_id": "operator_review_summary_panel",
        "stage_id": "UI-APP-D4",
        **PANEL_SAFETY_FIELDS,
        "title": "Operator Review Summary",
        "description": "Paper-only local operator review status.",
        "review_status": str(summary.get("status", "PENDING_OPERATOR_REVIEW")),
        "review_required": True,
        "review_bypass_allowed": False,
        "candidate_count": len(rows),
        "pending_review_count": len(pending_symbols),
        "pending_review_symbols": pending_symbols,
        "upstream_summary": dict(summary),
        "allowed_operator_actions": (
            "read_report",
            "inspect_reason_codes",
            "inspect_risk_flags",
            "record_paper_review_status",
        ),
        "forbidden_operator_actions": (
            "buy",
            "sell",
            "place_order",
            "connect_broker",
            "connect_exchange",
            "bypass_review",
        ),
    }


def build_risk_reason_review_panels(
    handoff_payload: Mapping[str, Any],
    ranked_watchlist_view_model: Mapping[str, Any],
) -> dict[str, Any]:
    """Build all UI-APP-D4 read-only panels."""

    reason_panel = build_reason_codes_panel(ranked_watchlist_view_model)
    risk_panel = build_risk_flags_panel(ranked_watchlist_view_model)
    review_panel = build_operator_review_panel(
        handoff_payload,
        ranked_watchlist_view_model,
    )

    panels = {
        "reason_codes_panel": reason_panel,
        "risk_flags_panel": risk_panel,
        "operator_review_summary_panel": review_panel,
    }

    return {
        "panel_group_id": "ui_app_1_risk_reason_review_panels",
        "stage_id": "UI-APP-D4",
        **PANEL_SAFETY_FIELDS,
        "panels": panels,
        "panel_count": len(panels),
    }


def validate_risk_reason_review_panels(
    panel_group: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate UI-APP-D4 read-only panel safety."""

    errors: list[str] = []

    must_be_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for field in must_be_true:
        if panel_group.get(field) is not True:
            errors.append(f"expected_true:{field}")

    must_be_false = (
        "operator_review_bypass_allowed",
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
    )
    for field in must_be_false:
        if panel_group.get(field) is not False:
            errors.append(f"expected_false:{field}")

    panels = panel_group.get("panels", {})
    if not isinstance(panels, Mapping):
        errors.append("panels_must_be_object")
        panels = {}

    expected_panels = {
        "reason_codes_panel",
        "risk_flags_panel",
        "operator_review_summary_panel",
    }
    if set(panels.keys()) != expected_panels:
        errors.append("panel_keys_mismatch")

    for panel_name, panel in panels.items():
        if not isinstance(panel, Mapping):
            errors.append(f"panel_not_object:{panel_name}")
            continue

        for field in must_be_true:
            if panel.get(field) is not True:
                errors.append(f"panel_expected_true:{panel_name}:{field}")

        for field in must_be_false:
            if panel.get(field) is not False:
                errors.append(f"panel_expected_false:{panel_name}:{field}")

        if panel.get("panel_id") != panel_name:
            errors.append(f"panel_id_mismatch:{panel_name}")

    if panel_group.get("panel_count") != len(panels):
        errors.append("panel_count_mismatch")

    return {
        "ok": not errors,
        "errors": errors,
        "panel_count": len(panels),
        "stage_id": panel_group.get("stage_id"),
    }
