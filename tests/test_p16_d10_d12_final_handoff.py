from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p16_d10_final_operator_evidence_acceptance_packet_preserves_review():
    text = read_doc("p16_final_operator_evidence_acceptance_packet.md")
    assert "operator evidence console skeleton completed" in text
    assert "safety gate remains passed" in text
    assert "no deploy is enabled" in text
    assert "no real trading is enabled" in text


def test_p16_d11_final_archive_manifest_lists_core_artifacts():
    text = read_doc("p16_final_archive_manifest.md")
    assert "operator_evidence_console.py" in text
    assert "P16 operator evidence console is archived as paper-only" in text
    assert "P16 does not deploy" in text
    assert "P16 does not enable real trading" in text


def test_p16_d12_final_handoff_checkpoint_sets_next_phase_boundary():
    text = read_doc("p16_final_handoff_checkpoint.md")
    assert "P17 Local Evidence Console Export Files" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
