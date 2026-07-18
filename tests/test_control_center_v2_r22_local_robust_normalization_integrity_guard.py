from scripts.control_center_v2_r22_local_robust_normalization_integrity_guard import build_v2_r22_guard_report, main


def test_v2_r22_guard_passes_repository() -> None:
    report = build_v2_r22_guard_report(); assert report["ok"] is True; assert all(report["checks"].values())


def test_v2_r22_guard_main_passes() -> None: assert main() == 0


def test_v2_r22_guard_locks_all_repaired_invariants() -> None:
    checks = build_v2_r22_guard_report()["checks"]; assert checks["instrument_identity_closed"] is True; assert checks["evidence_state_closed"] is True
