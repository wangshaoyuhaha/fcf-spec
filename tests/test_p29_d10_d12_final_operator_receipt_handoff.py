from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p29_d10_final_operator_receipt_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p29_final_operator_receipt_archive_acceptance_packet.md")
    assert "final operator receipt completed" in text
    assert "operator receipt completion gate status is PASSED" in text
    assert "READY_FOR_OPERATOR_RECEIPT_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p29_d11_final_operator_receipt_archive_manifest_lists_receipt_artifacts():
    text = read_doc("p29_final_operator_receipt_archive_manifest.md")
    assert "paper_release_final_operator_receipt.py" in text
    assert "P29 paper release final operator receipt is archived" in text
    assert "P29 does not deploy" in text
    assert "P29 remains local-only and read-only" in text


def test_p29_d12_final_operator_receipt_handoff_checkpoint_sets_p30_boundary():
    text = read_doc("p29_final_operator_receipt_handoff_checkpoint.md")
    assert "P30 Paper Release Final Delivery" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
