from __future__ import annotations

from collections import defaultdict

from .contracts import (
    FoundationDeliveryReceipt,
    InstitutionalArchitectureReconciliation,
    InstitutionalArchitectureRegistry,
    ReconciliationFinding,
    digest,
)


EXPECTED_GAP_IDS = tuple(f"V2-FR-GAP-{number:03d}" for number in range(71, 87))
EXPECTED_CANDIDATE_IDS = tuple(
    sorted(
        (
            "CAPITAL_TRANSMISSION_PRESSURE",
            "EARNINGS_SURPRISE",
            "EQUITY_SUPPLY_PRESSURE",
            "EVENT_REACTION_QUALITY",
            "EXPIRY_BASIS_ROLL_STRESS",
            "FX_TRANSMISSION_SENSITIVITY",
            "HOLIDAY_LIQUIDITY_STRESS",
            "INSTITUTIONAL_CROWDING",
            "POLICY_NOVELTY_ALIGNMENT",
            "WINDOW_DRESSING_PRESSURE",
        )
    )
)


_DELIVERIES = (
    (23, "local_institutional_calendar_evidence", (71, 84)),
    (24, "local_multi_clock_event_state", (72, 73)),
    (25, "local_causal_transmission_graph", (74,)),
    (26, "local_consensus_expectation_gap", (75,)),
    (27, "local_event_reaction_quality", (76,)),
    (28, "local_a_share_earnings_lifecycle_accounting_quality", (77,)),
    (29, "local_index_futures_basis_roll_expiry", (78,)),
    (30, "local_equity_supply_pressure", (79,)),
    (31, "local_fx_transmission_sensitivity", (80,)),
    (32, "local_institutional_crowding", (81,)),
    (33, "local_holiday_liquidity_state", (82,)),
    (34, "local_policy_window_language_evidence", (83,)),
    (35, "local_evidence_integrity", (84,)),
    (36, "local_institutional_factor_lifecycle", (85,)),
    (37, "local_factor_validation_evidence", (86,)),
)


def _upper_name(name: str) -> str:
    return name.upper()


def build_expected_delivery_receipts() -> tuple[FoundationDeliveryReceipt, ...]:
    receipts = []
    for stage, name, gaps in _DELIVERIES:
        app_id = f"v2_r{stage}_{name}_foundation_app_1"
        upper = _upper_name(name)
        if stage == 28:
            guard_name = "control_center_v2_r28_local_a_share_earnings_accounting_quality_guard.py"
        else:
            guard_name = f"control_center_v2_r{stage}_{name}_guard.py"
        receipts.append(
            FoundationDeliveryReceipt(
                stage_id=f"V2-R{stage}",
                app_id=app_id,
                final_state_path=(
                    f"FCF_CURRENT_STATE_V2_R{stage}_{upper}_FOUNDATION_APP_1_FINAL.md"
                ),
                guard_path=f"scripts/{guard_name}",
                test_path=(
                    f"tests/{app_id}/test_v2_r{stage}_d1_d6.py"
                ),
                gap_ids=tuple(f"V2-FR-GAP-{gap:03d}" for gap in gaps),
            )
        )
    return tuple(receipts)


EXPECTED_RECEIPTS = build_expected_delivery_receipts()
EXPECTED_BY_STAGE = {item.stage_id: item for item in EXPECTED_RECEIPTS}
EXPECTED_OVERLAP_GAP_IDS = ("V2-FR-GAP-084",)


def build_expected_architecture_registry() -> InstitutionalArchitectureRegistry:
    return InstitutionalArchitectureRegistry(
        receipts=EXPECTED_RECEIPTS,
        candidate_ids=EXPECTED_CANDIDATE_IDS,
    )


