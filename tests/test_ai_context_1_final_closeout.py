from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecar" / "ai_context_1_final_closeout.md"


def test_ai_context_1_final_closeout_doc_exists_and_preserves_boundary():
    text = DOC.read_text(encoding="ascii")
    assert "AI-CONTEXT-1 Final Closeout" in text
    assert "Status: completed" in text
    assert "D1 sidecar boundary and explanation contract" in text
    assert "D6 final handoff to UI-APP workflow" in text
    assert "no score mutation" in text
    assert "no reason code fabrication" in text
    assert "no risk flag suppression" in text
    assert "no buy instruction" in text
    assert "no sell instruction" in text
    assert "no limit-up guarantee" in text
    assert "no real trading" in text
    assert "operator review required" in text
    assert "merge to main requires operator review" in text
