from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "paper_and_shadow_validation_planning"
    / "REGISTERED_INPUT_AND_EVALUATION_WINDOW_CONTRACT.md"
)


def read_contract() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_d2_phase_and_status_are_explicit() -> None:
    text = read_contract()

    for marker in (
        "PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1",
        "PLANNING_ONLY",
        "NO_RUNTIME_IMPLEMENTATION",
        "NO_DATA_FETCHING",
        "NO_FORWARD_OBSERVATION_RUNTIME",
    ):
        assert marker in text


def test_d2_requires_registered_source_identity() -> None:
    text = read_contract()

    for marker in (
        "Required source manifest fields",
        "source_artifact_id",
        "dataset_version",
        "Config Snapshot identifier",
        "content_hash",
        "observation_cutoff_utc",
        "correlation_id",
        "evidence_references",
        "A missing mandatory field must not be silently inferred.",
    ):
        assert marker in text


def test_d2_separates_historical_and_forward_windows() -> None:
    text = read_contract()

    for marker in (
        "Evaluation window identity",
        "HISTORICAL_REPLAY",
        "FORWARD_OBSERVATION",
        "decision_cutoff_utc",
        "outcome_maturity_utc",
        "Historical replay must use a frozen dataset snapshot.",
        "Subsequent outcomes must be registered as separate artifacts.",
    ):
        assert marker in text


def test_d2_blocks_leakage_and_invalid_inputs() -> None:
    text = read_contract()

    for marker in (
        "Leakage-control rules",
        "future-known features",
        "silent historical backfill",
        "correlation_id mismatch",
        "LEAKAGE_RISK",
        "INVALID inputs must not enter metric calculation.",
        "No AI explanation may override a leakage-control failure.",
    ):
        assert marker in text


def test_d2_preserves_permanent_project_boundaries() -> None:
    text = read_contract()

    for marker in (
        "P1-P47 frozen Core mutation",
        "P48",
        "runtime data ingestion",
        "broker or exchange connectivity",
        "order placement",
        "model invocation",
        "automatic Champion promotion",
        "automatic learning activation",
        "Operator review remains mandatory",
        "paper-only remains mandatory",
        "read-only remains mandatory",
        "sidecar-only remains mandatory",
    ):
        assert marker in text
