from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p27_d10_final_verification_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p27_final_verification_archive_acceptance_packet.md")
    assert "final verification packet completed" in text
    assert "final verification completion gate status is PASSED" in text
    assert "READY_FOR_VERIFICATION_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p27_d11_final_verification_archive_manifest_lists_verification_artifacts():
    text = read_doc("p27_final_verification_archive_manifest.md")
    assert "paper_release_final_verification.py" in text
    assert "P27 paper release final verification is archived" in text
    assert "P27 does not deploy" in text
    assert "P27 remains local-only and read-only" in text


def test_p27_d12_final_verification_handoff_checkpoint_sets_p28_boundary():
    text = read_doc("p27_final_verification_handoff_checkpoint.md")
    assert "P28 Paper Release Final Seal" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
