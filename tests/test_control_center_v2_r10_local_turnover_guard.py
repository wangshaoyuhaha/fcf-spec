from scripts.control_center_v2_r10_local_turnover_guard import build_v2_r10_guard_report, main


def test_v2_r10_guard_passes_repository() -> None:
    report = build_v2_r10_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_r10_guard_main_passes() -> None:
    assert main() == 0


def test_v2_r10_guard_preserves_closed_boundary() -> None:
    report = build_v2_r10_guard_report()
    assert report["checks"]["boundary_closed"] is True
    assert report["checks"]["no_prohibited_runtime"] is True
