from pathlib import Path

from scripts.control_center_v2_r24_local_multi_clock_event_state_guard import (
    APP_FILES,
    APP_ROOT,
    build_v2_r24_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def test_v2_r24_guard_passes_repository() -> None:
    report = build_v2_r24_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_r24_guard_main_passes() -> None:
    assert main() == 0


def test_v2_r24_surface_is_exact() -> None:
    assert sorted(path.name for path in (ROOT / APP_ROOT).glob("*.py")) == sorted(
        APP_FILES
    )
