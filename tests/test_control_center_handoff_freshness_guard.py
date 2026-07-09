from pathlib import Path

from scripts.control_center_handoff_freshness_guard import (
    HandoffFreshnessBaseline,
    discover_handoff_source_paths,
    load_handoff_sources,
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


def test_discovers_exact_handoff_sources_and_current_state_files(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md").write_text("cc", encoding="utf-8")
    (tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md").write_text("handoff", encoding="utf-8")
    (tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md").write_text("prompt", encoding="utf-8")
    (tmp_path / "FCF_CURRENT_STATE_TEST_FINAL.md").write_text("state", encoding="utf-8")
    (tmp_path / "ignored.md").write_text("ignored", encoding="utf-8")

    paths = discover_handoff_source_paths(tmp_path)
    relatives = [path.relative_to(tmp_path).as_posix() for path in paths]

    assert "docs/FCF_PROJECT_CONTROL_CENTER.md" in relatives
    assert "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md" in relatives
    assert "FCF_NEW_WINDOW_CHAT_PROMPT.md" in relatives
    assert "FCF_CURRENT_STATE_TEST_FINAL.md" in relatives
    assert "ignored.md" not in relatives


def test_loads_handoff_sources_as_utf8_records(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md").write_text("control center", encoding="utf-8")
    (tmp_path / "FCF_CURRENT_STATE_ALPHA_FINAL.md").write_text("alpha state", encoding="utf-8")

    records = load_handoff_sources(tmp_path)

    assert {record.relative_path for record in records} == {
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "FCF_CURRENT_STATE_ALPHA_FINAL.md",
    }
    assert {record.text for record in records} == {"control center", "alpha state"}


def test_missing_optional_sources_are_ignored(tmp_path: Path):
    records = load_handoff_sources(tmp_path)
    assert records == ()


def test_extracts_commit_hashes_in_stable_order():
    from scripts.control_center_handoff_freshness_guard import extract_commit_hashes

    text = "b757644 2feba64 b757644 36db8f6"
    assert extract_commit_hashes(text) == ("b757644", "2feba64", "36db8f6")


def test_extracts_pytest_passed_counts_in_stable_order():
    from scripts.control_center_handoff_freshness_guard import extract_pytest_counts

    text = "1782 passed, 1791 passed, 1782 passed"
    assert extract_pytest_counts(text) == (1782, 1791)


def test_extracts_phase_tokens_in_stable_order():
    from scripts.control_center_handoff_freshness_guard import extract_phase_tokens

    text = """
    CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
    CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1
    CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
    """
    assert extract_phase_tokens(text) == (
        "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1",
        "CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1",
    )


def test_builds_handoff_freshness_snapshot():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffSourceRecord,
        build_handoff_freshness_snapshot,
    )

    record = HandoffSourceRecord(
        relative_path="FCF_CURRENT_STATE_TEST_FINAL.md",
        text="""
        b757644
        1782 passed
        CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
        """,
    )

    snapshot = build_handoff_freshness_snapshot(record)

    assert snapshot.relative_path == "FCF_CURRENT_STATE_TEST_FINAL.md"
    assert snapshot.commit_hashes == ("b757644",)
    assert snapshot.pytest_counts == (1782,)
    assert snapshot.phase_tokens == ("CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1",)
    assert snapshot.text_length == len(record.text)


def test_builds_handoff_freshness_snapshots_for_records():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffSourceRecord,
        build_handoff_freshness_snapshots,
    )

    records = (
        HandoffSourceRecord("a.md", "b757644 1782 passed CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1"),
        HandoffSourceRecord("b.md", "2feba64 1791 passed CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1"),
    )

    snapshots = build_handoff_freshness_snapshots(records)

    assert len(snapshots) == 2
    assert snapshots[0].relative_path == "a.md"
    assert snapshots[1].relative_path == "b.md"


def test_detects_no_drift_for_current_snapshot():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffSourceRecord,
        build_handoff_freshness_snapshot,
        detect_handoff_freshness_drift,
    )

    record = HandoffSourceRecord(
        "fresh.md",
        """
        b757644 2feba64 36db8f6
        1782 passed
        CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
        """,
    )

    snapshot = build_handoff_freshness_snapshot(record)
    drift = detect_handoff_freshness_drift(snapshot, _baseline())

    assert drift.relative_path == "fresh.md"
    assert drift.reason_codes == ()


def test_detects_missing_latest_baseline_values():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffSourceRecord,
        build_handoff_freshness_snapshot,
        detect_handoff_freshness_drift,
    )

    record = HandoffSourceRecord("stale.md", "c3e6ae1 1781 passed OLD-PHASE-APP-1")
    snapshot = build_handoff_freshness_snapshot(record)
    drift = detect_handoff_freshness_drift(snapshot, _baseline())

    assert "MISSING_LATEST_MAIN_COMMIT" in drift.reason_codes
    assert "MISSING_LATEST_MERGE_COMMIT" in drift.reason_codes
    assert "MISSING_LATEST_D6_COMMIT" in drift.reason_codes
    assert "MISSING_LATEST_PHASE" in drift.reason_codes
    assert "MISSING_LATEST_PYTEST_COUNT" in drift.reason_codes


def test_detects_stale_snapshot_values():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffSourceRecord,
        build_handoff_freshness_snapshot,
        detect_handoff_freshness_drift,
    )

    record = HandoffSourceRecord(
        "mixed.md",
        """
        b757644 2feba64 36db8f6 c3e6ae1
        1782 passed
        1781 passed
        CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1
        CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1
        """,
    )

    snapshot = build_handoff_freshness_snapshot(record)
    drift = detect_handoff_freshness_drift(
        snapshot,
        _baseline(),
        stale_commits=("c3e6ae1",),
        stale_phases=("CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1",),
        stale_pytest_counts=(1781,),
    )

    assert "STALE_COMMIT_REFERENCE" in drift.reason_codes
    assert "STALE_PHASE_REFERENCE" in drift.reason_codes
    assert "STALE_PYTEST_COUNT_REFERENCE" in drift.reason_codes


