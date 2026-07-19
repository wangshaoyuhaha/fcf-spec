from pathlib import Path

import scripts.run_active_surface_quality_guard as active_surface_guard
import scripts.run_all_checks as run_all_checks


EXPECTED_GENERATED_OUTPUTS = (
    "runtime/learning_engine/shadow_ledger.json",
    "runtime/operator_console/status_snapshot.json",
    "runtime/operator_console/operator_review_packet.json",
    "runtime/operator_console/acceptance_summary.json",
    "runtime/operator_console/p13_branch_closeout_manifest.json",
    "runtime/operator_console/ai_learning_audit_report.json",
    "runtime/operator_console/ai_learning_memory_ledger.json",
    "runtime/operator_console/p13_final_closeout_summary.json",
)


def test_generated_output_allowlists_are_exact_and_synchronized():
    assert run_all_checks.GENERATED_OUTPUT_ALLOWLIST == EXPECTED_GENERATED_OUTPUTS
    assert active_surface_guard.GENERATED_OUTPUT_ALLOWLIST == EXPECTED_GENERATED_OUTPUTS


def test_run_all_restores_every_allowlisted_output(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    scratch_root = tmp_path / "scratch"
    original = b"registered-original\n"

    for relative in EXPECTED_GENERATED_OUTPUTS:
        target = project_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original)

    def overwrite_outputs(_command):
        for relative in EXPECTED_GENERATED_OUTPUTS:
            (project_root / relative).write_bytes(b"generated-change\n")

    monkeypatch.setattr(run_all_checks, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(run_all_checks, "SAFE_TEMP_ROOT", scratch_root)
    monkeypatch.setattr(run_all_checks, "COMMANDS", (("python", "fake.py"),))
    monkeypatch.setattr(run_all_checks, "run_command", overwrite_outputs)

    assert run_all_checks.main() == 0
    assert all(
        (project_root / relative).read_bytes() == original
        for relative in EXPECTED_GENERATED_OUTPUTS
    )
    assert tuple(scratch_root.iterdir()) == ()
