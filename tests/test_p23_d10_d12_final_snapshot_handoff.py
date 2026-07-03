from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p23_d10_final_snapshot_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p23_final_snapshot_archive_acceptance_packet.md")
    assert "evidence snapshot completed" in text
    assert "snapshot completion gate status is PASSED" in text
    assert "READY_FOR_SNAPSHOT_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p23_d11_final_snapshot_archive_manifest_lists_snapshot_artifacts():
    text = read_doc("p23_final_snapshot_archive_manifest.md")
    assert "paper_release_evidence_snapshot.py" in text
    assert "P23 paper release evidence snapshot is archived" in text
    assert "P23 does not deploy" in text
    assert "P23 remains local-only and read-only" in text


def test_p23_d12_final_snapshot_handoff_checkpoint_sets_p24_boundary():
    text = read_doc("p23_final_snapshot_handoff_checkpoint.md")
    assert "P24 Paper Release Master Index" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