def test_detects_drift_for_multiple_snapshots():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffSourceRecord,
        build_handoff_freshness_snapshots,
        detect_handoff_freshness_drifts,
    )

    records = (
        HandoffSourceRecord(
            "fresh.md",
            "b757644 2feba64 36db8f6 1782 passed CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1",
        ),
        HandoffSourceRecord("stale.md", "c3e6ae1 1781 passed OLD-PHASE-APP-1"),
    )

    snapshots = build_handoff_freshness_snapshots(records)
    drifts = detect_handoff_freshness_drifts(snapshots, _baseline())

    assert len(drifts) == 2
    assert drifts[0].reason_codes == ()
    assert drifts[1].reason_codes


def test_builds_passing_guard_packet_when_no_drift_exists():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffDriftRecord,
        build_handoff_freshness_guard_packet,
    )

    drifts = (
        HandoffDriftRecord("a.md", ()),
        HandoffDriftRecord("b.md", ()),
    )

    packet = build_handoff_freshness_guard_packet(drifts)

    assert packet.app_id == "CONTROL-CENTER-HANDOFF-FRESHNESS-GUARD-APP-1"
    assert packet.total_sources == 2
    assert packet.blocked_sources == 0
    assert packet.passed is True
    assert packet.reason_codes == ()
    assert packet.blocked_paths == ()


def test_builds_blocking_guard_packet_when_drift_exists():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffDriftRecord,
        build_handoff_freshness_guard_packet,
    )

    drifts = (
        HandoffDriftRecord("fresh.md", ()),
        HandoffDriftRecord("stale.md", ("STALE_COMMIT_REFERENCE", "MISSING_LATEST_PHASE")),
    )

    packet = build_handoff_freshness_guard_packet(drifts)

    assert packet.total_sources == 2
    assert packet.blocked_sources == 1
    assert packet.passed is False
    assert packet.reason_codes == ("STALE_COMMIT_REFERENCE", "MISSING_LATEST_PHASE")
    assert packet.blocked_paths == ("stale.md",)


def test_guard_packet_deduplicates_reason_codes_and_paths():
    from scripts.control_center_handoff_freshness_guard import (
        HandoffDriftRecord,
        build_handoff_freshness_guard_packet,
    )

    drifts = (
        HandoffDriftRecord("a.md", ("STALE_COMMIT_REFERENCE",)),
        HandoffDriftRecord("a.md", ("STALE_COMMIT_REFERENCE", "STALE_PHASE_REFERENCE")),
    )

    packet = build_handoff_freshness_guard_packet(drifts)

    assert packet.blocked_sources == 2
    assert packet.reason_codes == ("STALE_COMMIT_REFERENCE", "STALE_PHASE_REFERENCE")
    assert packet.blocked_paths == ("a.md",)


def test_empty_guard_packet_is_passing_noop():
    from scripts.control_center_handoff_freshness_guard import build_handoff_freshness_guard_packet

    packet = build_handoff_freshness_guard_packet(())

    assert packet.total_sources == 0
    assert packet.blocked_sources == 0
    assert packet.passed is True
    assert packet.reason_codes == ()
    assert packet.blocked_paths == ()
