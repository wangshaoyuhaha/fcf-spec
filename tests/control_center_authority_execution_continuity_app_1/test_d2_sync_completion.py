from pathlib import Path

import pytest

from scripts.control_center_active_authority_sync_guard import (
    ACTIVE_AUTHORITY_PATHS,
    AuthorityBaseline,
    assert_authority_sync_pass,
    build_authority_sync_report,
    inspect_active_authority,
    missing_final_state_pairs,
)


ROOT = Path(__file__).resolve().parents[2]


def _operator_launch_baseline() -> AuthorityBaseline:
    return AuthorityBaseline(
        phase_id="BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1",
        main_merge_commit="2cfe860ac8c9847819557da1fbb405b7e3952eaa",
        d6_commit="7083f16e7a1bb030f03f09b63f53c9fc7a110f83",
        final_marker=(
            "BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1 "
            "FINAL SYNC START"
        ),
    )


def test_d2_blocks_one_stale_authority_source(tmp_path: Path):
    baseline = _operator_launch_baseline()
    content = (
        f"{baseline.phase_id}\n{baseline.main_merge_commit}\n"
        f"{baseline.d6_commit}\n{baseline.final_marker}\n"
    )
    for relative in ACTIVE_AUTHORITY_PATHS:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    (tmp_path / ACTIVE_AUTHORITY_PATHS[1]).write_text("stale\n", encoding="utf-8")

    report = build_authority_sync_report(
        inspect_active_authority(tmp_path, baseline)
    )

    assert report.status == "BLOCKED"
    assert ACTIVE_AUTHORITY_PATHS[1] in report.blocked_paths
    with pytest.raises(ValueError, match="ACTIVE_AUTHORITY_SYNC_FAILED"):
        assert_authority_sync_pass(report)


def test_d2_repository_active_authority_is_synchronized():
    report = build_authority_sync_report(
        inspect_active_authority(ROOT, _operator_launch_baseline())
    )

    assert report.status == "PASS"
    assert_authority_sync_pass(report)


def test_d2_all_approved_current_states_have_final_pairs():
    approved = (
        "FCF_CURRENT_STATE_BROWSER_PRODUCT_CONSOLE_"
        "INTEGRATION_ACCEPTANCE_APP_1_APPROVED.md",
    )

    assert missing_final_state_pairs(ROOT, approved) == ()
