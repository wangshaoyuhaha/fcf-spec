from scripts.control_center_fcp_0039_a_share_cross_source_artifact_independence_integrity_hardening_guard import (
    build_fcp_0039_guard_report,
    main,
)


def test_fcp_0039_guard_passes_repository() -> None:
    report = build_fcp_0039_guard_report()

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0039_guard_main_passes() -> None:
    assert main() == 0
