from pathlib import Path


DOC_PATH = Path("docs/CONTROL_CENTER_GLOBAL_SCAN_CLASSIFICATION_GUARD_APP_1_D1_CONTRACT.md")


def test_global_scan_classification_contract_exists():
    assert DOC_PATH.exists()


def test_global_scan_classification_contract_labels_defined():
    text = DOC_PATH.read_text(encoding="utf-8")
    labels = [
        "EXPECTED_GOVERNANCE_TEXT",
        "EXPECTED_TEST_ASSERTION",
        "EXPECTED_FINAL_STATE_HISTORY",
        "EXPECTED_SAFETY_BOUNDARY",
        "ACTIONABLE_STALE_STATE",
        "ACTIONABLE_UNSAFE_PERMISSION",
        "ACTIONABLE_STRUCTURE_GAP",
    ]
    for label in labels:
        assert label in text


def test_global_scan_classification_contract_actionable_review_required():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "ACTIONABLE_STALE_STATE" in text
    assert "ACTIONABLE_UNSAFE_PERMISSION" in text
    assert "ACTIONABLE_STRUCTURE_GAP" in text
    assert "always require review" in text


def test_global_scan_classification_contract_expected_hits_remain_visible():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "Expected labels do not delete the hit" in text
    assert "Expected labels do not remove audit visibility" in text


def test_global_scan_classification_contract_non_downgrade_rule():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "Non-Downgrade Rule" in text
    assert "must not be downgraded" in text


def test_global_scan_classification_contract_safety_boundary_preserved():
    text = DOC_PATH.read_text(encoding="utf-8")
    required = [
        "paper-only",
        "local-only",
        "read-only",
        "sidecar-only",
        "operator-review-required",
        "must not",
        "create P48",
        "mutate frozen core P1-P47",
        "broker APIs",
        "exchange APIs",
        "API keys",
        "wallet keys",
        "buy, sell, or order",
        "deploy anything",
        "create release tags",
        "bypass operator review",
    ]
    for item in required:
        assert item in text
