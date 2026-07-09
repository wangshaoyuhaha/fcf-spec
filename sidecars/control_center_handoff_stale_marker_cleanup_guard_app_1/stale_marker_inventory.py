"""Inventory scanner for stale handoff markers.

This module is paper-only, local-only, read-only, and sidecar-only.
It detects stale marker candidates only.
It does not rewrite files, delete text, mutate core, tag, release, or deploy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXPECTED_FINAL_STATE_HISTORY = "EXPECTED_FINAL_STATE_HISTORY"
ACTIONABLE_STALE_STATE = "ACTIONABLE_STALE_STATE"

TARGET_HANDOFF_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
    "docs/HANDOFF_PROMPT.md",
)

CURRENT_TRUTH_MARKERS = (
    "8c18573",
    "ad16c03",
    "42ffeef",
    "1884 passed",
    "Completed Phase: CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1",
)

STALE_MARKER_PATTERNS = {
    "APPROVED_BUT_NOT_STARTED": ("Approved but not started", "approved but not started"),
    "APPROVED_NEXT_PHASE": ("APPROVED NEXT PHASE", "Approved next phase", "approved next phase"),
    "BEGIN_WITH_D1": ("Begin with D1", "begin with D1", "start D1"),
    "CREATE_SIDECAR_BRANCH": ("Create sidecar branch", "create sidecar branch"),
    "OLD_VALIDATION_COUNT": (
        "1505 passed",
        "1836 passed",
        "1842 passed",
        "1852 passed",
        "1860 passed",
        "1868 passed",
        "1876 passed",
    ),
    "OLD_NEXT_PHASE_CANDIDATE": (
        "UI-RISK-FLAG-VISIBILITY-APP-1",
        "next large sidecar candidate",
        "next phase order preserved",
    ),
}

HISTORICAL_CONTEXT_MARKERS = (
    "Completed Phase:",
    "previous completed phase",
    "historical",
    "history",
    "Archived",
    "archive",
    "final current-state",
    "final closeout",
    "historical closeout",
    "historical record",
)

CURRENT_ENTRY_CONTEXT_MARKERS = (
    "Next action:",
    "Current next:",
    "Current action:",
)


@dataclass(frozen=True)
class StaleMarkerHit:
    source_path: str
    line_number: int
    line_text: str
    marker_family: str
    classification_label: str
    review_required: bool


@dataclass(frozen=True)
class StaleMarkerInventory:
    hits: tuple[StaleMarkerHit, ...]
    total_hit_count: int
    expected_history_count: int
    actionable_stale_count: int
    target_scope_preserved: bool
    current_truth_present: bool
    cleanup_performed: bool


def is_target_handoff_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized in TARGET_HANDOFF_PATHS


def _line_has_any(line: str, patterns: Iterable[str]) -> bool:
    lowered = line.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def _detect_marker_family(line: str) -> str | None:
    for family, patterns in STALE_MARKER_PATTERNS.items():
        if _line_has_any(line, patterns):
            return family
    return None


def _classify_line(before_context: str, after_context: str) -> str:
    if _line_has_any(before_context, CURRENT_ENTRY_CONTEXT_MARKERS):
        return ACTIONABLE_STALE_STATE
    if _line_has_any(before_context + "\n" + after_context, HISTORICAL_CONTEXT_MARKERS):
        return EXPECTED_FINAL_STATE_HISTORY
    return ACTIONABLE_STALE_STATE


def scan_text_for_stale_markers(source_path: str, text: str) -> tuple[StaleMarkerHit, ...]:
    if not is_target_handoff_path(source_path):
        return tuple()

    lines = text.splitlines()
    hits: list[StaleMarkerHit] = []

    for index, line in enumerate(lines, start=1):
        family = _detect_marker_family(line)
        if family is None:
            continue

        before_start = max(0, index - 4)
        before_context = "\n".join(lines[before_start:index - 1])
        after_end = min(len(lines), index + 3)
        after_context = "\n".join(lines[index:after_end])

        label = _classify_line(before_context, after_context)

        hits.append(
            StaleMarkerHit(
                source_path=source_path,
                line_number=index,
                line_text=line,
                marker_family=family,
                classification_label=label,
                review_required=label == ACTIONABLE_STALE_STATE,
            )
        )

    return tuple(hits)


def current_truth_present(text_by_path: dict[str, str]) -> bool:
    combined = "\n".join(text_by_path.values())
    return all(marker in combined for marker in CURRENT_TRUTH_MARKERS)


def build_stale_marker_inventory(text_by_path: dict[str, str]) -> StaleMarkerInventory:
    hits: list[StaleMarkerHit] = []

    for path, text in text_by_path.items():
        hits.extend(scan_text_for_stale_markers(path, text))

    expected_history_count = sum(
        1 for hit in hits if hit.classification_label == EXPECTED_FINAL_STATE_HISTORY
    )
    actionable_stale_count = sum(
        1 for hit in hits if hit.classification_label == ACTIONABLE_STALE_STATE
    )

    return StaleMarkerInventory(
        hits=tuple(hits),
        total_hit_count=len(hits),
        expected_history_count=expected_history_count,
        actionable_stale_count=actionable_stale_count,
        target_scope_preserved=all(is_target_handoff_path(path) for path in text_by_path),
        current_truth_present=current_truth_present(text_by_path),
        cleanup_performed=False,
    )


def read_target_handoff_files(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative_path in TARGET_HANDOFF_PATHS:
        path = root / relative_path
        if path.exists():
            result[relative_path] = path.read_text(encoding="utf-8")
    return result


def inventory_requires_cleanup(inventory: StaleMarkerInventory) -> bool:
    return inventory.actionable_stale_count > 0


def inventory_preserves_read_only_boundary(inventory: StaleMarkerInventory) -> bool:
    return inventory.cleanup_performed is False and inventory.target_scope_preserved is True
