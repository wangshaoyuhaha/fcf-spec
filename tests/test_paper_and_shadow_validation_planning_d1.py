from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "paper_and_shadow_validation_planning"
    / "BOUNDARY_CONTRACT.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d1_phase_and_authority_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1",
        "PLANNING_ONLY",
        "NO_RUNTIME_IMPLEMENTATION",
        "NO_SHADOW_TRADING_RUNTIME",
        "The deterministic FCF engine remains the calculation and policy authority.",
        "Registered artifacts remain the evidence authority.",
        "The Operator remains the final review authority.",
    ):
        assert marker in text


def test_d1_separates_replay_and_forward_observation() -> None:
    text = read_contract()

    for marker in (
        "Paper validation boundary",
        "Shadow observation boundary",
        "Historical replay and forward observation separation",
        "Historical replay must not be presented as forward observation.",
        "Forward observation must not silently reuse future-known historical data.",
        "This planning phase does not implement shadow observation runtime behavior.",
    ):
        assert marker in text


def test_d1_preserves_validation_governance() -> None:
    text = read_contract()

    for marker in (
        "Deterministic benchmark authority",
        "Baseline and candidate boundary",
        "Registered artifact boundary",
        "correlation_id",
        "Operator review remains mandatory",
        "BLOCKED",
        "DEGRADED",
        "INVALID",
        "No state may silently become ACCEPTED.",
    ):
        assert marker in text


def test_d1_prohibits_automatic_authority_and_execution() -> None:
    text = read_contract()

    for marker in (
        "automatic Champion promotion",
        "automatic baseline replacement",
        "automatic learning activation",
        "automatic approval",
        "real trading",
        "real execution",
        "broker or exchange connectivity",
        "real order placement",
        "P1-P47 frozen Core mutation",
        "P48 creation",
        "tag creation",
        "release creation",
        "deployment",
    ):
        assert marker in text


def test_d1_permanent_sidecar_boundaries_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "paper-only remains mandatory",
        "read-only remains mandatory",
        "sidecar-only remains mandatory",
        "P1-P47 remain frozen",
        "P48 is not created",
        "no runtime implementation is created",
    ):
        assert marker in text
