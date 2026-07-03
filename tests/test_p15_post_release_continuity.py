from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p15_post_release_continuity_checkpoint_records_release_anchor():
    text = read_doc("p15_post_release_continuity_checkpoint.md")

    assert "v14-learning-engine-paper" in text
    assert "5188158 merge P14 learning engine into main" in text
    assert "GitHub Release published" in text
    assert "no deploy performed" in text


def test_p15_post_release_safety_manifest_preserves_no_real_trading_boundary():
    text = read_doc("p15_post_release_safety_manifest.md")

    assert "paper-only" in text
    assert "no real exchange API" in text
    assert "no real orders" in text
    assert "no auto-deploy" in text


def test_p15_next_phase_candidate_plan_stays_read_only_and_paper_only():
    text = read_doc("p15_next_phase_candidate_plan.md")

    assert "read-only indexes" in text
    assert "patch proposal review queue" in text
    assert "real exchange integration" in text
    assert "auto-trading" in text
