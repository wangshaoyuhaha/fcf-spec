from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p22_d10_final_ledger_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p22_final_ledger_archive_acceptance_packet.md")
    assert "release master ledger completed" in text
    assert "ledger completion gate status is PASSED" in text
    assert "READY_FOR_LEDGER_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p22_d11_final_ledger_archive_manifest_lists_ledger_artifacts():
    text = read_doc("p22_final_ledger_archive_manifest.md")
    assert "paper_release_master_ledger.py" in text
    assert "P22 paper release master ledger is archived" in text
    assert "P22 does not deploy" in text
    assert "P22 remains local-only and read-only" in text


def test_p22_d12_final_ledger_handoff_checkpoint_sets_p23_boundary():
    text = read_doc("p22_final_ledger_handoff_checkpoint.md")
    assert "P23 Paper Release Evidence Snapshot" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
