from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ACTIVE_AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)


@dataclass(frozen=True)
class AuthorityBaseline:
    phase_id: str
    main_merge_commit: str
    d6_commit: str
    final_marker: str


@dataclass(frozen=True)
class AuthoritySourceState:
    relative_path: str
    exists: bool
    has_phase: bool
    has_main_merge: bool
    has_d6: bool
    has_final_marker: bool


@dataclass(frozen=True)
class AuthoritySyncReport:
    status: str
    source_count: int
    blocked_paths: tuple[str, ...]
    reason_codes: tuple[str, ...]


def inspect_authority_source(
    root: str | Path,
    relative_path: str,
    baseline: AuthorityBaseline,
) -> AuthoritySourceState:
    target = Path(root) / relative_path
    if not target.is_file():
        return AuthoritySourceState(
            relative_path=relative_path,
            exists=False,
            has_phase=False,
            has_main_merge=False,
            has_d6=False,
            has_final_marker=False,
        )

    text = target.read_text(encoding="utf-8")
    return AuthoritySourceState(
        relative_path=relative_path,
        exists=True,
        has_phase=baseline.phase_id in text,
        has_main_merge=baseline.main_merge_commit in text,
        has_d6=baseline.d6_commit in text,
        has_final_marker=baseline.final_marker in text,
    )


def inspect_active_authority(
    root: str | Path,
    baseline: AuthorityBaseline,
) -> tuple[AuthoritySourceState, ...]:
    return tuple(
        inspect_authority_source(root, path, baseline)
        for path in ACTIVE_AUTHORITY_PATHS
    )


def build_authority_sync_report(
    states: Iterable[AuthoritySourceState],
) -> AuthoritySyncReport:
    records = tuple(states)
    blocked_paths: list[str] = []
    reason_codes: list[str] = []

    for state in records:
        reasons: list[str] = []
        if not state.exists:
            reasons.append("MISSING_AUTHORITY_SOURCE")
        if state.exists and not state.has_phase:
            reasons.append("MISSING_LATEST_PHASE")
        if state.exists and not state.has_main_merge:
            reasons.append("MISSING_MAIN_MERGE")
        if state.exists and not state.has_d6:
            reasons.append("MISSING_D6")
        if state.exists and not state.has_final_marker:
            reasons.append("MISSING_FINAL_MARKER")
        if reasons:
            blocked_paths.append(state.relative_path)
            reason_codes.extend(reasons)

    return AuthoritySyncReport(
        status="PASS" if not blocked_paths else "BLOCKED",
        source_count=len(records),
        blocked_paths=tuple(blocked_paths),
        reason_codes=tuple(dict.fromkeys(reason_codes)),
    )


def assert_authority_sync_pass(report: AuthoritySyncReport) -> None:
    if report.status != "PASS":
        paths = ",".join(report.blocked_paths)
        reasons = ",".join(report.reason_codes)
        raise ValueError(
            f"ACTIVE_AUTHORITY_SYNC_FAILED:paths={paths}:reasons={reasons}"
        )


def missing_final_state_pairs(
    root: str | Path,
    approved_paths: Iterable[str],
) -> tuple[str, ...]:
    repo_root = Path(root)
    missing: list[str] = []
    for approved in approved_paths:
        expected = approved.replace("_APPROVED.md", "_FINAL.md")
        if expected == approved or not (repo_root / expected).is_file():
            missing.append(expected)
    return tuple(sorted(missing))
