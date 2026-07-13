from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "browser_product_console_design"
    / "FINAL_DESIGN_BLUEPRINT_AND_ACCEPTANCE.md"
)

DESIGN_DIRECTORY = ROOT / "docs" / "browser_product_console_design"


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d6_complete_design_package_is_present() -> None:
    required_files = (
        "BOUNDARY_AND_ROLE_CONTRACT.md",
        "INFORMATION_ARCHITECTURE_AND_NAVIGATION.md",
        "DATA_SUBMISSION_AND_WORKFLOW_CONTROL.md",
        "REPORT_RISK_AND_EVIDENCE_PRESENTATION.md",
        "OPERATOR_REVIEW_AND_CONFIGURATION_GOVERNANCE.md",
        "FINAL_DESIGN_BLUEPRINT_AND_ACCEPTANCE.md",
    )

    for name in required_files:
        assert (DESIGN_DIRECTORY / name).is_file()


def test_d6_final_authority_and_command_contract_is_explicit() -> None:
    text = read_contract()

    for marker in (
        "The deterministic FCF engine remains the calculation and policy authority.",
        "The Operator remains the final review authority.",
        "Every state-changing command must include:",
        "idempotency key",
        "A browser refresh must not repeat a command.",
        "Risk flags must remain first-class governed data.",
        "AI output must remain labelled ASSISTIVE_ONLY.",
    ):
        assert marker in text


def test_d6_preserves_permanent_boundaries() -> None:
    text = read_contract()

    for marker in (
        "NO_RUNTIME_IMPLEMENTATION",
        "real broker or exchange connectivity",
        "automatic model selection",
        "automatic Prompt execution",
        "direct Git mutation",
        "P1-P47 frozen Core mutation",
        "P48 creation",
        "No implementation phase is approved by this document.",
        "paper-only remains mandatory",
        "Operator review remains mandatory",
        "no runtime implementation is created",
    ):
        assert marker in text
