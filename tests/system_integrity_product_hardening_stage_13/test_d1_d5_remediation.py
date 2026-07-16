from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from apps.controlled_learning_backtesting_p0_p3_stage_11 import (
    AppendOnlyRegistry,
    AttributionRecord,
    BacktestBiasGuard,
    DataSourceVersionLock,
    DataSourceVersionRegistry,
    DeterministicUnifiedBacktestEngine,
    HumanFeedback,
    P0_P3_CAPABILITY_REGISTRY,
    P0_P3_IMPLEMENTATION_BINDINGS,
    WalkForwardValidator,
    build_attribution_registry,
    build_outcome_label_registry,
)
from apps.p4_controlled_enhancements_stage_12 import (
    ChallengerProposalRequest,
    DeterministicP4ProposalService,
    P4_CAPABILITY_REGISTRY,
    P4_IMPLEMENTATION_BINDINGS,
    RegisteredCaseMemoryService,
    SpecialistTrainingGovernanceService,
)
from apps.read_only_data_gateway_app_1.artifact_reader import (
    RegisteredArtifactReadError,
    _resolved_allowed_root,
)
from scripts.run_active_surface_quality_guard import main as run_quality_guard
from tests.controlled_learning_backtesting_p0_p3_stage_11.test_d1_d6_p0_p3 import (
    _evidence,
    _request,
)
from tests.p4_controlled_enhancements_stage_12.test_d1_d6_p4 import (
    _case,
    _plan,
    _proposal,
    _query,
    _shadow,
    _training_result,
)
from apps.p4_controlled_enhancements_stage_12 import LocalForwardShadowValidationService


def test_d1_late_evidence_is_rejected_at_request_boundary():
    late = _evidence(
        available_at_utc="2025-01-04T00:00:00Z",
        ingested_at_utc="2025-01-04T01:00:00Z",
        retrieval_time_utc="2025-01-04T01:00:00Z",
        as_of_time_utc="2025-01-05T00:00:00Z",
    )
    with pytest.raises(ValueError, match="future evidence"):
        replace(_request(), evidence=(late,))


def test_d1_unregistered_observation_evidence_is_rejected():
    observation = replace(
        _request().observations[0], evidence_ids=("unknown-evidence",)
    )
    with pytest.raises(ValueError, match="unregistered evidence"):
        replace(_request(), observations=(observation,) + _request().observations[1:])


def test_d1_nonfinite_payload_and_non_utc_feedback_are_rejected():
    with pytest.raises(ValueError, match="finite"):
        _evidence(payload={"value": float("nan")})
    with pytest.raises(ValueError, match="ISO-8601"):
        HumanFeedback(
            feedback_id="feedback",
            operator_id="operator",
            target_artifact_id="target",
            classification="valid",
            reason="reason",
            submitted_at_utc="not-a-time",
        )


def test_d1_capability_bindings_are_complete_and_callable():
    expected = {
        item for values in P0_P3_CAPABILITY_REGISTRY.values() for item in values
    }
    assert set(P0_P3_IMPLEMENTATION_BINDINGS) == expected
    assert all(callable(value) for value in P0_P3_IMPLEMENTATION_BINDINGS.values())
    assert set(P4_IMPLEMENTATION_BINDINGS) == set(P4_CAPABILITY_REGISTRY["P4"])
    assert P0_P3_IMPLEMENTATION_BINDINGS["BACKTEST-BIAS-GUARD-APP-1"] is BacktestBiasGuard
    assert P0_P3_IMPLEMENTATION_BINDINGS["WALK-FORWARD-VALIDATION-APP-1"] is WalkForwardValidator


def test_d1_append_only_registry_rejects_overwrite():
    record = DataSourceVersionLock("source", "v1", "a" * 64, "2025-01-01T00:00:00Z")
    registry = AppendOnlyRegistry().append(record, "source_id")
    with pytest.raises(ValueError, match="cannot be overwritten"):
        registry.append(record, "source_id")


def test_d1_concrete_registry_and_result_derived_registries_are_immutable():
    source = DataSourceVersionLock("source", "v1", "a" * 64, "2025-01-01T00:00:00Z")
    source_registry = DataSourceVersionRegistry().append(source)
    with pytest.raises(ValueError, match="cannot be overwritten"):
        source_registry.append(source)

    result = DeterministicUnifiedBacktestEngine().run(_request())
    outcomes = build_outcome_label_registry(result)
    attribution = build_attribution_registry(result)
    assert len(outcomes.records) == len(result.outcome_labels)
    assert attribution.records[0].result_id == result.result_id
    assert attribution.records[0].source_evidence_ids == result.source_evidence_ids


def test_d2_mixed_scope_case_is_excluded():
    record = _case(source_artifact_ids=("result-1", "outside-result"))
    retrieval = RegisteredCaseMemoryService().retrieve((record,), _query())
    assert retrieval.records == ()
    assert "unregistered-scope-case-excluded" in retrieval.reason_codes


def test_d2_training_source_must_belong_to_plan():
    evaluation = SpecialistTrainingGovernanceService().evaluate_registered_result(
        _plan(dataset_artifact_ids=("dataset-1",)),
        _training_result(source_evidence_ids=("outside-dataset",)),
    )
    assert evaluation.status == "BLOCKED_REVIEW_REQUIRED"
    assert "training-result-source-outside-plan" in evaluation.reason_codes


def test_d2_challenger_declares_every_change_variable():
    request = _proposal(
        change_space={"quality_weight": ("0.6",), "risk_limit": ("0.2",)}
    )
    candidate = DeterministicP4ProposalService().propose_challenger(request)
    assert set(candidate.declared_changes) == {"quality_weight", "risk_limit"}


def test_d2_schedule_rejects_unregistered_dependency():
    service = DeterministicP4ProposalService()
    candidate = service.propose_challenger(_proposal())
    with pytest.raises(ValueError, match="not registered"):
        service.propose_schedule(
            "schedule",
            candidate,
            "2025-05-01T00:00:00Z",
            "2025-05-02T00:00:00Z",
            ("dependency",),
            registered_artifact_ids=("other",),
        )


def test_d2_shadow_reports_absolute_error_and_direction_accuracy():
    result = LocalForwardShadowValidationService().evaluate(
        (_shadow(), _shadow(observation_id="shadow-2", observed_return=Decimal("-0.01"))),
        "2025-04-04T00:00:00Z",
    )
    assert result.mean_error == Decimal("-0.02")
    assert result.mean_absolute_error == Decimal("0.02")
    assert result.direction_accuracy == Decimal("0.5")


def test_d5_symlink_rejection_branch_runs_without_windows_symlink_privilege(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(Path, "is_symlink", lambda self: True)
    with pytest.raises(RegisteredArtifactReadError, match="symbolic-allowed-root"):
        _resolved_allowed_root(tmp_path)


def test_d5_active_surface_quality_guard_passes():
    assert run_quality_guard() == 0
