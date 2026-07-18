from scripts.control_center_v2_r20_local_triple_exponential_oscillator_guard import build_v2_r20_guard_report, main


def test_v2_r20_guard_passes_repository() -> None:
    report = build_v2_r20_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_r20_guard_main_passes() -> None:
    assert main() == 0


def test_v2_r20_guard_has_closed_boundary() -> None:
    assert build_v2_r20_guard_report()["checks"]["boundary_closed"] is True
