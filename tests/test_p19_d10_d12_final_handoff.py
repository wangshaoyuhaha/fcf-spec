from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p19_d10_final_archive_acceptance_packet_confirms_safe_archive():
    text = read_doc("p19_final_archive_acceptance_packet.md")
    assert "archive index completed" in text
    assert "safety gate status is PASSED" in text
    assert "no deploy is enabled" in text
    assert "no real trading is enabled" in text


def test_p19_d11_final_archive_manifest_lists_archive_view_artifacts():
    text = read_doc("p19_final_archive_manifest.md")
    assert "operator_evidence_archive_view.py" in text
    assert "P19 local evidence archive view is archived" in text
    assert "P19 does not deploy" in text
    assert "P19 remains local-only and read-only" in text


def test_p19_d12_final_handoff_checkpoint_sets_p20_boundary():
    text = read_doc("p19_final_handoff_checkpoint.md")
    assert "P20 Local Evidence Console Final Review" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
