from pathlib import Path


DOC_PATH = Path("docs/CONTROL_CENTER_HANDOFF_STALE_MARKER_CLEANUP_GUARD_APP_1_D1_CONTRACT.md")


def test_d1_contract_exists():
    assert DOC_PATH.exists()


def test_d1_contract_names_phase_and_purpose():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "CONTROL-CENTER-HANDOFF-STALE-MARKER-CLEANUP-GUARD-APP-1" in text
    assert "Handoff Stale Marker Cleanup Contract" in text


def test_d1_contract_separates_historical_and_actionable_stale_markers():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "EXPECTED_FINAL_STATE_HISTORY" in text
    assert "ACTIONABLE_STALE_STATE" in text
    assert "Historical archived stale markers" in text
    assert "Current-entry stale markers" in text


def test_d1_contract_limits_scope_to_control_and_handoff_docs():
    text = DOC_PATH.read_text(encoding="utf-8")
    required_paths = [
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        "FCF_NEW_WINDOW_CHAT_PROMPT.md",
        "docs/HANDOFF_PROMPT.md",
    ]
    for path in required_paths:
        assert path in text


def test_d1_contract_current_state_truth_requirements():
    text = DOC_PATH.read_text(encoding="utf-8")
    required = [
        "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed",
        "main merge commit is ad16c03",
        "final handoff sync commit is 8c18573",
        "validation is 1884 passed",
        "git status is clean",
        "origin/main is synced",
    ]
    for item in required:
        assert item in text


def test_d1_contract_safety_boundary_preserved():
    text = DOC_PATH.read_text(encoding="utf-8")
    required = [
        "paper-only",
        "local-only",
        "sidecar-only",
        "operator review required",
        "no P48",
        "no P1-P47 core mutation",
        "no source code mutation",
        "no runtime mutation",
        "no real trading",
        "no real execution",
        "no broker API",
        "no exchange API",
        "no API key",
        "no wallet private key",
        "no buy / sell / order",
        "no tag",
        "no release",
        "no deploy",
    ]
    for item in required:
        assert item in text


def test_d1_contract_no_cleanup_performed_yet():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "no handoff cleanup is performed yet" in text
