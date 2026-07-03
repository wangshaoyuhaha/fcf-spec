from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p30_d10_final_delivery_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p30_final_delivery_archive_acceptance_packet.md")
    assert "final delivery packet completed" in text
    assert "final delivery completion gate status is PASSED" in text
    assert "READY_FOR_DELIVERY_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p30_d11_final_delivery_archive_manifest_lists_delivery_artifacts():
    text = read_doc("p30_final_delivery_archive_manifest.md")
    assert "paper_release_final_delivery.py" in text
    assert "P30 paper release final delivery is archived" in text
    assert "P30 does not deploy" in text
    assert "P30 remains local-only and read-only" in text


def test_p30_d12_final_delivery_handoff_checkpoint_sets_p31_boundary():
    text = read_doc("p30_final_delivery_handoff_checkpoint.md")
    assert "P31 Paper Release Terminal Closeout" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
