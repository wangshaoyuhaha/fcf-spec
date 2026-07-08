from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecars" / "correlation_id_traceability_app_1" / "D1_contract.md"


def test_correlation_id_traceability_d1_contract_exists():
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    required = [
        "CORRELATION-ID-TRACEABILITY-APP-1",
        "paper-only",
        "local-only",
        "read-only",
        "sidecar-only",
        "operator review required",
        "no P48 core expansion",
        "no P1-P47 core mutation",
        "no score mutation",
        "no reason code mutation",
        "no risk flag deletion",
        "no risk flag downgrade",
        "data snapshot",
        "validation result",
        "operator review record",
        "UI report view",
        "archive item",
        "Dify handoff packet",
        "correlation_id",
        "Correlation_ID is only a traceability identifier",
    ]
    for item in required:
        assert item in text

