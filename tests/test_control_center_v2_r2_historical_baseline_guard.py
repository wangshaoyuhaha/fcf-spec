from pathlib import Path

from scripts.control_center_v2_r2_historical_baseline_guard import (
    APP_FILES,
    DOCS,
    build_v2_r2_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def test_v2_r2_guard_passes_repository():
    report = build_v2_r2_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_r2_guard_main_passes():
    assert main() == 0


def test_v2_r2_surface_and_docs_are_exact():
    assert len(APP_FILES) == 8
    assert len(DOCS) == 6
    assert all((ROOT / path).is_file() for path in DOCS)
