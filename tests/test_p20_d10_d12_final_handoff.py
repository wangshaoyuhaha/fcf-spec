from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p20_d10_final_archive_acceptance_packet_confirms_final_archive_ready():
    text = read_doc("p20_final_archive_acceptance_packet.md")
    assert "final review packet completed" in text
    assert "completion gate status is PASSED" in text
    assert "READY_FOR_FINAL_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p20_d11_final_archive_manifest_lists_final_review_artifacts():
    text = read_doc("p20_final_archive_manifest.md")
    assert "operator_evidence_final_review.py" in text
    assert "P20 local evidence final review is archived" in text
    assert "P20 does not deploy" in text
    assert "P20 remains local-only and read-only" in text


def test_p20_d12_final_handoff_checkpoint_sets_p21_boundary():
    text = read_doc("p20_final_handoff_checkpoint.md")
    assert "P21 Paper Evidence Console Master Closeout" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
