"""D1 contract for ARCHIVE-CORRELATION-ROLLUP-APP-1.

Boundary:
- sidecar-only
- read-only
- paper-only
- local-only
- index-only
- no core mutation
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

ARCHIVE_CORRELATION_ROLLUP_APP_ID = "ARCHIVE-CORRELATION-ROLLUP-APP-1"

CORRELATION_ROLLUP_REQUIRED_LINKS: Tuple[str, ...] = (
    "data_snapshot",
    "candidate",
    "ai_explanation",
    "ui_packet",
    "review_packet",
    "archive_packet",
    "handoff",
    "final_state",
)

ALLOWED_ROLLUP_STATUSES: Tuple[str, ...] = (
    "COMPLETE",
    "INCOMPLETE",
    "STALE",
    "UNRESOLVED",
)

_FORBIDDEN_ACTIONS: Tuple[str, ...] = (
    "core_mutation",
    "auto_pass",
    "auto_fill_correlation_id",
    "placeholder_review",
    "ui_dashboard_panel",
    "trade_execution",
    "broker_api",
    "exchange_api",
    "api_key",
    "wallet_private_key",
    "real_account",
    "real_position",
    "buy_sell_order",
    "auto_position",
    "auto_portfolio_action",
    "tag",
    "release",
    "deploy",
    "p48",
)


def build_correlation_rollup_contract() -> Dict[str, Any]:
    """Return immutable D1 sidecar boundary and rollup contract."""

    contract: Dict[str, Any] = {
        "app_id": ARCHIVE_CORRELATION_ROLLUP_APP_ID,
        "stage": "D1",
        "purpose": "upgrade correlation_id from field preservation to read-only full-chain evidence index",
        "mode": {
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "index_only": True,
            "operator_review_required": True,
        },
        "core_policy": {
            "core_frozen": True,
            "p1_p47_frozen": True,
            "p48_forbidden": True,
            "core_mutation_allowed": False,
            "sidecar_extension_only": True,
        },
        "rollup_contract": {
            "identifier": "correlation_id",
            "auto_fill_allowed": False,
            "missing_chain_policy": "mark_only",
            "allowed_statuses": list(ALLOWED_ROLLUP_STATUSES),
            "required_links": list(CORRELATION_ROLLUP_REQUIRED_LINKS),
            "evidence_backfill_allowed": False,
            "placeholder_review_allowed": False,
            "auto_pass_allowed": False,
        },
        "dependency_policy": {
            "single_direction": True,
            "reads_existing_artifacts_only": True,
            "writes_core": False,
            "writes_ui_dashboard": False,
            "creates_orders": False,
        },
        "forbidden_actions": list(_FORBIDDEN_ACTIONS),
    }

    return deepcopy(contract)
