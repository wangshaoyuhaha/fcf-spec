import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", PROJECT_ROOT.parent))
SAFE_TEMP_ROOT = (LOCAL_APP_DATA / "FCF-pytest-scratch-v2").resolve()
GENERATED_OUTPUT_ALLOWLIST = (
    "runtime/learning_engine/shadow_ledger.json",
    "runtime/operator_console/status_snapshot.json",
    "runtime/operator_console/operator_review_packet.json",
    "runtime/operator_console/acceptance_summary.json",
    "runtime/operator_console/p13_branch_closeout_manifest.json",
    "runtime/operator_console/ai_learning_audit_report.json",
    "runtime/operator_console/ai_learning_memory_ledger.json",
    "runtime/operator_console/p13_final_closeout_summary.json",
)


COMMANDS = [
    ["python", "scripts/run_active_surface_quality_guard.py"],
    ["python", "scripts/control_center_v2_factor_realtime_architecture_guard.py"],
    ["python", "scripts/control_center_project_memory_guard.py"],
    ["python", "scripts/control_center_future_capability_intake_guard.py"],
    [
        "python",
        "scripts/control_center_fcp_0001_data_entitlement_provenance_readiness_guard.py",
    ],
    ["python", "scripts/control_center_fcp_0002_counterfactual_decision_journal_guard.py"],
    ["python", "scripts/control_center_fcp_0003_correlated_evidence_confidence_budget_guard.py"],
    [
        "python",
        "scripts/control_center_fcp_0004_institutional_calendar_causal_intelligence_reconciliation_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0005_mvp_product_readiness_decision_gate_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0006_a_share_mvp_target_data_acceptance_baseline_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0007_a_share_rqdata_demo_artifact_intake_replay_acceptance_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0008_chinese_browser_console_local_data_intake_preview_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0009_provider_neutral_market_data_adapter_readiness_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0010_simplified_chinese_console_localization_consistency_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0011_candidate_data_source_onboarding_evidence_review_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0012_sanitized_candidate_data_session_evidence_intake_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0013_candidate_data_evidence_bundle_reconciliation_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0014_candidate_data_evidence_gap_remediation_plan_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0015_candidate_evidence_console_launch_routing_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0016_trusted_data_supply_chain_cost_aware_source_routing_architecture_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0018_btc_trusted_market_data_substrate_local_replay_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0019_a_share_local_export_canonicalization_bridge_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0020_governance_successor_state_scalability_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0021_a_share_cross_source_quality_reconciliation_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0022_btc_local_export_canonicalization_bridge_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0023_btc_cross_source_venue_quality_reconciliation_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0024_cross_market_registered_data_readiness_review_packet_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0025_registered_data_readiness_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0026_registered_data_authority_exactness_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0027_registered_data_primitive_type_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0028_registered_bridge_result_lineage_coherence_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0029_a_share_daily_calibration_result_lineage_coherence_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0030_btc_replay_report_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0031_btc_cross_source_reconciliation_dataset_lineage_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0032_a_share_cross_source_reconciliation_dataset_lineage_authority_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0033_cross_market_readiness_dataset_lineage_visibility_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0034_btc_perpetual_leverage_paper_research_architecture_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0035_guojin_qmt_registered_local_daily_export_profile_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0036_guojin_qmt_registered_local_daily_batch_coverage_reconciliation_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0037_a_share_registered_expected_trading_date_artifact_profile_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0039_a_share_cross_source_artifact_independence_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0040_a_share_same_calendar_cross_source_field_delta_diagnostic_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0041_a_share_cross_source_row_delta_evidence_ledger_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0042_a_share_cross_source_operator_delta_review_packet_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0043_a_share_cross_source_operator_delta_review_receipt_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0044_a_share_cross_source_operator_review_receipt_ledger_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0045_btc_cross_source_exact_observation_delta_evidence_ledger_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0047_btc_perpetual_margin_risk_tier_evidence_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0048_btc_perpetual_funding_method_schedule_evidence_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0049_btc_perpetual_fee_rebate_schedule_evidence_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0050_guojin_qmt_registered_dual_export_quality_evidence_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0051_guojin_qmt_historical_coverage_completeness_gate_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0052_guojin_qmt_coverage_supplement_lineage_integrity_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0053_btc_perpetual_rule_bundle_point_in_time_coherence_gate_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0054_btc_perpetual_mark_index_liquidation_mechanics_evidence_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0055_btc_perpetual_complete_rule_bundle_coherence_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0059_btc_perpetual_paper_stress_evaluation_input_domain_semantics_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0060_btc_perpetual_paper_stress_evaluation_readiness_coherence_gate_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0061_btc_perpetual_paper_stress_scenario_parameter_domain_semantics_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0063_btc_perpetual_paper_stress_evaluation_operand_schema_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0065_btc_perpetual_paper_stress_evaluation_context_coherence_gate_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0068_btc_perpetual_paper_stress_evaluation_trigger_predicate_semantics_registry_guard.py",
    ],
    [
        "python",
        "scripts/control_center_fcp_0069_btc_perpetual_paper_stress_evaluation_input_binding_registry_guard.py",
    ],
    ["python", "scripts/control_center_v2_r1_factor_contract_guard.py"],
    ["python", "scripts/control_center_v2_r2_historical_baseline_guard.py"],
    ["python", "scripts/control_center_v2_r3_local_event_ingress_guard.py"],
    ["python", "scripts/control_center_v2_r4_local_anomaly_radar_guard.py"],
    ["python", "scripts/control_center_v2_r5_local_cognitive_shield_guard.py"],
    ["python", "scripts/control_center_v2_r6_local_paper_scenario_guard.py"],
    ["python", "scripts/control_center_v2_r7_local_market_session_guard.py"],
    ["python", "scripts/control_center_v2_r8_local_same_time_baseline_guard.py"],
    ["python", "scripts/control_center_v2_r9_local_volume_ratio_guard.py"],
    ["python", "scripts/control_center_v2_r10_local_turnover_guard.py"],
    ["python", "scripts/control_center_v2_r11_local_factor_registry_guard.py"],
    ["python", "scripts/control_center_v2_r12_local_technical_indicator_guard.py"],
    ["python", "scripts/control_center_v2_r13_local_momentum_indicator_guard.py"],
    ["python", "scripts/control_center_v2_r14_local_trend_indicator_guard.py"],
    ["python", "scripts/control_center_v2_r15_local_volatility_indicator_guard.py"],
    ["python", "scripts/control_center_v2_r16_local_range_channel_indicator_guard.py"],
    ["python", "scripts/control_center_v2_r17_local_stochastic_oscillator_guard.py"],
    ["python", "scripts/control_center_v2_r18_local_directional_trend_strength_guard.py"],
    ["python", "scripts/control_center_v2_r19_local_percentage_price_oscillator_guard.py"],
    ["python", "scripts/control_center_v2_r20_local_triple_exponential_oscillator_guard.py"],
    ["python", "scripts/control_center_v2_r21_local_robust_normalization_guard.py"],
    ["python", "scripts/control_center_v2_r22_local_robust_normalization_integrity_guard.py"],
    ["python", "scripts/control_center_v2_r23_local_institutional_calendar_evidence_guard.py"],
    ["python", "scripts/control_center_v2_r24_local_multi_clock_event_state_guard.py"],
    ["python", "scripts/control_center_v2_r25_local_causal_transmission_graph_guard.py"],
    ["python", "scripts/control_center_v2_r26_local_consensus_expectation_gap_guard.py"],
    ["python", "scripts/control_center_v2_r27_local_event_reaction_quality_guard.py"],
    ["python", "scripts/control_center_v2_r28_local_a_share_earnings_accounting_quality_guard.py"],
    ["python", "scripts/control_center_v2_r29_local_index_futures_basis_roll_expiry_guard.py"],
    ["python", "scripts/control_center_v2_r30_local_equity_supply_pressure_guard.py"],
    ["python", "scripts/control_center_v2_r31_local_fx_transmission_sensitivity_guard.py"],
    ["python", "scripts/control_center_v2_r32_local_institutional_crowding_guard.py"],
    ["python", "scripts/control_center_v2_r33_local_holiday_liquidity_state_guard.py"],
    ["python", "scripts/control_center_v2_r34_local_policy_window_language_evidence_guard.py"],
    ["python", "scripts/control_center_v2_r35_local_evidence_integrity_guard.py"],
    ["python", "scripts/control_center_v2_r36_local_institutional_factor_lifecycle_guard.py"],
    ["python", "scripts/control_center_v2_r37_local_factor_validation_evidence_guard.py"],
    ["python", "scripts/control_center_v2_r38_local_operator_factor_governance_projection_guard.py"],
    ["python", "scripts/control_center_v2_r39_browser_operator_factor_governance_projection_guard.py"],
    ["python", "scripts/control_center_v2_r40_browser_factor_governance_field_presentation_guard.py"],
    ["python", "scripts/control_center_v2_r41_browser_governance_starter_package_guard.py"],
    ["python", "scripts/control_center_v2_r42_browser_governance_attention_summary_guard.py"],
    ["python", "scripts/control_center_v2_r43_browser_governance_review_queue_guard.py"],
    ["python", "scripts/control_center_v2_r44_browser_governance_review_evidence_trace_guard.py"],
    ["python", "scripts/control_center_v2_r45_browser_governance_review_reason_summary_guard.py"],
    ["python", "scripts/control_center_v2_r46_browser_governance_review_coverage_summary_guard.py"],
    ["python", "scripts/control_center_v2_r47_browser_governance_review_market_summary_guard.py"],
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







































