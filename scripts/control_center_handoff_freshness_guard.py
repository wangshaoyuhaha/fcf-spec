from __future__ import annotations

from dataclasses import dataclass


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
