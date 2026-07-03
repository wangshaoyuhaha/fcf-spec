from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p21_d10_final_master_archive_acceptance_packet_confirms_master_archive_ready():
    text = read_doc("p21_final_master_archive_acceptance_packet.md")
    assert "master closeout packet completed" in text
    assert "master completion gate status is PASSED" in text
    assert "READY_FOR_MASTER_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p21_d11_final_master_archive_manifest_lists_master_artifacts():
    text = read_doc("p21_final_master_archive_manifest.md")
    assert "paper_evidence_master_closeout.py" in text
    assert "P21 paper evidence master closeout is archived" in text
    assert "P21 does not deploy" in text
    assert "P21 remains local-only and read-only" in text


def test_p21_d12_final_master_handoff_checkpoint_sets_p22_boundary():
    text = read_doc("p21_final_master_handoff_checkpoint.md")
    assert "P22 Paper Release Master Ledger" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
