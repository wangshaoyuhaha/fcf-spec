from dataclasses import replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.fcf_web_console_app_1 import FCFWebConsoleApplication, WebConsoleSnapshot
from apps.multi_market_adapters_stage_6 import MarketAdapterId
from apps.p4_controlled_enhancements_stage_12 import (
    CaseMemoryQuery,
    CaseMemoryRecord,
    ChallengerProposalRequest,
    DeterministicP4ProposalService,
    ForwardShadowObservation,
    LocalForwardShadowValidationService,
    P4_CAPABILITY_REGISTRY,
    P4_CONTROLLED_ENHANCEMENTS_BOUNDARY,
    RegisteredCaseMemoryService,
    RegisteredTrainingResult,
    SpecialistTrainingGovernanceService,
    SpecialistTrainingPlan,
    build_p4_acceptance,
    build_p4_console_sections,
)


def _case(case_id="case-1", **overrides):
    values = {
        "case_id": case_id,
        "available_at_utc": "2025-01-02T00:00:00Z",
        "market_id": MarketAdapterId.US_EQUITY,
        "regime_id": "regime-normal",
        "outcome_status": "POSITIVE",
        "source_artifact_ids": ("result-1",),
        "attributes": MappingProxyType({"score": "0.8"}),
    }
    values.update(overrides)
    return CaseMemoryRecord(**values)


def _query(**overrides):
    values = {
        "query_id": "query-1",
        "as_of_time_utc": "2025-01-10T00:00:00Z",
        "market_id": MarketAdapterId.US_EQUITY,
        "regime_id": "regime-normal",
        "allowed_artifact_ids": ("result-1",),
        "limit": 20,
    }
    values.update(overrides)
    return CaseMemoryQuery(**values)


def _proposal(**overrides):
    values = {
        "proposal_id": "proposal-1",
        "candidate_type": "factor",
        "champion_version": "champion-v1",
        "proposed_version": "challenger-v2",
        "source_result_ids": ("result-1",),
        "source_feedback_ids": (),
        "change_space": MappingProxyType({"quality_weight": ("0.6", "0.7")}),
        "rationale": "Registered evidence supports a bounded Challenger.",
        "deterministic_seed": 1,
    }
    values.update(overrides)
    return ChallengerProposalRequest(**values)


def _shadow(**overrides):
    values = {
        "observation_id": "shadow-1",
        "market_id": MarketAdapterId.US_EQUITY,
        "forward_window_started_at_utc": "2025-04-01T00:00:00Z",
        "decision_time_utc": "2025-04-02T00:00:00Z",
        "observation_time_utc": "2025-04-03T00:00:00Z",
        "registered_at_utc": "2025-04-03T01:00:00Z",
        "expected_return": Decimal("0.02"),
        "observed_return": Decimal("0.01"),
        "evidence_ids": ("shadow-artifact-1",),
    }
    values.update(overrides)
    return ForwardShadowObservation(**values)


def _plan(**overrides):
    values = {
        "plan_id": "training-plan-1",
        "specialist_role": "risk-specialist",
        "as_of_time_utc": "2025-04-01T00:00:00Z",
        "dataset_artifact_ids": ("dataset-1",),
        "config_snapshot_id": "config-v1",
        "objective_metrics": ("fact-alignment", "incremental-value"),
        "operator_trigger_id": "operator-trigger-1",
    }
    values.update(overrides)
    return SpecialistTrainingPlan(**values)


def _training_result(**overrides):
    values = {
        "result_id": "training-result-1",
        "plan_id": "training-plan-1",
        "registered_at_utc": "2025-04-05T00:00:00Z",
        "training_artifact_id": "training-artifact-1",
        "source_evidence_ids": ("dataset-1",),
        "metrics": MappingProxyType(
            {
                "fact-alignment": Decimal("0.91"),
                "incremental-value": Decimal("0.03"),
            }
        ),
    }
    values.update(overrides)
    return RegisteredTrainingResult(**values)


def test_d1_boundary_preserves_all_permanent_controls():
    boundary = P4_CONTROLLED_ENHANCEMENTS_BOUNDARY
    assert boundary.registered_artifact_only is True
    assert boundary.operator_review_required is True
    assert boundary.training_execution_allowed is False
    assert boundary.experiment_execution_allowed is False
    assert boundary.real_execution_allowed is False


