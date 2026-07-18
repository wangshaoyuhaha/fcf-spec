from pathlib import Path

from scripts.control_center_v2_r37_local_factor_validation_evidence_guard import APP_FILES, APP_ROOT, build_v2_r37_guard_report, main

ROOT = Path(__file__).resolve().parents[1]


def test_guard():
    assert build_v2_r37_guard_report(ROOT)["ok"] is True


def test_main():
    assert main() == 0


def test_surface():
    assert sorted(path.name for path in (ROOT / APP_ROOT).glob("*.py")) == sorted(APP_FILES)
