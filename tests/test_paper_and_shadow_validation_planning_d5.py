from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "paper_and_shadow_validation_planning"
    / "VALIDATION_PLAN_AND_LIFECYCLE_CONTRACT.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d5_phase_and_runtime_boundary_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1",
        "PLANNING_ONLY",
        "NO_RUNTIME_IMPLEMENTATION",
        "NO_SCHEDULER",
        "NO_BACKGROUND_WORKER",
        "NO_AUTOMATIC_STATE_TRANSITION",
    ):
        assert marker in text


def test_d5_requires_complete_plan_identity_and_entry_gates() -> None:
    text = read_contract()

    for marker in (
        "Validation plan packet",
        "validation_plan_id",
        "evaluation_mode",
        "metric_registry_version",
        "blocking_guardrails",
        "correlation_id",
        "Entry gates",
        "leakage-control checks pass",
        "risk flags remain visible",
        "contradictions remain visible",
    ):
        assert marker in text


def test_d5_requires_governed_lifecycle_and_operator_approval() -> None:
    text = read_contract()

    for marker in (
        "Lifecycle states",
        "READY_FOR_OPERATOR_REVIEW",
        "APPROVED_FOR_PAPER_VALIDATION",
        "APPROVED_FOR_FORWARD_OBSERVATION",
        "No state transition may occur silently.",
        "Operator plan approval",
        "Plan approval does not start a runtime.",
        "Plan approval does not authorize real execution.",
    ):
        assert marker in text


def test_d5_preserves_stop_revision_and_duplicate_controls() -> None:
    text = read_contract()

    for marker in (
        "Stop conditions",
        "A stop condition must not be converted into successful completion.",
        "Cancelled plans must not silently resume.",
        "Revision and restart",
        "A restart must not overwrite the earlier plan",
        "Idempotency and duplicate prevention",
        "must not create duplicate validation records",
    ):
        assert marker in text


def test_d5_preserves_permanent_project_boundaries() -> None:
    text = read_contract()

    for marker in (
        "Controlled handoff",
        "a scheduler",
        "a queue",
        "a worker",
        "a web server",
        "an API endpoint",
        "automatic Champion promotion",
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
