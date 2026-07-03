from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p25_d10_final_closeout_acceptance_packet_confirms_closeout_ready():
    text = read_doc("p25_final_closeout_acceptance_packet.md")
    assert "final archive packet completed" in text
    assert "final archive completion gate status is PASSED" in text
    assert "READY_FOR_FINAL_ARCHIVE_CLOSEOUT" in text
    assert "no real trading is enabled" in text


def test_p25_d11_final_closeout_manifest_lists_final_archive_artifacts():
    text = read_doc("p25_final_closeout_manifest.md")
    assert "paper_release_final_archive.py" in text
    assert "P25 paper release final archive is closed" in text
    assert "P25 does not deploy" in text
    assert "P25 remains local-only and read-only" in text


def test_p25_d12_final_closeout_handoff_checkpoint_sets_p26_boundary():
    text = read_doc("p25_final_closeout_handoff_checkpoint.md")
    assert "P26 Paper Release Completion Receipt" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
