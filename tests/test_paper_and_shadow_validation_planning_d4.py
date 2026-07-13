from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "paper_and_shadow_validation_planning"
    / "RISK_CONTRADICTION_AND_OPERATOR_REVIEW_CONTRACT.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d4_phase_and_authority_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1",
        "PLANNING_ONLY",
        "NO_RUNTIME_IMPLEMENTATION",
        "NO_AUTOMATIC_DECISION",
        "NO_AUTOMATIC_PROMOTION",
        "The Operator remains the final review and acceptance authority.",
    ):
        assert marker in text


def test_d4_requires_complete_result_packet_identity() -> None:
    text = read_contract()

    for marker in (
        "Validation result packet identity",
        "validation_packet_id",
        "comparison_id",
        "metric_results",
        "guardrail_results",
        "risk_flags",
        "contradiction_records",
        "correlation_id",
        "Missing mandatory packet identity must fail visibly.",
    ):
        assert marker in text


def test_d4_preserves_risk_and_contradiction_evidence() -> None:
    text = read_contract()

    for marker in (
        "Risk flag preservation",
        "Risk flags must remain first-class packet content.",
        "must not delete, suppress, downgrade, or relabel",
        "Contradiction preservation",
        "Contradictions must remain visible",
        "An unresolved blocking contradiction must prevent ACCEPTED status.",
    ):
        assert marker in text


def test_d4_requires_operator_review_and_separate_promotion() -> None:
    text = read_contract()

    for marker in (
        "Operator review record",
        "reviewer_identity",
        "decision",
        "rationale",
        "Separation of review and promotion",
        "An ACCEPT decision does not automatically",
        "Promotion requires a separately registered governance packet",
    ):
        assert marker in text


def test_d4_preserves_permanent_boundaries() -> None:
    text = read_contract()

    for marker in (
        "BLOCKED, DEGRADED, and INVALID must remain separate.",
        "automatic Champion promotion",
        "automatic baseline replacement",
        "automatic learning activation",
        "P1-P47 frozen Core mutation",
        "P48",
        "real trading",
        "real execution",
        "broker or exchange connectivity",
        "order placement",
        "paper-only remains mandatory",
        "read-only remains mandatory",
        "sidecar-only remains mandatory",
    ):
        assert marker in text
