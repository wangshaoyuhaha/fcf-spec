from scripts.control_center_handoff_freshness_guard import (
    HandoffFreshnessBaseline,
    validate_handoff_freshness_contract,
)


def _baseline() -> HandoffFreshnessBaseline:
    return HandoffFreshnessBaseline(
        latest_main_commit="b757644",
        latest_phase="CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1",
        merge_commit="2feba64",
        d6_commit="36db8f6",
        pytest_passed_count=1782,
        run_all_checks_passed=True,
    )


def _fresh_text() -> str:
    return """
    latest main commit: b757644
    latest phase: CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
    latest merge commit: 2feba64
    latest D6 commit: 36db8f6
    python -m pytest -q = 1782 passed
    run_all_checks passed
    paper-only
    local-only
    read-only governance validation
    sidecar-only
    operator review required
    no P48
    no core mutation
    no real trading
    no broker API
    no exchange API
    no API key
    no buy button
    no sell button
    no order button
    no tag
    no release
    no deploy
    """


def test_accepts_fresh_handoff_contract():
    result = validate_handoff_freshness_contract(_fresh_text(), _baseline())
    assert result.passed is True
    assert result.reason_codes == ()


def test_blocks_missing_latest_main_commit():
    text = _fresh_text().replace("b757644", "")
    result = validate_handoff_freshness_contract(text, _baseline())
    assert result.passed is False
    assert "MISSING_CURRENT_BASELINE_VALUE" in result.reason_codes


def test_blocks_stale_commit_reference():
    text = _fresh_text() + "\nc3e6ae1\n"
    result = validate_handoff_freshness_contract(
        text,
        _baseline(),
        stale_commits=("c3e6ae1",),
    )
    assert result.passed is False
    assert "STALE_COMMIT_REFERENCE" in result.reason_codes


def test_blocks_stale_phase_reference():
    text = _fresh_text() + "\nCONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1\n"
    result = validate_handoff_freshness_contract(
        text,
        _baseline(),
        stale_phases=("CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1",),
    )
    assert result.passed is False
    assert "STALE_PHASE_REFERENCE" in result.reason_codes


def test_blocks_stale_pytest_count_reference():
    text = _fresh_text() + "\n1781 passed\n"
    result = validate_handoff_freshness_contract(
        text,
        _baseline(),
        stale_pytest_counts=(1781,),
    )
    assert result.passed is False
    assert "STALE_PYTEST_COUNT_REFERENCE" in result.reason_codes


def test_blocks_unsafe_runtime_reference():
    text = _fresh_text() + "\nreal order\n"
    result = validate_handoff_freshness_contract(text, _baseline())
    assert result.passed is False
    assert "UNSAFE_RUNTIME_REFERENCE" in result.reason_codes
