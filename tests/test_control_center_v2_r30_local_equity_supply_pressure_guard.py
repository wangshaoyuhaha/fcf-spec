from pathlib import Path

from scripts.control_center_v2_r30_local_equity_supply_pressure_guard import APP_FILES, APP_ROOT, build_v2_r30_guard_report, main

ROOT = Path(__file__).resolve().parents[1]


def test_v2_r30_guard_passes_repository() -> None:
    report = build_v2_r30_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_r30_guard_main_passes() -> None:
    assert main() == 0


def test_v2_r30_surface_is_exact() -> None:
    assert sorted(path.name for path in (ROOT / APP_ROOT).glob("*.py")) == sorted(APP_FILES)
