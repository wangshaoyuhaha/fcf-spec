from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p26_d10_final_receipt_archive_acceptance_packet_confirms_archive_ready():
    text = read_doc("p26_final_receipt_archive_acceptance_packet.md")
    assert "completion receipt completed" in text
    assert "receipt completion gate status is PASSED" in text
    assert "READY_FOR_RECEIPT_ARCHIVE" in text
    assert "no real trading is enabled" in text


def test_p26_d11_final_receipt_archive_manifest_lists_receipt_artifacts():
    text = read_doc("p26_final_receipt_archive_manifest.md")
    assert "paper_release_completion_receipt.py" in text
    assert "P26 paper release completion receipt is archived" in text
    assert "P26 does not deploy" in text
    assert "P26 remains local-only and read-only" in text


def test_p26_d12_final_receipt_handoff_checkpoint_sets_p27_boundary():
    text = read_doc("p26_final_receipt_handoff_checkpoint.md")
    assert "P27 Paper Release Final Verification" in text
    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "operator review required" in text