def test_d1_registry_keeps_exact_five_canonical_p4_capabilities():
    assert tuple(P4_CAPABILITY_REGISTRY) == ("P4",)
    assert P4_CAPABILITY_REGISTRY["P4"] == (
        "CASE-MEMORY-RETRIEVAL-APP-1",
        "AUTOMATIC-CHALLENGER-PROPOSAL-APP-1",
        "REALTIME-SHADOW-VALIDATION-APP-1",
        "AUTOMATIC-EXPERIMENT-SCHEDULER-APP-1",
        "SPECIALIST-MODEL-TRAINING-APP-1",
    )


def test_d2_case_memory_is_immutable_and_preserves_negative_cases():
    record = _case(outcome_status="NEGATIVE")
    assert record.outcome_status == "NEGATIVE"
    with pytest.raises(TypeError):
        record.attributes["score"] = "1.0"


def test_d2_case_memory_excludes_future_cases():
    retrieval = RegisteredCaseMemoryService().retrieve(
        (_case(available_at_utc="2025-01-11T00:00:00Z"),),
        _query(),
    )
    assert retrieval.records == ()
    assert "future-case-excluded" in retrieval.reason_codes


def test_d2_case_memory_excludes_artifacts_outside_registered_scope():
    retrieval = RegisteredCaseMemoryService().retrieve(
        (_case(source_artifact_ids=("result-2",)),),
        _query(),
    )
    assert retrieval.records == ()
    assert "unregistered-scope-case-excluded" in retrieval.reason_codes


def test_d2_case_memory_filters_orders_and_limits_deterministically():
    records = (
        _case("case-old", available_at_utc="2025-01-02T00:00:00Z"),
        _case("case-new", available_at_utc="2025-01-03T00:00:00Z"),
        _case("case-other", regime_id="regime-stress"),
    )
    retrieval = RegisteredCaseMemoryService().retrieve(records, _query(limit=1))
    assert tuple(item.case_id for item in retrieval.records) == ("case-new",)
    assert retrieval.read_only is True
    assert retrieval.network_access_used is False


def test_d2_case_memory_rejects_duplicate_registered_case_ids():
    with pytest.raises(ValueError, match="case ids must be unique"):
        RegisteredCaseMemoryService().retrieve((_case(), _case()), _query())


def test_d3_challenger_proposal_is_deterministic_and_candidate_only():
    service = DeterministicP4ProposalService()
    first = service.propose_challenger(_proposal())
    second = service.propose_challenger(_proposal())
    assert first.declared_changes == second.declared_changes
    assert first.declared_changes["quality_weight"] == "0.7"
    assert first.candidate_only is True
    assert first.automatic_activation_allowed is False


def test_d3_challenger_proposal_rejects_empty_change_space():
    with pytest.raises(ValueError, match="change_space"):
        _proposal(change_space={})


def test_d3_schedule_is_a_review_proposal_and_cannot_execute():
    service = DeterministicP4ProposalService()
    candidate = service.propose_challenger(_proposal())
    schedule = service.propose_schedule(
        "schedule-1",
        candidate,
        "2025-05-01T00:00:00Z",
        "2025-05-31T00:00:00Z",
        ("backtest-result-1",),
    )
    assert schedule.status == "PROPOSED_REVIEW_REQUIRED"
    assert schedule.operator_review_required is True
    assert schedule.job_execution_allowed is False


def test_d3_schedule_rejects_non_positive_window():
    candidate = DeterministicP4ProposalService().propose_challenger(_proposal())
    with pytest.raises(ValueError, match="positive duration"):
        DeterministicP4ProposalService().propose_schedule(
            "schedule-1",
            candidate,
            "2025-05-01T00:00:00Z",
            "2025-05-01T00:00:00Z",
            ("result-1",),
        )


def test_d4_shadow_contract_rejects_historical_decision():
    with pytest.raises(ValueError, match="forward-only"):
        _shadow(decision_time_utc="2025-03-31T00:00:00Z")


def test_d4_shadow_validation_passes_mature_registered_observation():
    result = LocalForwardShadowValidationService().evaluate(
        (_shadow(),),
        "2025-04-04T00:00:00Z",
    )
    assert result.status == "PASS_REVIEW_REQUIRED"
    assert result.mean_error == Decimal("-0.01")
    assert result.network_access_used is False
    assert result.real_execution_used is False


def test_d4_shadow_validation_keeps_pending_visible():
    result = LocalForwardShadowValidationService().evaluate(
        (_shadow(observed_return=None),),
        "2025-04-04T00:00:00Z",
    )
    assert result.status == "DEGRADED_REVIEW_REQUIRED"
    assert "shadow-observation-pending" in result.reason_codes


def test_d4_shadow_validation_blocks_future_registration():
    result = LocalForwardShadowValidationService().evaluate(
        (_shadow(registered_at_utc="2025-04-06T00:00:00Z"),),
        "2025-04-04T00:00:00Z",
    )
    assert result.status == "BLOCKED_REVIEW_REQUIRED"
    assert "future-registration-blocked" in result.reason_codes


