from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p28_d10_final_seal_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p28_final_seal_archive_acceptance_packet.md")
    assert "final seal packet completed" in text
    assert "final seal completion gate status is PASSED" in text
    assert "READY_FOR_SEAL_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p28_d11_final_seal_archive_manifest_lists_seal_artifacts():
    text = read_doc("p28_final_seal_archive_manifest.md")
    assert "paper_release_final_seal.py" in text
    assert "P28 paper release final seal is archived" in text
    assert "P28 does not deploy" in text
    assert "P28 remains local-only and read-only" in text


def test_p28_d12_final_seal_handoff_checkpoint_sets_p29_boundary():
    text = read_doc("p28_final_seal_handoff_checkpoint.md")
    assert "P29 Paper Release Final Operator Receipt" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
