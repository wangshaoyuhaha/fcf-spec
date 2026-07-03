from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p24_d10_final_index_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p24_final_index_archive_acceptance_packet.md")
    assert "master index completed" in text
    assert "index completion gate status is PASSED" in text
    assert "READY_FOR_INDEX_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p24_d11_final_index_archive_manifest_lists_index_artifacts():
    text = read_doc("p24_final_index_archive_manifest.md")
    assert "paper_release_master_index.py" in text
    assert "P24 paper release master index is archived" in text
    assert "P24 does not deploy" in text
    assert "P24 remains local-only and read-only" in text


def test_p24_d12_final_index_handoff_checkpoint_sets_p25_boundary():
    text = read_doc("p24_final_index_handoff_checkpoint.md")
    assert "P25 Paper Release Final Archive" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
