import subprocess


import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", PROJECT_ROOT.parent))
SAFE_TEMP_ROOT = (LOCAL_APP_DATA / "FCF" / "pytest-scratch").resolve()
GENERATED_OUTPUT_ALLOWLIST = (
    "runtime/learning_engine/shadow_ledger.json",
    "runtime/operator_console/ai_learning_audit_report.json",
    "runtime/operator_console/ai_learning_memory_ledger.json",
    "runtime/operator_console/p13_final_closeout_summary.json",
)


COMMANDS = [
    ["python", "scripts/run_active_surface_quality_guard.py"],
    ["python", "scripts/control_center_v2_factor_realtime_architecture_guard.py"],
    ["python", "scripts/control_center_project_memory_guard.py"],
    ["python", "scripts/control_center_future_capability_intake_guard.py"],
    ["python", "scripts/control_center_v2_r1_factor_contract_guard.py"],
    ["python", "scripts/control_center_v2_r2_historical_baseline_guard.py"],
    ["python", "scripts/control_center_v2_r3_local_event_ingress_guard.py"],
    ["python", "scripts/control_center_v2_r4_local_anomaly_radar_guard.py"],
    ["python", "scripts/control_center_v2_r5_local_cognitive_shield_guard.py"],
    ["python", "scripts/control_center_v2_r6_local_paper_scenario_guard.py"],
    ["python", "scripts/control_center_v2_r7_local_market_session_guard.py"],
    ["python", "scripts/run_safety_smoke.py"],
    ["python", "scripts/run_market_snapshot_smoke.py"],
    ["python", "scripts/run_decision_draft_smoke.py"],
    ["python", "scripts/run_operator_review_smoke.py"],
    ["python", "scripts/run_paper_pipeline_smoke.py"],
    ["python", "scripts/run_paper_analysis_report_smoke.py"],
    ["python", "scripts/run_integrated_report_smoke.py"],
    ["python", "scripts/run_analysis_flow_smoke.py"],
    ["python", "scripts/run_analysis_cli_smoke.py"],
    ["python", "scripts/run_paper_history_smoke.py"],
    ["python", "scripts/run_batch_analysis_smoke.py"],
    ["python", "scripts/run_batch_cli_smoke.py"],
    ["python", "scripts/run_batch_history_smoke.py"],
    ["python", "scripts/run_batch_quality_smoke.py"],
    ["python", "scripts/run_schema_validation_smoke.py"],
    ["python", "scripts/run_local_data_loader_smoke.py"],
    ["python", "scripts/run_local_data_bridge_smoke.py"],
    ["python", "scripts/run_local_data_handoff_smoke.py"],
    ["python", "scripts/run_p3_closeout_smoke.py"],
    ["python", "scripts/run_paper_analysis_logic_smoke.py"],
    ["python", "scripts/run_paper_analysis_pipeline_smoke.py"],
    ["python", "scripts/run_paper_review_packet_smoke.py"],
    ["python", "scripts/run_paper_readable_report_smoke.py"],
    ["python", "scripts/run_p4_closeout_smoke.py"],
    ["python", "scripts/run_paper_risk_governance_smoke.py"],
    ["python", "scripts/run_paper_governance_audit_smoke.py"],
    ["python", "scripts/run_paper_governance_report_smoke.py"],
    ["python", "scripts/run_paper_governance_contract_smoke.py"],
    ["python", "scripts/run_p5_closeout_smoke.py"],
    ["python", "scripts/run_paper_multi_market_smoke.py"],
    ["python", "scripts/run_paper_multi_market_pipeline_smoke.py"],
    ["python", "scripts/run_paper_multi_market_report_smoke.py"],
    ["python", "scripts/run_paper_multi_market_registry_smoke.py"],
    ["python", "scripts/run_p6_closeout_smoke.py"],
    ["python", "scripts/run_paper_operator_console_smoke.py"],
    ["python", "scripts/run_paper_operator_workflow_smoke.py"],
    ["python", "scripts/run_paper_operator_console_report_smoke.py"],
    ["python", "scripts/run_paper_operator_console_acceptance_smoke.py"],
    ["python", "scripts/run_p7_closeout_smoke.py"],
    ["python", "scripts/run_paper_learning_memory_smoke.py"],
    ["python", "scripts/run_paper_learning_audit_smoke.py"],
    ["python", "scripts/run_paper_learning_ui_smoke.py"],
    ["python", "scripts/run_paper_learning_readiness_smoke.py"],
    ["python", "scripts/run_p8_closeout_smoke.py"],
    ["python", "scripts/run_paper_backtest_baseline_smoke.py"],
    ["python", "scripts/run_paper_backtest_metrics_smoke.py"],
    ["python", "scripts/run_paper_calibration_proposal_smoke.py"],
    ["python", "scripts/run_paper_calibration_readiness_smoke.py"],
    ["python", "scripts/run_p9_closeout_smoke.py"],
    ["python", "scripts/run_paper_model_registry_smoke.py"],
    ["python", "scripts/run_paper_model_card_smoke.py"],
    ["python", "scripts/run_paper_model_registry_ui_smoke.py"],
    ["python", "scripts/run_paper_model_registry_readiness_smoke.py"],
    ["python", "scripts/run_p10_model_registry_closeout_smoke.py"],
    ["python", "scripts/run_paper_deployment_handoff_smoke.py"],
    ["python", "scripts/run_paper_deployment_preflight_smoke.py"],
    ["python", "scripts/run_paper_deployment_dry_run_smoke.py"],
    ["python", "scripts/run_paper_deployment_dry_run_report_smoke.py"],
    ["python", "scripts/run_p11_paper_deployment_closeout_smoke.py"],
    ["python", "scripts/run_paper_final_release_package_smoke.py"],
    ["python", "scripts/run_paper_final_release_acceptance_smoke.py"],
    ["python", "scripts/run_paper_final_release_archive_smoke.py"],
    ["python", "scripts/run_paper_final_release_archive_acceptance_smoke.py"],
    ["python", "scripts/run_p12_final_archive_closeout_smoke.py"],
    ["python", "scripts/run_p13_operator_console_smoke.py"],
    ["python", "scripts/run_p13_operator_console_launcher_smoke.py"],
    ["python", "scripts/run_p13_operator_console_snapshot_smoke.py"],
    ["python", "scripts/run_p13_operator_console_review_packet_smoke.py"],
    ["python", "scripts/run_p13_operator_console_acceptance_smoke.py"],
    ["python", "scripts/run_p13_branch_closeout_smoke.py"],
    ["python", "scripts/run_p13_ai_learning_boundary_smoke.py"],
    ["python", "scripts/run_p13_ai_learning_memory_ledger_smoke.py"],
    ["python", "scripts/run_p13_ai_learning_audit_report_smoke.py"],
    ["python", "scripts/run_p13_final_closeout_summary_smoke.py"],
    ["python", "scripts/run_p14_regime_taxonomy_smoke.py"],
    ["python", "scripts/run_p14_shadow_ledger_smoke.py"],
    ["python", "scripts/run_p14_expert_trust_score_smoke.py"],
    ["python", "scripts/run_p14_feature_source_audit_smoke.py"],
    ["python", "scripts/run_p14_risk_adjusted_trust_score_smoke.py"],
    ["python", "scripts/run_p14_feature_orthogonality_audit_smoke.py"],
    ["python", "scripts/run_p14_alpha_decay_profiling_smoke.py"],
    ["python", "scripts/run_p14_meta_anomaly_detection_smoke.py"],
    ["python", "scripts/run_p14_governor_weight_proposal_smoke.py"],
    ["python", "scripts/run_p14_scenario_engine_smoke.py"],
    ["python", "scripts/run_p14_patch_proposal_sandbox_smoke.py"],
    ["python", "scripts/run_p14_data_quality_sentry_smoke.py"],
    ["python", "scripts/run_p14_explanation_consistency_check_smoke.py"],
    ["python", "scripts/run_p14_learning_engine_closeout_smoke.py"],
    ["python", "scripts/run_p14_merge_readiness_bridge_smoke.py"],
    ["python", "scripts/run_p14_final_operator_acceptance_packet_smoke.py"],
    ["python", "scripts/run_p14_final_archive_manifest_smoke.py"],
    ["python", "scripts/run_p14_final_branch_handoff_smoke.py"],
    ["python", "scripts/run_p14_human_merge_plan_smoke.py"],
    ["python", "scripts/run_p14_human_release_plan_smoke.py"],
    ["python", "scripts/run_p14_final_completion_receipt_smoke.py"],
    ["python", "main.py", "--symbol", "BTCUSDT", "--price", "65000"],
    ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"],
]


def run_command(command: list[str]) -> None:
    print("")
    print("== RUN:", " ".join(command), "==")
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["TEMP"] = str(SAFE_TEMP_ROOT)
    environment["TMP"] = str(SAFE_TEMP_ROOT)
    completed = subprocess.run(command, check=False, env=environment)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    try:
        SAFE_TEMP_ROOT.relative_to(PROJECT_ROOT)
    except ValueError:
        pass
    else:
        raise SystemExit("safe temporary root must remain outside the repository")
    SAFE_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    probe = SAFE_TEMP_ROOT / "fcf-write-probe"
    probe.mkdir(exist_ok=False)
    probe.rmdir()
    snapshots = {
        relative: (PROJECT_ROOT / relative).read_bytes()
        for relative in GENERATED_OUTPUT_ALLOWLIST
    }
    try:
        for command in COMMANDS:
            run_command(command)
    finally:
        for relative, content in snapshots.items():
            target = PROJECT_ROOT / relative
            if target.read_bytes() != content:
                target.write_bytes(content)

    print("")
    print("== ALL CHECKS PASSED ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())







































