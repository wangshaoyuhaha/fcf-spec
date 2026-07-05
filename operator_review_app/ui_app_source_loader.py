"""Loader for UI-APP-1 local read-only report artifacts and workflow handoff."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .paper_review_contract import build_paper_review_contract, validate_paper_review_contract


ALLOWED_UI_SOURCE_TYPES = {
    "ui_app_local_report_artifact",
    "ui_app_workflow_handoff",
}


@dataclass(frozen=True)
class UiAppSourcePayload:
    """Read-only UI-APP source payload for operator review."""

    source_type: str
    source_path: str
    source_exists: bool
    payload: dict[str, Any]
    load_errors: tuple[str, ...]
    paper_only: bool = True
    read_only: bool = True
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["load_errors"] = list(self.load_errors)
        return data


def _load_json_file(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"source file does not exist: {path}"]
    if not path.is_file():
        return {}, [f"source path is not a file: {path}"]

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"invalid json: {exc}"]

    if not isinstance(loaded, dict):
        return {}, ["json payload must be an object"]

    return loaded, []


def load_ui_app_source_payload(
    source_path: str | Path,
    *,
    source_type: str,
) -> UiAppSourcePayload:
    """Load a UI-APP-1 source payload without mutation or execution."""

    errors: list[str] = []

    contract = build_paper_review_contract()
    contract_errors = validate_paper_review_contract(contract)
    errors.extend(contract_errors)

    if source_type not in ALLOWED_UI_SOURCE_TYPES:
        errors.append(f"source_type is not allowed: {source_type}")

    path = Path(source_path)
    payload, load_errors = _load_json_file(path)
    errors.extend(load_errors)

    return UiAppSourcePayload(
        source_type=source_type,
        source_path=str(path),
        source_exists=path.exists() and path.is_file(),
        payload=payload,
        load_errors=tuple(errors),
    )


def summarize_ui_app_source_payload(source: UiAppSourcePayload) -> dict[str, Any]:
    """Return a compact read-only summary for later operator review stages."""

    payload = source.payload

    return {
        "source_type": source.source_type,
        "source_path": source.source_path,
        "source_exists": source.source_exists,
        "load_error_count": len(source.load_errors),
        "paper_only": source.paper_only,
        "read_only": source.read_only,
        "trade_action_enabled": source.trade_action_enabled,
        "real_execution_allowed": source.real_execution_allowed,
        "source_report_id": payload.get("report_id") or payload.get("source_report_id") or "",
        "source_stage_id": payload.get("stage_id") or payload.get("source_stage_id") or "",
        "candidate_count": payload.get("candidate_count", 0),
        "has_ranked_watchlist": "ranked_watchlist" in payload,
        "has_risk_flags": "risk_flags" in payload,
        "has_reason_codes": "reason_codes" in payload,
        "operator_review_required": payload.get("operator_review_required", True),
    }
