from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "paper_and_shadow_validation_planning"
    / "FINAL_CURRENT_STATE.md"
)


def read_state() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d6_phase_status_and_delivery_are_explicit() -> None:
    text = read_state()

    for marker in (
        "PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1",
        "D6 - Final Planning Closeout and Controlled Handoff",
        "SIDECAR_COMPLETE",
        "PLANNING_ONLY",
        "NOT_MERGED_TO_MAIN",
        "NO_RUNTIME_IMPLEMENTATION",
        "NO_PAPER_VALIDATION_RUNTIME",
        "NO_SHADOW_OBSERVATION_RUNTIME",
        "NO_TRADING_RUNTIME",
    ):
        assert marker in text


def test_d6_records_all_completed_deliveries() -> None:
    text = read_state()

    for marker in (
        "D1 - Boundary contract",
        "fd935fb5507d02b46320ca313df8cbe1df81b2c9",
        "D2 - Registered inputs and evaluation windows",
        "9809c6f86cb6fe6f0fea39d53208438356ef18c2",
        "D3 - Metric and comparison contract",
        "89fb8af57084ba870a8251ff561c766900e3fad3",
        "D4 - Risk, contradiction, and Operator review",
        "fb361ba72845171ac784497f7db511d4d12cae44",
        "D5 - Validation plan and lifecycle",
        "f6327cfa4c85e82f574ae42a94f11a1d4e977d8b",
    ):
        assert marker in text


def test_d6_preserves_authority_and_governance() -> None:
    text = read_state()

    for marker in (
        "The deterministic FCF engine remains the calculation and hard-policy",
        "Registered artifacts remain the evidence authority.",
        "The Operator remains the final plan, review, acceptance, promotion, and",
        "AI remains advisory only.",
        "risk flags",
        "contradiction records",
        "correlation_id",
        "No state may silently become ACCEPTED.",
    ):
        assert marker in text


def test_d6_preserves_runtime_and_execution_prohibitions() -> None:
    text = read_state()

    for marker in (
        "This phase authorizes no runtime.",
        "scheduler",
        "worker",
        "web server",
        "API endpoint",
        "validation runtime",
        "shadow observation runtime",
        "broker connector",
        "exchange connector",
        "order path",
        "real trading",
        "real execution",
    ):
        assert marker in text


def test_d6_preserves_core_promotion_and_release_boundaries() -> None:
    text = read_state()

    for marker in (
        "P1-P47 remain frozen.",
        "P48 is not created.",
        "paper-only",
        "read-only",
        "sidecar-only",
        "automatic Champion promotion",
        "automatic baseline replacement",
        "automatic learning activation",
        "No next phase may start automatically.",
        "tag",
        "release",
        "deployment",
    ):
        assert marker in text


def test_d6_requires_controlled_merge_and_full_validation() -> None:
    text = read_state()

    for marker in (
        "Merge readiness",
        "all D1-D6 targeted tests pass",
        "full project pytest passes during Boundary C",
        "run_all_checks passes during Boundary C",
        "generated runtime artifacts are restored",
        "no frozen Core mutation is detected",
        "no runtime implementation is detected",
        "Boundary D must synchronize",
    ):
        assert marker in text
