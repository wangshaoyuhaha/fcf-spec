import json
from pathlib import Path

SCHEMA_DOC = Path("docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_SCHEMA_D2.md")
FIXTURE = Path("tests/fixtures/ui_risk_flag_visibility/d2_visibility_packet.json")

PROTECTED_FIELDS = [
    "risk_flags",
    "reason_codes",
    "review_status",
    "blocked_reasons",
    "conflict_signals",
    "missing_required_fields",
    "unsafe_permissions",
    "operator_review_required",
    "circuit_break",
    "correlation_id",
    "source_artifact",
    "evidence_chain_status",
]


def test_d2_schema_document_exists_and_declares_boundaries():
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    assert "sidecar-only" in text
    assert "P1-P47 冻结" in text
    assert "禁止 P48" in text
    assert "禁止 core mutation" in text
    assert "paper-only" in text
    assert "operator review required" in text


def test_d2_schema_lists_all_protected_fields():
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    for field in PROTECTED_FIELDS:
        assert field in text


def test_d2_schema_requires_review_required_and_circuit_break_non_downgrade():
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    assert "REVIEW_REQUIRED 不得自动通过" in text
    assert "CIRCUIT_BREAK 不允许降级" in text


def test_d2_schema_requires_operator_review_for_conflict_missing_and_unsafe():
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    assert "任何 conflict_signals 都必须进入 operator review" in text
    assert "任何 missing_required_fields 都必须进入 operator review" in text
    assert "任何 unsafe_permissions 都必须进入 operator review" in text


def test_d2_fixture_contains_all_protected_fields():
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for field in PROTECTED_FIELDS:
        assert field in packet


def test_d2_fixture_preserves_review_required_reason_codes_and_visibility_flags():
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert packet["review_status"] == "REVIEW_REQUIRED"
    assert packet["operator_review_required"] is True
    assert "REVIEW_REQUIRED" in packet["risk_flags"]
    assert "CONFLICT_SIGNAL" in packet["risk_flags"]
    assert "MISSING_REQUIRED_FIELD" in packet["reason_codes"]
    assert "UNSAFE_PERMISSION" in packet["reason_codes"]
    assert packet["missing_required_fields"]
    assert packet["unsafe_permissions"]
    assert packet["evidence_chain_status"] == "incomplete"
