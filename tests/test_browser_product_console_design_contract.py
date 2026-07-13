from pathlib import Path


DOCUMENT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "browser_product_console_design"
    / "BOUNDARY_AND_ROLE_CONTRACT.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_roles_and_authority_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1",
        "DESIGN_ONLY",
        "Viewer",
        "Research Analyst",
        "Operator Reviewer",
        "Governance Administrator",
        "The deterministic FCF engine remains the calculation and policy authority.",
        "The Operator remains the final review authority.",
        "Separation of duties",
    ):
        assert marker in text


def test_project_safety_boundaries_are_preserved() -> None:
    text = read_contract()

    for marker in (
        "paper-only remains mandatory",
        "Operator review remains mandatory",
        "no P1-P47 frozen Core file is changed",
        "no P48 is created",
        "real broker or exchange connectivity",
        "real order placement",
        "wallet or private-key access",
        "automatic approval",
    ):
        assert marker in text


def test_runtime_is_not_authorized() -> None:
    text = read_contract()

    for marker in (
        "NO_RUNTIME_IMPLEMENTATION",
        "It does not start a web server.",
        "It does not open a network port.",
        "It does not create an API runtime.",
        "It does not invoke a model.",
        "HTTP service startup during this design phase",
        "port binding during this design phase",
        "arbitrary shell, Python, or PowerShell execution",
    ):
        assert marker in text
