from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecars" / "correlation_id_traceability_app_1" / "D4_chain_integrity_rules.md"


def test_correlation_id_traceability_d4_chain_integrity_rules_exist():
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    required = [
        "D4 Chain Integrity Rules",
        "every trace record must have one correlation_id",
        "source_artifact_id",
        "source_stage",
        "source_artifact_checksum",
        "must not create circular references",
        "validation failure states must remain visible",
        "operator review requirements must remain visible",
        "risk_flags_present must remain visible",
        "reason_codes_present must remain visible",
        "UI references must not hide risk flags",
        "Dify handoff references must stay local and read-only",
        "correlation_id is missing",
        "validation_state is downgraded",
        "review_state bypasses operator review",
        "trace_integrity_failed",
        "must not be promoted to valid archive state",
        "must not be passed to Dify handoff as complete",
        "must not suppress operator review",
        "must not become trade instructions",
        "paper-only, local-only, read-only, sidecar-only",
    ]
    for item in required:
        assert item in text

