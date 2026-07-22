from scripts.control_center_fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_guard import (
    build_fcp_0075_guard_report,
    main,
)


def test_fcp_0075_guard_passes_repository():
    report = build_fcp_0075_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0075_guard_main_passes():
    assert main() == 0
