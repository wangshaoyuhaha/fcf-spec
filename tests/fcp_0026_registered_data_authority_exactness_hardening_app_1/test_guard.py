from scripts.control_center_fcp_0026_registered_data_authority_exactness_hardening_guard import (
    build_fcp_0026_guard_report,
    main,
)


def test_fcp_0026_guard_passes_repository():
    assert build_fcp_0026_guard_report()["ok"] is True


def test_fcp_0026_guard_main_passes():
    assert main() == 0
