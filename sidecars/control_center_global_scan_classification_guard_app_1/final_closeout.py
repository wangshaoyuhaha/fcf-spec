"""Final closeout for CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1.

This module is paper-only, local-only, read-only, and sidecar-only.
It creates final handoff summaries only and does not mutate core, runtime, source,
or handoff files.
"""

from __future__ import annotations

from dataclasses import dataclass

from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    RawScanHit,
)
from sidecars.control_center_global_scan_classification_guard_app_1.review_packet import (
    ClassificationReviewPacket,
    build_review_packet,
    review_packet_blocks_unsafe_permission,
    review_packet_preserves_visibility,
    review_packet_queue_size_matches_actionable_count,
)


PHASE_ID = "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1"

COMPLETED_STAGE_IDS = (
    "D1_GLOBAL_SCAN_CLASSIFICATION_CONTRACT",
    "D2_GLOBAL_SCAN_CLASSIFICATION_RULEBOOK",
    "D3_CLASSIFICATION_PACKET",
    "D4_ACTIONABLE_REVIEW_GATE",
    "D5_CLASSIFICATION_REVIEW_PACKET",
    "D6_FINAL_WORKFLOW_HANDOFF_AND_CLOSEOUT",
)


@dataclass(frozen=True)
class FinalCloseout:
    phase_id: str
    completed_stage_ids: tuple[str, ...]
    review_packet: ClassificationReviewPacket
    all_records_visible: bool
    actionable_queue_complete: bool
    unsafe_permission_blocked_until_review: bool
    paper_only: bool
    local_only: bool
    read_only: bool
    sidecar_only: bool
    operator_review_required: bool
    p48_core_expansion_allowed: bool
    core_mutation_allowed: bool
    source_mutation_allowed: bool
    runtime_mutation_allowed: bool
    handoff_mutation_allowed: bool
    real_trading_allowed: bool
    broker_api_allowed: bool
    exchange_api_allowed: bool
    api_key_allowed: bool
    wallet_private_key_allowed: bool
    buy_sell_order_allowed: bool
    tag_release_deploy_allowed: bool


def build_final_closeout(
    hits: tuple[RawScanHit, ...],
    *,
    packet_id: str,
) -> FinalCloseout:
    review_packet = build_review_packet(hits, packet_id=packet_id)

    unsafe_permission_blocked = (
        review_packet_blocks_unsafe_permission(review_packet)
        if review_packet.blocked_until_review
        else True
    )

    return FinalCloseout(
        phase_id=PHASE_ID,
        completed_stage_ids=COMPLETED_STAGE_IDS,
        review_packet=review_packet,
        all_records_visible=review_packet_preserves_visibility(review_packet),
        actionable_queue_complete=review_packet_queue_size_matches_actionable_count(
            review_packet
        ),
        unsafe_permission_blocked_until_review=unsafe_permission_blocked,
        paper_only=True,
        local_only=True,
        read_only=True,
        sidecar_only=True,
        operator_review_required=True,
        p48_core_expansion_allowed=False,
        core_mutation_allowed=False,
        source_mutation_allowed=False,
        runtime_mutation_allowed=False,
        handoff_mutation_allowed=False,
        real_trading_allowed=False,
        broker_api_allowed=False,
        exchange_api_allowed=False,
        api_key_allowed=False,
        wallet_private_key_allowed=False,
        buy_sell_order_allowed=False,
        tag_release_deploy_allowed=False,
    )


def final_closeout_preserves_safety_boundary(closeout: FinalCloseout) -> bool:
    return (
        closeout.paper_only is True
        and closeout.local_only is True
        and closeout.read_only is True
        and closeout.sidecar_only is True
        and closeout.operator_review_required is True
        and closeout.p48_core_expansion_allowed is False
        and closeout.core_mutation_allowed is False
        and closeout.source_mutation_allowed is False
        and closeout.runtime_mutation_allowed is False
        and closeout.handoff_mutation_allowed is False
        and closeout.real_trading_allowed is False
        and closeout.broker_api_allowed is False
        and closeout.exchange_api_allowed is False
        and closeout.api_key_allowed is False
        and closeout.wallet_private_key_allowed is False
        and closeout.buy_sell_order_allowed is False
        and closeout.tag_release_deploy_allowed is False
    )


def final_closeout_ready_for_operator_merge_review(closeout: FinalCloseout) -> bool:
    return (
        closeout.phase_id == PHASE_ID
        and closeout.completed_stage_ids == COMPLETED_STAGE_IDS
        and closeout.all_records_visible is True
        and closeout.actionable_queue_complete is True
        and closeout.unsafe_permission_blocked_until_review is True
        and final_closeout_preserves_safety_boundary(closeout) is True
    )
