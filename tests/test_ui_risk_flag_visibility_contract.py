from pathlib import Path

CONTRACT = Path("docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_CONTRACT_D1.md")


def _text() -> str:
    assert CONTRACT.exists(), "D1 UI risk flag visibility contract is missing"
    return CONTRACT.read_text(encoding="utf-8")


def test_d1_contract_declares_sidecar_only_core_frozen_boundary():
    text = _text()
    assert "sidecar-only" in text
    assert "P1-P47 frozen" in text
    assert "no P48" in text
    assert "no core mutation" in text


def test_d1_contract_protects_risk_flags_and_reason_codes():
    text = _text()
    for required in [
        "risk_flags",
        "reason_codes",
        "review_status",
        "blocked_reasons",
        "conflict_signals",
        "missing_required_fields",
        "unsafe_permissions",
    ]:
        assert required in text


def test_d1_contract_forbids_review_required_and_circuit_break_downgrade():
    text = _text()
    assert "REVIEW_REQUIRED" in text
    assert "MUST NOT auto-pass" in text
    assert "CIRCUIT_BREAK" in text
    assert "MUST NOT downgrade" in text


def test_d1_contract_requires_operator_review_for_visible_risk_metadata():
    text = _text()
    for required in [
        "conflict signal",
        "missing required field",
        "unsafe permission",
        "operator review",
    ]:
        assert required in text
