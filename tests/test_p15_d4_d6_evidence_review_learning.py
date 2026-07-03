from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p15_d4_release_evidence_index_records_tag_release_and_no_deploy():
    text = read_doc("p15_release_evidence_index.md")
    assert "v14-learning-engine-paper" in text
    assert "5188158 merge P14 learning engine into main" in text
    assert "GitHub Release exists" in text
    assert "no deploy was performed" in text


def test_p15_d5_operator_review_history_keeps_human_gate():
    text = read_doc("p15_operator_review_history_index.md")
    assert "operator review is required" in text
    assert "no auto-merge" in text
    assert "no auto-release" in text
    assert "no auto-deploy" in text


def test_p15_d6_learning_memory_browser_plan_is_read_only():
    text = read_doc("p15_learning_memory_browser_plan.md")
    assert "read-only local index" in text
    assert "shadow ledger summary" in text
    assert "parameter auto-update" in text
    assert "real execution" in text