def test_d4_shadow_validation_exposes_direction_contradiction():
    result = LocalForwardShadowValidationService().evaluate(
        (_shadow(observed_return=Decimal("-0.01")),),
        "2025-04-04T00:00:00Z",
    )
    assert result.status == "DEGRADED_REVIEW_REQUIRED"
    assert "shadow-direction-contradiction" in result.reason_codes


def test_d4_shadow_validation_blocks_empty_observation_set():
    result = LocalForwardShadowValidationService().evaluate(
        (), "2025-04-04T00:00:00Z"
    )
    assert result.status == "BLOCKED_REVIEW_REQUIRED"
    assert "shadow-observations-required" in result.reason_codes


def test_d5_training_plan_never_authorizes_training_execution():
    assert _plan().training_execution_allowed is False
    with pytest.raises(ValueError, match="cannot execute"):
        _plan(training_execution_allowed=True)


def test_d5_registered_result_rejects_stage12_model_invocation():
    with pytest.raises(ValueError, match="registered training results only"):
        _training_result(model_invocation_performed_by_stage_12=True)


def test_d5_training_evaluation_passes_complete_registered_metrics():
    evaluation = SpecialistTrainingGovernanceService().evaluate_registered_result(
        _plan(),
        _training_result(),
    )
    assert evaluation.status == "PASS_REVIEW_REQUIRED"
    assert evaluation.advisory_only is True
    assert evaluation.automatic_activation_allowed is False


def test_d5_training_evaluation_degrades_missing_objective_metric():
    evaluation = SpecialistTrainingGovernanceService().evaluate_registered_result(
        _plan(),
        _training_result(metrics={"fact-alignment": Decimal("0.91")}),
    )
    assert evaluation.status == "DEGRADED_REVIEW_REQUIRED"
    assert "objective-metrics-missing" in evaluation.reason_codes


def test_d5_training_evaluation_blocks_plan_mismatch():
    evaluation = SpecialistTrainingGovernanceService().evaluate_registered_result(
        _plan(),
        _training_result(plan_id="other-plan"),
    )
    assert evaluation.status == "BLOCKED_REVIEW_REQUIRED"


def test_d5_training_evaluation_blocks_result_registered_before_plan():
    evaluation = SpecialistTrainingGovernanceService().evaluate_registered_result(
        _plan(as_of_time_utc="2025-04-06T00:00:00Z"),
        _training_result(registered_at_utc="2025-04-05T00:00:00Z"),
    )
    assert evaluation.status == "BLOCKED_REVIEW_REQUIRED"
    assert "training-result-precedes-plan" in evaluation.reason_codes


def test_d6_web_console_renders_all_p4_sections_read_only():
    case_retrieval = RegisteredCaseMemoryService().retrieve((_case(),), _query())
    proposal_service = DeterministicP4ProposalService()
    candidate = proposal_service.propose_challenger(_proposal())
    schedule = proposal_service.propose_schedule(
        "schedule-1",
        candidate,
        "2025-05-01T00:00:00Z",
        "2025-05-31T00:00:00Z",
        ("result-1",),
    )
    shadow = LocalForwardShadowValidationService().evaluate(
        (_shadow(),), "2025-04-04T00:00:00Z"
    )
    training = SpecialistTrainingGovernanceService().evaluate_registered_result(
        _plan(), _training_result()
    )
    sections = build_p4_console_sections(
        case_retrieval, candidate, shadow, schedule, training
    )
    app = FCFWebConsoleApplication(
        WebConsoleSnapshot(
            correlation_id="corr-p4",
            sections=sections,
            source_artifact_ids=("result-1", "shadow-artifact-1", "training-artifact-1"),
        )
    )
    assert "experiment_schedule_proposal" in app.dispatch("GET", "/workflows").body.decode()
    models = app.dispatch("GET", "/models").body.decode()
    assert "challenger_proposal" in models
    assert "specialist_training_governance" in models
    assert "realtime_shadow_validation" in app.dispatch("GET", "/paper-portfolio").body.decode()
    assert "case_memory_retrieval" in app.dispatch("GET", "/reports").body.decode()


def test_d6_acceptance_closes_five_capabilities_and_defers_runtime_config():
    acceptance = build_p4_acceptance()
    assert acceptance.status == "D1_D6_ACCEPTED"
    assert acceptance.capability_count == 5
    assert acceptance.next_phase == "LOCAL_AI_RUNTIME_CONFIGURATION_GOVERNANCE"
