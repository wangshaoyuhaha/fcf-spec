from pathlib import Path

from scripts.control_center_v2_r1_factor_contract_guard import (
    APP_FILES,
    DOC_PATHS,
    FACTOR_FIELDS,
    STATE_SYNC_FIELDS,
    TARGET_FIELDS,
    build_v2_r1_factor_contract_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def test_v2_r1_factor_contract_guard_passes_repository():
    report = build_v2_r1_factor_contract_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_r1_factor_contract_guard_main_passes():
    assert main() == 0


def test_v2_r1_factor_contract_surface_is_exact_and_complete():
    assert len(APP_FILES) == 7
    assert len(DOC_PATHS) == 6
    assert len(FACTOR_FIELDS) == 48
    assert len(TARGET_FIELDS) == 27
    assert len(STATE_SYNC_FIELDS) == 16
    assert all((ROOT / path).is_file() for path in DOC_PATHS)
