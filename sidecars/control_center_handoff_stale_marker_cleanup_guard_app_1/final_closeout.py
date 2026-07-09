"""Final closeout for handoff stale marker cleanup guard.

This module is paper-only, local-only, read-only, and sidecar-only.
It creates final closeout summaries only.
"""

from __future__ import annotations

from dataclasses import dataclass

from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.controlled_handoff_cleanup import (
    CURRENT_TRUTH_HEADER,
    CURRENT_TRUTH_HEADER_TITLE,
    TARGET_HANDOFF_PATHS,
    has_current_truth_header,
    safety_boundary_present,
)


PHASE_ID = "CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1"

COMPLETED_STAGE_IDS = (
    "D1_HANDOFF_STALE_MARKER_CLEANUP_CONTRACT",
    "D2_STALE_MARKER_INVENTORY_SCANNER",
    "D3_STALE_MARKER_CLEANUP_PLAN",
    "D4_STALE_MARKER_CLEANUP_PATCH_BUILDER",
    "D5_CONTROLLED_HANDOFF_CLEANUP_APPLY",
    "D6_FINAL_CLOSEOUT",
)


@dataclass(frozen=True)
class HandoffCleanupFinalCloseout:
    phase_id: str
    completed_stage_ids: tuple[str, ...]
    target_handoff_paths: tuple[str, ...]
    current_truth_header_title: str
    current_truth_header_present: bool
    stale_markers_marked_historical: bool
    current_truth_commits_present: bool
    validation_truth_present: bool
    safety_boundary_preserved: bool
    paper_only: bool
    local_only: bool
    read_only: bool
    sidecar_only: bool
    operator_review_required: bool
    p48_allowed: bool
    core_mutation_allowed: bool
    runtime_mutation_allowed: bool
    real_trading_allowed: bool
    broker_api_allowed: bool
    exchange_api_allowed: bool
    api_key_allowed: bool
    wallet_private_key_allowed: bool
    buy_sell_order_allowed: bool
    tag_release_deploy_allowed: bool


def build_final_closeout() -> HandoffCleanupFinalCloseout:
    return HandoffCleanupFinalCloseout(
        phase_id=PHASE_ID,
        completed_stage_ids=COMPLETED_STAGE_IDS,
        target_handoff_paths=TARGET_HANDOFF_PATHS,
        current_truth_header_title=CURRENT_TRUTH_HEADER_TITLE,
        current_truth_header_present=has_current_truth_header(CURRENT_TRUTH_HEADER),
        stale_markers_marked_historical="historical unless explicitly re-approved" in CURRENT_TRUTH_HEADER,
        current_truth_commits_present=all(
            item in CURRENT_TRUTH_HEADER for item in ("ad16c03", "8c18573")
        ),
        validation_truth_present="1884 passed" in CURRENT_TRUTH_HEADER,
        safety_boundary_preserved=safety_boundary_present(CURRENT_TRUTH_HEADER),
        paper_only=True,
        local_only=True,
        read_only=True,
        sidecar_only=True,
        operator_review_required=True,
        p48_allowed=False,
        core_mutation_allowed=False,
        runtime_mutation_allowed=False,
        real_trading_allowed=False,
        broker_api_allowed=False,
        exchange_api_allowed=False,
        api_key_allowed=False,
        wallet_private_key_allowed=False,
        buy_sell_order_allowed=False,
        tag_release_deploy_allowed=False,
    )


def final_closeout_preserves_safety_boundary(closeout: HandoffCleanupFinalCloseout) -> bool:
    return (
        closeout.safety_boundary_preserved is True
        and closeout.paper_only is True
        and closeout.local_only is True
        and closeout.read_only is True
        and closeout.sidecar_only is True
        and closeout.operator_review_required is True
        and closeout.p48_allowed is False
        and closeout.core_mutation_allowed is False
        and closeout.runtime_mutation_allowed is False
        and closeout.real_trading_allowed is False
        and closeout.broker_api_allowed is False
        and closeout.exchange_api_allowed is False
        and closeout.api_key_allowed is False
        and closeout.wallet_private_key_allowed is False
        and closeout.buy_sell_order_allowed is False
        and closeout.tag_release_deploy_allowed is False
    )


def final_closeout_ready_for_merge_review(closeout: HandoffCleanupFinalCloseout) -> bool:
    return (
        closeout.phase_id == PHASE_ID
        and closeout.completed_stage_ids == COMPLETED_STAGE_IDS
        and closeout.current_truth_header_present is True
        and closeout.stale_markers_marked_historical is True
        and closeout.current_truth_commits_present is True
        and closeout.validation_truth_present is True
        and final_closeout_preserves_safety_boundary(closeout) is True
    )
