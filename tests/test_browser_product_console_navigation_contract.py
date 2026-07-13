from pathlib import Path


DOCUMENT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "browser_product_console_design"
    / "INFORMATION_ARCHITECTURE_AND_NAVIGATION.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_primary_navigation_is_complete() -> None:
    text = read_contract()

    for marker in (
        "Overview",
        "Data Workspace",
        "Research Runs",
        "AI Comparison",
        "Evidence and Risk",
        "Operator Review",
        "Reports and Archive",
        "Governance",
        "Audit History",
    ):
        assert marker in text


def test_navigation_preserves_authority_and_safety() -> None:
    text = read_contract()

    for marker in (
        "The product shell must always display PAPER_ONLY.",
        "Risk flags must not be hidden by summary text.",
        "No review action is complete without explicit human confirmation.",
        "The browser must not archive automatically.",
        "Audit records must be read-only from the browser.",
        "Hidden navigation does not count as an authorization control.",
    ):
        assert marker in text


def test_navigation_cannot_trigger_runtime_actions() -> None:
    text = read_contract()

    for marker in (
        "A browser refresh must restore display state without repeating an action.",
        "A deep link must not create, approve, route, invoke, archive, or execute.",
        "no runtime implementation is created",
        "no web server is started",
        "no HTTP port is opened",
        "no model is invoked",
    ):
        assert marker in text
