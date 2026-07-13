from pathlib import Path


DOCUMENT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "browser_product_console_design"
    / "DATA_SUBMISSION_AND_WORKFLOW_CONTROL.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_submission_and_validation_contract_is_explicit() -> None:
    text = read_contract()

    for marker in (
        "submission identifier",
        "content hash",
        "privacy classification",
        "licensing status",
        "Schema version",
        "Policy Eligibility rejects the submission",
        "A blocked submission must not be silently downgraded to a warning.",
    ):
        assert marker in text


def test_workflow_control_is_idempotent_and_stage_scoped() -> None:
    text = read_contract()

    for marker in (
        "Every submission action requires an idempotency key.",
        "Every workflow-start action requires an idempotency key.",
        "A browser refresh must not repeat a workflow start.",
        "Retry must be stage-scoped.",
        "A resume action must not repeat completed deterministic stages.",
        "Cancelling a workflow must not delete evidence or audit history.",
    ):
        assert marker in text


def test_d3_preserves_authority_and_runtime_boundaries() -> None:
    text = read_contract()

    for marker in (
        "Controlled AI remains subordinate to deterministic authority and Operator review.",
        "Missing required artifacts must block review completion.",
        "The browser must not edit immutable audit records.",
        "no runtime implementation is created",
        "web server startup during this design phase",
        "HTTP port binding during this design phase",
        "direct Git mutation",
    ):
        assert marker in text
