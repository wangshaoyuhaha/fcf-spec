from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecars" / "correlation_id_traceability_app_1" / "D2_source_map.md"


def test_correlation_id_traceability_d2_source_map_exists():
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    required = [
        "D2 Source Map",
        "Data stage",
        "Validation stage",
        "Operator review stage",
        "UI report stage",
        "Archive stage",
        "Dify handoff stage",
        "correlation_id",
        "source_artifact_id",
        "source_artifact_path",
        "source_artifact_checksum",
        "upstream_correlation_id",
        "downstream_correlation_id",
        "must not mutate source data",
        "must not downgrade validation failures",
        "must not bypass operator review",
        "must not hide risk flags or reason codes",
        "must not overwrite or delete archived content",
        "must not deploy, create, or update a Dify app",
        "paper-only, local-only, read-only, and sidecar-only",
    ]
    for item in required:
        assert item in text

