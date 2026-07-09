"""Deterministic global scan classification rulebook.

This module is paper-only, local-only, read-only, and sidecar-only.
It does not execute trades, connect to brokers, connect to exchanges, store credentials,
mutate core files, deploy releases, or bypass operator review.
"""

from __future__ import annotations

from dataclasses import dataclass


EXPECTED_GOVERNANCE_TEXT = "EXPECTED_GOVERNANCE_TEXT"
EXPECTED_TEST_ASSERTION = "EXPECTED_TEST_ASSERTION"
EXPECTED_FINAL_STATE_HISTORY = "EXPECTED_FINAL_STATE_HISTORY"
EXPECTED_SAFETY_BOUNDARY = "EXPECTED_SAFETY_BOUNDARY"
ACTIONABLE_STALE_STATE = "ACTIONABLE_STALE_STATE"
ACTIONABLE_UNSAFE_PERMISSION = "ACTIONABLE_UNSAFE_PERMISSION"
ACTIONABLE_STRUCTURE_GAP = "ACTIONABLE_STRUCTURE_GAP"

LABELS = (
    EXPECTED_GOVERNANCE_TEXT,
    EXPECTED_TEST_ASSERTION,
    EXPECTED_FINAL_STATE_HISTORY,
    EXPECTED_SAFETY_BOUNDARY,
    ACTIONABLE_STALE_STATE,
    ACTIONABLE_UNSAFE_PERMISSION,
    ACTIONABLE_STRUCTURE_GAP,
)

ACTIONABLE_LABELS = {
    ACTIONABLE_STALE_STATE,
    ACTIONABLE_UNSAFE_PERMISSION,
    ACTIONABLE_STRUCTURE_GAP,
}

EXPECTED_LABELS = {
    EXPECTED_GOVERNANCE_TEXT,
    EXPECTED_TEST_ASSERTION,
    EXPECTED_FINAL_STATE_HISTORY,
    EXPECTED_SAFETY_BOUNDARY,
}

CONSERVATIVE_PRIORITY = (
    ACTIONABLE_UNSAFE_PERMISSION,
    ACTIONABLE_STRUCTURE_GAP,
    ACTIONABLE_STALE_STATE,
    EXPECTED_SAFETY_BOUNDARY,
    EXPECTED_TEST_ASSERTION,
    EXPECTED_FINAL_STATE_HISTORY,
    EXPECTED_GOVERNANCE_TEXT,
)

UNSAFE_TERMS = (
    "real trading",
    "real execution",
    "broker",
    "exchange",
    "api key",
    "wallet private key",
    "real account",
    "real position",
    "buy button",
    "sell button",
    "order button",
    "buy",
    "sell",
    "order",
    "operator review bypass",
    "bypass operator review",
    "circuit_break downgrade",
    "downgrade circuit_break",
)

PERMISSION_TERMS = (
    "allowed",
    "enabled",
    "permission",
    "permit",
    "permits",
    "enable",
    "enables",
    "can ",
    "may ",
    "true",
)

PROHIBITION_TERMS = (
    "no ",
    "not ",
    "never",
    "must not",
    "forbidden",
    "prohibit",
    "prohibited",
    "blocked",
    "deny",
    "disabled",
)

STALE_TERMS = (
    "stale",
    "outdated",
    "obsolete",
    "old validation",
    "wrong head",
    "old head",
    "not synced",
    "conflicts with current control center",
    "conflict with current control center",
    "handoff mismatch",
)

STRUCTURE_GAP_TERMS = (
    "structure gap",
    "missing provenance",
    "missing audit trail",
    "missing classification rule",
    "unclear ownership",
    "reverse dependency",
    "circular dependency",
    "sidecar isolation gap",
    "dependency boundary missing",
)

TEST_PATH_TERMS = (
    "/tests/",
    "\\tests\\",
    "test_",
)

