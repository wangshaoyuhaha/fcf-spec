"""Cleanup plan builder for stale handoff markers.

This module is paper-only, local-only, and sidecar-only.
It builds a plan only. It does not mutate files.
"""

from __future__ import annotations

from dataclasses import dataclass

from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_inventory import (
    ACTIONABLE_STALE_STATE,
    EXPECTED_FINAL_STATE_HISTORY,
    StaleMarkerHit,
    StaleMarkerInventory,
)


REPLACE_WITH_CURRENT_STATE = "REPLACE_WITH_CURRENT_STATE"
MARK_AS_HISTORICAL = "MARK_AS_HISTORICAL"
PRESERVE_HISTORY = "PRESERVE_HISTORY"

CURRENT_STATE_REPLACEMENT_TEXT = """Current state:
CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed.
Main merge commit: ad16c03.
Final handoff sync commit: 8c18573.
Validation: python scripts/run_all_checks.py = ALL CHECKS PASSED; python -m pytest -q = 1884 passed.
Git status: clean.
origin/main: synced.
Next work requires explicit operator approval.
"""


@dataclass(frozen=True)
class CleanupPlanItem:
    source_path: str
    line_number: int
    marker_family: str
    original_line_text: str
    classification_label: str
    planned_action: str
    replacement_text: str
    review_required: bool


@dataclass(frozen=True)
class CleanupPlan:
    items: tuple[CleanupPlanItem, ...]
    total_inventory_hits: int
    cleanup_action_count: int
    preserved_history_count: int
    files_mutated: bool
    operator_review_required: bool
    safety_boundary_preserved: bool


def _planned_action_for_hit(hit: StaleMarkerHit) -> str:
    if hit.classification_label == ACTIONABLE_STALE_STATE:
        return REPLACE_WITH_CURRENT_STATE
    if hit.classification_label == EXPECTED_FINAL_STATE_HISTORY:
        return PRESERVE_HISTORY
    return MARK_AS_HISTORICAL


def build_cleanup_plan(inventory: StaleMarkerInventory) -> CleanupPlan:
    items: list[CleanupPlanItem] = []

    for hit in inventory.hits:
        action = _planned_action_for_hit(hit)

        if action == REPLACE_WITH_CURRENT_STATE:
            replacement = CURRENT_STATE_REPLACEMENT_TEXT
            review_required = True
        elif action == PRESERVE_HISTORY:
            replacement = ""
            review_required = False
        else:
            replacement = "Historical stale marker. Preserve as history."
            review_required = True

        items.append(
            CleanupPlanItem(
                source_path=hit.source_path,
                line_number=hit.line_number,
                marker_family=hit.marker_family,
                original_line_text=hit.line_text,
                classification_label=hit.classification_label,
                planned_action=action,
                replacement_text=replacement,
                review_required=review_required,
            )
        )

    cleanup_action_count = sum(
        1 for item in items if item.planned_action == REPLACE_WITH_CURRENT_STATE
    )
    preserved_history_count = sum(
        1 for item in items if item.planned_action == PRESERVE_HISTORY
    )

    return CleanupPlan(
        items=tuple(items),
        total_inventory_hits=inventory.total_hit_count,
        cleanup_action_count=cleanup_action_count,
        preserved_history_count=preserved_history_count,
        files_mutated=False,
        operator_review_required=cleanup_action_count > 0,
        safety_boundary_preserved=True,
    )


def cleanup_plan_preserves_history(plan: CleanupPlan) -> bool:
    return all(
        item.planned_action != REPLACE_WITH_CURRENT_STATE
        for item in plan.items
        if item.classification_label == EXPECTED_FINAL_STATE_HISTORY
    )


def cleanup_plan_requires_review(plan: CleanupPlan) -> bool:
    return plan.operator_review_required is True


def cleanup_plan_is_read_only(plan: CleanupPlan) -> bool:
    return plan.files_mutated is False and plan.safety_boundary_preserved is True
