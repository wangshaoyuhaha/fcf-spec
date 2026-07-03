from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p17_d10_final_export_acceptance_packet_confirms_operator_review():
    text = read_doc("p17_final_export_acceptance_packet.md")
    assert "local evidence export manifest completed" in text
    assert "validation status is PASSED" in text
    assert "READY_FOR_OPERATOR_REVIEW" in text
    assert "no real trading is enabled" in text


def test_p17_d11_final_archive_manifest_lists_export_artifacts():
    text = read_doc("p17_final_archive_manifest.md")
    assert "operator_evidence_export.py" in text
    assert "P17 local evidence export layer is archived" in text
    assert "P17 does not deploy" in text
    assert "P17 remains local-only and read-only" in text


def test_p17_d12_final_handoff_checkpoint_sets_p18_boundary():
    text = read_doc("p17_final_handoff_checkpoint.md")
    assert "P18 Local Evidence Console Navigation" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
