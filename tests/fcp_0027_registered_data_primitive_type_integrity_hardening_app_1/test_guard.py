from scripts.control_center_fcp_0027_registered_data_primitive_type_integrity_hardening_guard import (
    build_fcp_0027_guard_report,
    main,
)


def test_fcp_0027_guard_passes_repository():
    assert build_fcp_0027_guard_report()["ok"] is True


def test_fcp_0027_guard_main_passes():
    assert main() == 0
