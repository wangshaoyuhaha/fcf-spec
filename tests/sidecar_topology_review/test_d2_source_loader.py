from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecars" / "correlation_id_traceability_app_1" / "D6_final_handoff_closeout.md"


def test_correlation_id_traceability_d6_final_handoff_closeout_exists():
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    required = [
        "D6 Final Handoff Closeout",
        "CORRELATION-ID-TRACEABILITY-APP-1 is completed",
        "D1 sidecar boundary and traceability contract",
        "D2 read-only source map",
        "D3 trace record schema",
        "D4 chain integrity rules",
        "D5 trace review packet",
        "correlation_id trace linkage",
        "validation failure visibility",
        "operator review requirement visibility",
        "risk flag visibility",
        "reason code visibility",
        "archive reference visibility",
        "local Dify handoff reference visibility",
        "no-execution receipt requirements",
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
        "no Dify deploy",
        "no Dify API write",
        "no tag",
        "no release",
        "no deploy",
        "Merge Readiness",
        "non-executable",
    ]
    for item in required:
        assert item in text

