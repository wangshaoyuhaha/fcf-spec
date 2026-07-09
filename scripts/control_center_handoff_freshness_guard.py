from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_SAFETY_TERMS = (
    "paper-only",
    "local-only",
    "read-only governance validation",
    "sidecar-only",
    "operator review required",
    "no P48",
    "no core mutation",
    "no real trading",
    "no broker API",
    "no exchange API",
    "no API key",
    "no buy button",
    "no sell button",
    "no order button",
    "no tag",
    "no release",
    "no deploy",
)


FORBIDDEN_STALE_RUNTIME_TERMS = (
    "broker integration",
    "exchange integration",
    "real order",
    "live order",
    "wallet key",
    "trading API",
)


PROTECTED_EXACT_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
    "docs/HANDOFF_PROMPT.md",
)


@dataclass(frozen=True)
class HandoffFreshnessBaseline:
    latest_main_commit: str
    latest_phase: str
    merge_commit: str
    d6_commit: str
    pytest_passed_count: int
    run_all_checks_passed: bool


@dataclass(frozen=True)
class HandoffFreshnessResult:
    passed: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class HandoffSourceRecord:
    relative_path: str
    text: str


def validate_handoff_freshness_contract(
    text: str,
    baseline: HandoffFreshnessBaseline,
    stale_commits: tuple[str, ...] = (),
    stale_phases: tuple[str, ...] = (),
    stale_pytest_counts: tuple[int, ...] = (),
) -> HandoffFreshnessResult:
    normalized = text.lower()
    reasons: list[str] = []

    required_values = (
        baseline.latest_main_commit,
        baseline.latest_phase,
        baseline.merge_commit,
        baseline.d6_commit,
        str(baseline.pytest_passed_count),
    )

    for value in required_values:
        if value.lower() not in normalized:
            reasons.append("MISSING_CURRENT_BASELINE_VALUE")

    if baseline.run_all_checks_passed and "run_all_checks" not in normalized:
        reasons.append("MISSING_RUN_ALL_CHECKS_REFERENCE")

    for term in REQUIRED_SAFETY_TERMS:
        if term.lower() not in normalized:
            reasons.append("MISSING_SAFETY_BOUNDARY")

    for commit in stale_commits:
        if commit and commit.lower() in normalized:
            reasons.append("STALE_COMMIT_REFERENCE")

    for phase in stale_phases:
        if phase and phase.lower() in normalized:
            reasons.append("STALE_PHASE_REFERENCE")

    for count in stale_pytest_counts:
        if str(count) in normalized and count != baseline.pytest_passed_count:
            reasons.append("STALE_PYTEST_COUNT_REFERENCE")

    for term in FORBIDDEN_STALE_RUNTIME_TERMS:
        if term.lower() in normalized:
            reasons.append("UNSAFE_RUNTIME_REFERENCE")

    return HandoffFreshnessResult(
        passed=not reasons,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def discover_handoff_source_paths(root: str | Path) -> tuple[Path, ...]:
    repo_root = Path(root)
    paths: list[Path] = []

    for relative in PROTECTED_EXACT_PATHS:
        candidate = repo_root / relative
        if candidate.exists() and candidate.is_file():
            paths.append(candidate)

    for candidate in sorted(repo_root.glob("FCF_CURRENT_STATE*.md")):
        if candidate.is_file():
            paths.append(candidate)

    unique: dict[str, Path] = {}
    for path in paths:
        key = path.relative_to(repo_root).as_posix()
        unique[key] = path

    return tuple(unique[key] for key in sorted(unique))


def load_handoff_sources(root: str | Path) -> tuple[HandoffSourceRecord, ...]:
    repo_root = Path(root)
    records: list[HandoffSourceRecord] = []

    for path in discover_handoff_source_paths(repo_root):
        records.append(
            HandoffSourceRecord(
                relative_path=path.relative_to(repo_root).as_posix(),
                text=path.read_text(encoding="utf-8"),
            )
        )

    return tuple(records)

import re


@dataclass(frozen=True)
class HandoffFreshnessSnapshot:
    relative_path: str
    commit_hashes: tuple[str, ...]
    pytest_counts: tuple[int, ...]
    phase_tokens: tuple[str, ...]
    text_length: int


_COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b", re.IGNORECASE)
_PYTEST_RE = re.compile(r"\b(\d{3,5})\s+passed\b", re.IGNORECASE)
_PHASE_RE = re.compile(r"\b[A-Z0-9]+(?:-[A-Z0-9]+)*-APP-1\b")


def extract_commit_hashes(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(match.group(0).lower() for match in _COMMIT_RE.finditer(text)))


def extract_pytest_counts(text: str) -> tuple[int, ...]:
    return tuple(dict.fromkeys(int(match.group(1)) for match in _PYTEST_RE.finditer(text)))


def extract_phase_tokens(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(match.group(0) for match in _PHASE_RE.finditer(text)))


def build_handoff_freshness_snapshot(record: HandoffSourceRecord) -> HandoffFreshnessSnapshot:
    return HandoffFreshnessSnapshot(
        relative_path=record.relative_path,
        commit_hashes=extract_commit_hashes(record.text),
        pytest_counts=extract_pytest_counts(record.text),
        phase_tokens=extract_phase_tokens(record.text),
        text_length=len(record.text),
    )


def build_handoff_freshness_snapshots(
    records: tuple[HandoffSourceRecord, ...],
) -> tuple[HandoffFreshnessSnapshot, ...]:
    return tuple(build_handoff_freshness_snapshot(record) for record in records)


@dataclass(frozen=True)
class HandoffDriftRecord:
    relative_path: str
    reason_codes: tuple[str, ...]


def detect_handoff_freshness_drift(
    snapshot: HandoffFreshnessSnapshot,
    baseline: HandoffFreshnessBaseline,
    stale_commits: tuple[str, ...] = (),
    stale_phases: tuple[str, ...] = (),
    stale_pytest_counts: tuple[int, ...] = (),
) -> HandoffDriftRecord:
    reasons: list[str] = []

    if baseline.latest_main_commit.lower() not in snapshot.commit_hashes:
        reasons.append("MISSING_LATEST_MAIN_COMMIT")

    if baseline.merge_commit.lower() not in snapshot.commit_hashes:
        reasons.append("MISSING_LATEST_MERGE_COMMIT")

    if baseline.d6_commit.lower() not in snapshot.commit_hashes:
        reasons.append("MISSING_LATEST_D6_COMMIT")

    if baseline.latest_phase not in snapshot.phase_tokens:
        reasons.append("MISSING_LATEST_PHASE")

    if baseline.pytest_passed_count not in snapshot.pytest_counts:
        reasons.append("MISSING_LATEST_PYTEST_COUNT")

    for commit in stale_commits:
        if commit.lower() in snapshot.commit_hashes:
            reasons.append("STALE_COMMIT_REFERENCE")

    for phase in stale_phases:
        if phase in snapshot.phase_tokens:
            reasons.append("STALE_PHASE_REFERENCE")

    for count in stale_pytest_counts:
        if count in snapshot.pytest_counts and count != baseline.pytest_passed_count:
            reasons.append("STALE_PYTEST_COUNT_REFERENCE")

    return HandoffDriftRecord(
        relative_path=snapshot.relative_path,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def detect_handoff_freshness_drifts(
    snapshots: tuple[HandoffFreshnessSnapshot, ...],
    baseline: HandoffFreshnessBaseline,
    stale_commits: tuple[str, ...] = (),
    stale_phases: tuple[str, ...] = (),
    stale_pytest_counts: tuple[int, ...] = (),
) -> tuple[HandoffDriftRecord, ...]:
    return tuple(
        detect_handoff_freshness_drift(
            snapshot=snapshot,
            baseline=baseline,
            stale_commits=stale_commits,
            stale_phases=stale_phases,
            stale_pytest_counts=stale_pytest_counts,
        )
        for snapshot in snapshots
    )


@dataclass(frozen=True)
class HandoffFreshnessGuardPacket:
    app_id: str
    total_sources: int
    blocked_sources: int
    passed: bool
    reason_codes: tuple[str, ...]
    blocked_paths: tuple[str, ...]


def build_handoff_freshness_guard_packet(
    drifts: tuple[HandoffDriftRecord, ...],
    app_id: str = "CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1",
) -> HandoffFreshnessGuardPacket:
    blocked = tuple(drift for drift in drifts if drift.reason_codes)

    reason_codes: list[str] = []
    blocked_paths: list[str] = []

    for drift in blocked:
        blocked_paths.append(drift.relative_path)
        reason_codes.extend(drift.reason_codes)

    unique_reason_codes = tuple(dict.fromkeys(reason_codes))
    unique_blocked_paths = tuple(dict.fromkeys(blocked_paths))

    return HandoffFreshnessGuardPacket(
        app_id=app_id,
        total_sources=len(drifts),
        blocked_sources=len(blocked),
        passed=not blocked,
        reason_codes=unique_reason_codes,
        blocked_paths=unique_blocked_paths,
    )
