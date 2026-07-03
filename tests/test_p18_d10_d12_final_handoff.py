from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p18_d10_final_navigation_acceptance_packet_confirms_safe_navigation():
    text = read_doc("p18_final_navigation_acceptance_packet.md")
    assert "local evidence navigation index completed" in text
    assert "safety gate status is PASSED" in text
    assert "no deploy is enabled" in text
    assert "no real trading is enabled" in text


def test_p18_d11_final_archive_manifest_lists_navigation_artifacts():
    text = read_doc("p18_final_archive_manifest.md")
    assert "operator_evidence_navigation.py" in text
    assert "P18 local evidence navigation layer is archived" in text
    assert "P18 does not deploy" in text
    assert "P18 remains local-only and read-only" in text


def test_p18_d12_final_handoff_checkpoint_sets_p19_boundary():
    text = read_doc("p18_final_handoff_checkpoint.md")
    assert "P19 Local Evidence Console Archive View" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
