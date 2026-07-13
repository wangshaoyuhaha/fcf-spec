from pathlib import Path


DOCUMENT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "browser_product_console_design"
    / "OPERATOR_REVIEW_AND_CONFIGURATION_GOVERNANCE.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_operator_review_actions_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "Operator approval must be explicit and human-confirmed.",
        "APPROVE",
        "REJECT",
        "RETURN_FOR_REVISION",
        "RECORD_MANUAL_FALLBACK",
        "Every review action requires:",
        "A browser refresh must not repeat a review action.",
        "A repeated idempotency key must return the existing decision.",
    ):
        assert marker in text


def test_configuration_governance_is_controlled() -> None:
    text = read_contract()

    for marker in (
        "Configuration visibility does not grant modification authority.",
        "Configuration lifecycle",
        "A DRAFT configuration must not be treated as ACTIVE.",
        "A configuration change must remain subject to explicit governance approval.",
        "select a model automatically",
        "route providers automatically",
        "execute a Prompt automatically",
    ):
        assert marker in text


def test_d5_preserves_credentials_audit_and_runtime_boundaries() -> None:
    text = read_contract()

    for marker in (
        "broker credentials",
        "wallet keys",
        "private keys",
        "trading API keys",
        "Immutable audit records must remain read-only in the browser.",
        "paper-only remains mandatory",
        "no runtime implementation is created",
        "web server startup during this design phase",
        "HTTP port binding during this design phase",
        "direct Git mutation",
    ):
        assert marker in text
