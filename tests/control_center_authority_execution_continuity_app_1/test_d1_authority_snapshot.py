from pathlib import Path

from scripts.control_center_active_authority_sync_guard import (
    ACTIVE_AUTHORITY_PATHS,
    AuthorityBaseline,
    inspect_active_authority,
)


def _baseline() -> AuthorityBaseline:
    return AuthorityBaseline(
        phase_id="LATEST-APP-1",
        main_merge_commit="1" * 40,
        d6_commit="2" * 40,
        final_marker="LATEST FINAL SYNC START",
    )


def test_d1_registry_contains_all_five_active_authority_sources():
    assert len(ACTIVE_AUTHORITY_PATHS) == 5
    assert "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md" in ACTIVE_AUTHORITY_PATHS


def test_d1_snapshot_reports_each_required_truth_value(tmp_path: Path):
    baseline = _baseline()
    content = (
        f"{baseline.phase_id}\n{baseline.main_merge_commit}\n"
        f"{baseline.d6_commit}\n{baseline.final_marker}\n"
    )
    for relative in ACTIVE_AUTHORITY_PATHS:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    states = inspect_active_authority(tmp_path, baseline)

    assert len(states) == 5
    assert all(state.exists for state in states)
    assert all(state.has_phase for state in states)
    assert all(state.has_main_merge for state in states)
    assert all(state.has_d6 for state in states)
    assert all(state.has_final_marker for state in states)
