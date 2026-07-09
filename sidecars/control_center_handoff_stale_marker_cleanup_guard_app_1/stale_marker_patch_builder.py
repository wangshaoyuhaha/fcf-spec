"""Patch builder for stale handoff marker cleanup.

This module is paper-only, local-only, and sidecar-only.
It builds a patch packet only. It does not apply patches or mutate files.
"""

from __future__ import annotations

from dataclasses import dataclass

from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_cleanup_plan import (
    CURRENT_STATE_REPLACEMENT_TEXT,
    PRESERVE_HISTORY,
    REPLACE_WITH_CURRENT_STATE,
    CleanupPlan,
)


PATCH_REPLACE_WITH_CURRENT_STATE = "PATCH_REPLACE_WITH_CURRENT_STATE"
PATCH_PRESERVE_HISTORY = "PATCH_PRESERVE_HISTORY"


@dataclass(frozen=True)
class CleanupPatchItem:
    source_path: str
    line_number: int
    patch_action: str
    original_line_text: str
    replacement_text: str
    review_required: bool


@dataclass(frozen=True)
class CleanupPatchPacket:
    patch_items: tuple[CleanupPatchItem, ...]
    total_plan_items: int
    replace_patch_count: int
    preserve_patch_count: int
    patch_applied: bool
    files_mutated: bool
    operator_review_required: bool
    safety_boundary_preserved: bool


def build_cleanup_patch_packet(plan: CleanupPlan) -> CleanupPatchPacket:
    patch_items: list[CleanupPatchItem] = []

    for item in plan.items:
        if item.planned_action == REPLACE_WITH_CURRENT_STATE:
            patch_items.append(
                CleanupPatchItem(
                    source_path=item.source_path,
                    line_number=item.line_number,
                    patch_action=PATCH_REPLACE_WITH_CURRENT_STATE,
                    original_line_text=item.original_line_text,
                    replacement_text=CURRENT_STATE_REPLACEMENT_TEXT,
                    review_required=True,
                )
            )
        elif item.planned_action == PRESERVE_HISTORY:
            patch_items.append(
                CleanupPatchItem(
                    source_path=item.source_path,
                    line_number=item.line_number,
                    patch_action=PATCH_PRESERVE_HISTORY,
                    original_line_text=item.original_line_text,
                    replacement_text="",
                    review_required=False,
                )
            )

    replace_patch_count = sum(
        1 for item in patch_items if item.patch_action == PATCH_REPLACE_WITH_CURRENT_STATE
    )
    preserve_patch_count = sum(
        1 for item in patch_items if item.patch_action == PATCH_PRESERVE_HISTORY
    )

    return CleanupPatchPacket(
        patch_items=tuple(patch_items),
        total_plan_items=len(plan.items),
        replace_patch_count=replace_patch_count,
        preserve_patch_count=preserve_patch_count,
        patch_applied=False,
        files_mutated=False,
        operator_review_required=replace_patch_count > 0,
        safety_boundary_preserved=True,
    )


def patch_packet_preserves_visibility(packet: CleanupPatchPacket) -> bool:
    return len(packet.patch_items) == packet.total_plan_items


def patch_packet_is_not_applied(packet: CleanupPatchPacket) -> bool:
    return packet.patch_applied is False and packet.files_mutated is False


def patch_packet_requires_review(packet: CleanupPatchPacket) -> bool:
    return packet.operator_review_required is True


def patch_packet_preserves_safety_boundary(packet: CleanupPatchPacket) -> bool:
    return packet.safety_boundary_preserved is True and packet.files_mutated is False