def reconcile_institutional_architecture(
    registry: InstitutionalArchitectureRegistry,
) -> InstitutionalArchitectureReconciliation:
    actual_by_stage = {item.stage_id: item for item in registry.receipts}
    expected_stages = set(EXPECTED_BY_STAGE)
    actual_stages = set(actual_by_stage)
    missing_stages = tuple(sorted(expected_stages - actual_stages))
    unexpected_stages = tuple(sorted(actual_stages - expected_stages))
    mapping_mismatches = tuple(
        sorted(
            stage
            for stage in expected_stages & actual_stages
            if actual_by_stage[stage] != EXPECTED_BY_STAGE[stage]
        )
    )

    coverage: dict[str, list[str]] = defaultdict(list)
    for receipt in registry.receipts:
        for gap_id in receipt.gap_ids:
            coverage[gap_id].append(receipt.stage_id)
    gap_coverage = tuple(
        (gap_id, tuple(sorted(coverage.get(gap_id, ()))))
        for gap_id in EXPECTED_GAP_IDS
    )
    missing_gaps = tuple(gap for gap, stages in gap_coverage if not stages)
    unexpected_overlaps = tuple(
        gap
        for gap, stages in gap_coverage
        if len(stages) > 1 and gap not in EXPECTED_OVERLAP_GAP_IDS
    )
    overlap_mismatch = tuple(
        gap
        for gap in EXPECTED_OVERLAP_GAP_IDS
        if tuple(sorted(coverage.get(gap, ()))) != ("V2-R23", "V2-R35")
    )

    actual_candidates = set(registry.candidate_ids)
    expected_candidates = set(EXPECTED_CANDIDATE_IDS)
    missing_candidates = tuple(sorted(expected_candidates - actual_candidates))
    unexpected_candidates = tuple(sorted(actual_candidates - expected_candidates))
    overclaims = tuple(
        sorted(
            receipt.stage_id
            for receipt in registry.receipts
            if receipt.production_gap_closed or receipt.factor_activation_claimed
        )
    )

    findings = []
    for code, subjects in (
        ("MISSING_DELIVERY_STAGE", missing_stages),
        ("UNEXPECTED_DELIVERY_STAGE", unexpected_stages),
        ("DELIVERY_MAPPING_MISMATCH", mapping_mismatches),
        ("MISSING_GAP_COVERAGE", missing_gaps),
        ("UNEXPECTED_GAP_OVERLAP", unexpected_overlaps),
        ("EXPECTED_GAP_OVERLAP_MISMATCH", overlap_mismatch),
        ("MISSING_RESEARCH_CANDIDATE", missing_candidates),
        ("UNEXPECTED_RESEARCH_CANDIDATE", unexpected_candidates),
        ("PRODUCTION_AUTHORITY_OVERCLAIM", overclaims),
    ):
        if subjects:
            findings.append(ReconciliationFinding(code, "BLOCKING", subjects))
    if not findings:
        findings.append(
            ReconciliationFinding(
                "EXACT_REGISTERED_LOCAL_ARCHITECTURE_RECONCILIATION",
                "INFO",
                tuple(sorted(expected_stages)),
            )
        )
    state = (
        "BLOCKED"
        if any(item.severity == "BLOCKING" for item in findings)
        else "READY_FOR_OPERATOR_REVIEW"
    )
    payload = {
        "expected_overlap_gap_ids": EXPECTED_OVERLAP_GAP_IDS,
        "factor_activation_claimed": False,
        "findings": tuple(
            (item.code, item.severity, item.subject_ids) for item in findings
        ),
        "gap_coverage": gap_coverage,
        "mapping_mismatch_stage_ids": mapping_mismatches,
        "missing_candidate_ids": missing_candidates,
        "missing_gap_ids": missing_gaps,
        "missing_stage_ids": missing_stages,
        "operator_review_required": True,
        "overclaim_stage_ids": overclaims,
        "production_gap_closure_claimed": False,
        "registry_hash": registry.registry_hash,
        "state": state,
        "unexpected_candidate_ids": unexpected_candidates,
        "unexpected_stage_ids": unexpected_stages,
    }
    return InstitutionalArchitectureReconciliation(
        state=state,
        registry_hash=registry.registry_hash,
        findings=tuple(findings),
        missing_stage_ids=missing_stages,
        unexpected_stage_ids=unexpected_stages,
        missing_gap_ids=missing_gaps,
        mapping_mismatch_stage_ids=mapping_mismatches,
        missing_candidate_ids=missing_candidates,
        unexpected_candidate_ids=unexpected_candidates,
        overclaim_stage_ids=overclaims,
        gap_coverage=gap_coverage,
        expected_overlap_gap_ids=EXPECTED_OVERLAP_GAP_IDS,
        operator_review_required=True,
        production_gap_closure_claimed=False,
        factor_activation_claimed=False,
        reconciliation_hash=digest(payload),
    )
