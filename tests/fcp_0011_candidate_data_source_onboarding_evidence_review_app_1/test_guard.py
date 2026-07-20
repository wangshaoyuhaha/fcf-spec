from scripts.control_center_fcp_0011_candidate_data_source_onboarding_evidence_review_guard import (
    build_fcp_0011_guard_report,
    main,
)


def test_fcp_0011_guard_passes_repository() -> None:
    report = build_fcp_0011_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0011_guard_main_passes() -> None:
    assert main() == 0
