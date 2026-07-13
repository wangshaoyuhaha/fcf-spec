from pathlib import Path


DOCUMENT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "browser_product_console_design"
    / "REPORT_RISK_AND_EVIDENCE_PRESENTATION.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_report_and_risk_states_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "REVIEW_REQUIRED",
        "RETURNED_FOR_REVISION",
        "ARCHIVE_ELIGIBLE",
        "Risk flags must be presented as first-class governed data.",
        "A CRITICAL risk must not be hidden",
        "A blocking risk must remain visible",
    ):
        assert marker in text


def test_contradiction_and_evidence_are_traceable() -> None:
    text = read_contract()

    for marker in (
        "Contradictions must be displayed separately from ordinary risk flags.",
        "An unresolved contradiction must remain visible",
        "Every report conclusion must expose an evidence path.",
        "correlation identifier",
        "parent references",
        "validation status",
        "archive status",
    ):
        assert marker in text


def test_d4_preserves_ai_operator_and_export_boundaries() -> None:
    text = read_contract()

    for marker in (
        "AI output must be visually labelled ASSISTIVE_ONLY.",
        "AI output must not be labelled authoritative, approved, or final.",
        "require explicit human confirmation and rationale.",
        "The review packet must not contain an automatic approval control.",
        "Export is not archive.",
        "Export is not release.",
        "Export is not deployment.",
        "no runtime implementation is created",
    ):
        assert marker in text
