from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p15_d10_no_deploy_release_audit_blocks_runtime_activation():
    text = read_doc("p15_no_deploy_release_audit.md")
    assert "No deploy was performed" in text
    assert "No real exchange API was enabled" in text
    assert "No real orders were enabled" in text
    assert "None of these steps enable real trading" in text


def test_p15_d11_operator_evidence_console_contract_is_read_only():
    text = read_doc("p15_operator_evidence_console_contract.md")
    assert "read-only evidence console contract" in text
    assert "release evidence index" in text
    assert "patch proposal review queue" in text
    assert "deploy trigger" in text


def test_p15_d12_final_closeout_checkpoint_lists_complete_scope():
    text = read_doc("p15_final_closeout_checkpoint.md")
    assert "P15-D12 final closeout checkpoint" in text
    assert "no-deploy status is audited" in text
    assert "patch proposals remain review-only" in text
    assert "no real trading is enabled" in text
