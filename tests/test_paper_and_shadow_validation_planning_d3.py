from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "paper_and_shadow_validation_planning"
    / "METRIC_AND_COMPARISON_CONTRACT.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d3_phase_and_authority_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1",
        "PLANNING_ONLY",
        "NO_RUNTIME_IMPLEMENTATION",
        "NO_AUTOMATIC_PROMOTION",
        "NO_AUTOMATIC_LEARNING",
        "The deterministic FCF engine remains the metric calculation authority.",
        "The Operator remains the final acceptance authority.",
    ):
        assert marker in text


def test_d3_requires_registered_versioned_metrics() -> None:
    text = read_contract()

    for marker in (
        "Metric registry",
        "metric_id",
        "metric_version",
        "calculation_method",
        "minimum_sample_size",
        "guardrail_threshold",
        "blocking_threshold",
        "deterministic_implementation_reference",
        "An unregistered metric must not enter an accepted comparison packet.",
    ):
        assert marker in text


def test_d3_preserves_sample_and_segment_integrity() -> None:
    text = read_contract()

    for marker in (
        "Sample sufficiency",
        "INSUFFICIENT",
        "A small sample must not be represented as conclusive evidence.",
        "Exclusions and abstentions",
        "Segment analysis",
        "Aggregate improvement must not hide a blocking failure",
        "Abstention must not be counted as a correct prediction",
    ):
        assert marker in text


def test_d3_preserves_comparison_and_guardrail_states() -> None:
    text = read_contract()

    for marker in (
        "Primary metrics and guardrails",
        "NOT_COMPARABLE",
        "INSUFFICIENT_SAMPLE",
        "BLOCKED",
        "DEGRADED",
        "INVALID",
        "NOT_COMPARABLE must not be represented as a tie.",
        "INSUFFICIENT_SAMPLE must not be represented as evidence of equivalence.",
    ):
        assert marker in text


def test_d3_prohibits_automatic_authority_and_execution() -> None:
    text = read_contract()

    for marker in (
        "automatic Champion promotion",
        "automatic baseline replacement",
        "automatic configuration activation",
        "automatic learning activation",
        "Operator review remains mandatory",
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