FINAL_STATE_TERMS = (
    "fcf_current_state",
    "final current state",
    "final-state",
    "closeout",
    "completion record",
    "validation history",
)

GOVERNANCE_PATH_TERMS = (
    "/docs/",
    "\\docs\\",
    "handoff",
    "control_center",
    "project_control_center",
    "architecture",
    "safety",
    "governance",
)


@dataclass(frozen=True)
class ClassifiedScanHit:
    source_path: str
    matched_text: str
    classification_label: str
    reason_code: str
    review_required: bool
    correlation_id: str | None = None


def _normalize(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/").lower()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _choose_label(candidates: set[str]) -> str:
    for label in CONSERVATIVE_PRIORITY:
        if label in candidates:
            return label
    return ACTIONABLE_STRUCTURE_GAP


def _reason_code_for(label: str) -> str:
    return {
        EXPECTED_GOVERNANCE_TEXT: "EXPECTED_GOVERNANCE_TEXT_MATCH",
        EXPECTED_TEST_ASSERTION: "EXPECTED_TEST_ASSERTION_MATCH",
        EXPECTED_FINAL_STATE_HISTORY: "EXPECTED_FINAL_STATE_HISTORY_MATCH",
        EXPECTED_SAFETY_BOUNDARY: "EXPECTED_SAFETY_BOUNDARY_MATCH",
        ACTIONABLE_STALE_STATE: "ACTIONABLE_STALE_STATE_MATCH",
        ACTIONABLE_UNSAFE_PERMISSION: "ACTIONABLE_UNSAFE_PERMISSION_MATCH",
        ACTIONABLE_STRUCTURE_GAP: "ACTIONABLE_STRUCTURE_GAP_MATCH",
    }[label]


def classify_scan_hit(
    *,
    source_path: str,
    matched_text: str,
    context: str = "",
    correlation_id: str | None = None,
) -> ClassifiedScanHit:
    """Classify one global scan hit into exactly one label."""

    path = _normalize(source_path)
    body = _normalize(f"{matched_text}\n{context}")
    combined = f"{path}\n{body}"

    candidates: set[str] = set()

    has_unsafe = _contains_any(body, UNSAFE_TERMS)
    has_permission = _contains_any(body, PERMISSION_TERMS)
    has_prohibition = _contains_any(body, PROHIBITION_TERMS)

    if has_unsafe and has_permission and not has_prohibition:
        candidates.add(ACTIONABLE_UNSAFE_PERMISSION)

    if _contains_any(combined, STRUCTURE_GAP_TERMS):
        candidates.add(ACTIONABLE_STRUCTURE_GAP)

    if _contains_any(combined, STALE_TERMS):
        candidates.add(ACTIONABLE_STALE_STATE)

    if has_unsafe and has_prohibition:
        candidates.add(EXPECTED_SAFETY_BOUNDARY)

    if _contains_any(path, TEST_PATH_TERMS) or "assert " in body:
        candidates.add(EXPECTED_TEST_ASSERTION)

    if _contains_any(combined, FINAL_STATE_TERMS):
        candidates.add(EXPECTED_FINAL_STATE_HISTORY)

    if _contains_any(combined, GOVERNANCE_PATH_TERMS):
        candidates.add(EXPECTED_GOVERNANCE_TEXT)

    label = _choose_label(candidates)
    return ClassifiedScanHit(
        source_path=source_path,
        matched_text=matched_text,
        classification_label=label,
        reason_code=_reason_code_for(label),
        review_required=label in ACTIONABLE_LABELS,
        correlation_id=correlation_id,
    )


def is_actionable(label: str) -> bool:
    if label not in LABELS:
        raise ValueError(f"Unknown label: {label}")
    return label in ACTIONABLE_LABELS


def is_expected(label: str) -> bool:
    if label not in LABELS:
        raise ValueError(f"Unknown label: {label}")
    return label in EXPECTED_LABELS
