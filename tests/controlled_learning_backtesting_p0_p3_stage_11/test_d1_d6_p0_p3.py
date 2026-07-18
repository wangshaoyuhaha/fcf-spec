from dataclasses import replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.controlled_learning_backtesting_p0_p3_stage_11 import (
    AIReplayMode,
    BacktestObservation,
    BacktestResultRegistry,
    BacktestStatus,
    CONTROLLED_LEARNING_BACKTESTING_BOUNDARY,
    ConfigSnapshot,
    ControlledEvolutionService,
    DatasetSplit,
    DeterministicUnifiedBacktestEngine,
    EVOLUTION_GATE_CHECKS,
    HumanFeedback,
    LearningCandidate,
    P0_P3_CAPABILITY_REGISTRY,
    PointInTimeEvidence,
    RegisteredAIHistoricalEvaluationService,
    RegisteredAIReplay,
    UnifiedBacktestRequest,
    build_p0_p3_acceptance,
    build_p0_p3_console_sections,
)
from apps.fcf_web_console_app_1 import (
    FCFWebConsoleApplication,
    WebConsoleSnapshot,
)
from apps.multi_market_adapters_stage_6 import MarketAdapterId


_DIGEST = "a" * 64
_QUALIFICATION_CHECKS = (
    "no-core-mutation",
    "no-p48",
    "no-hard-policy-conflict",
    "authorized-data-source",
    "licensed-data-use",
    "authorized-processing",
    "no-future-data-dependency",
    "no-hidden-risk-change",
    "no-hidden-benchmark-change",
    "no-hidden-cost-change",
    "no-undeclared-model-prompt-change",
    "no-undeclared-market-rule-change",
    "no-real-execution-path",
    "no-automatic-promotion-authority",
)


def _evidence(**overrides):
    values = {
        "evidence_id": "pit-evidence-1",
        "source_version": "source-v1",
        "event_time_utc": "2025-01-01T00:00:00Z",
        "published_at_utc": "2025-01-01T01:00:00Z",
        "available_at_utc": "2025-01-01T02:00:00Z",
        "ingested_at_utc": "2025-01-01T03:00:00Z",
        "as_of_time_utc": "2025-01-02T00:00:00Z",
        "retrieval_time_utc": "2025-01-01T03:00:00Z",
        "content_sha256": _DIGEST,
        "license_id": "license-read-only",
        "payload": MappingProxyType({"value": 1}),
    }
    values.update(overrides)
    return PointInTimeEvidence(**values)


def _config(**overrides):
    values = {
        "config_snapshot_id": "config-v1",
        "code_commit": "a6496d30dac3864b175c9da5a245792a8b0dd3a4",
        "deterministic_engine_version": "engine-v1",
        "strategy_version": "strategy-v1",
        "factor_version": "factor-v1",
        "portfolio_policy_version": "portfolio-v1",
        "market_adapter_version": "adapters-v1",
        "universe_version": "universe-v1",
        "market_calendar_version": "calendar-v1",
        "corporate_action_version": "actions-v1",
        "benchmark_version": "benchmark-v1",
        "policy_version": "policy-v1",
        "output_schema_version": "schema-v1",
        "data_source_versions": {"source": "v1"},
        "dataset_digests": {"dataset": _DIGEST},
        "factor_weights": {"quality": Decimal("0.5")},
        "assumptions": {
            "fee_bps": "5",
            "funding": "registered",
            "liquidity": "capacity-v1",
            "roll": "rule-v1",
            "slippage_bps": "3",
            "tax": "policy-v1",
        },
        "model_role_assignments": {"research": "registered-model"},
        "prompt_versions": {"research": "prompt-v1"},
        "random_seed": 17,
        "experiment_variables": {"quality_weight": "0.5"},
    }
    values.update(overrides)
    return ConfigSnapshot(**values)


def _observation(
    observation_id,
    split,
    decision,
    outcome,
    *,
    predicted="0.80",
    actual="0.80",
    gross_return="0.03",
    capacity=True,
):
    return BacktestObservation(
        observation_id=observation_id,
        adapter_id=MarketAdapterId.US_EQUITY,
        split=split,
        decision_as_of_utc=decision,
        feature_available_at_utc=decision,
        outcome_time_utc=outcome,
        predicted_score=Decimal(predicted),
        actual_outcome=Decimal(actual),
        gross_return=Decimal(gross_return),
        transaction_cost=Decimal("0.002"),
        slippage_cost=Decimal("0.001"),
        capacity_passed=capacity,
        regime_id="regime-normal",
        factor_attribution={"quality": Decimal("0.01")},
        evidence_ids=("pit-evidence-1",),
    )


def _observations(*, predicted="0.80", gross_return="0.03", capacity=True):
    return (
        _observation(
            "train-1",
            DatasetSplit.TRAIN,
            "2025-01-02T00:00:00Z",
            "2025-01-03T00:00:00Z",
            predicted=predicted,
            gross_return=gross_return,
            capacity=capacity,
        ),
        _observation(
            "validation-1",
            DatasetSplit.VALIDATION,
            "2025-02-02T00:00:00Z",
            "2025-02-03T00:00:00Z",
            predicted=predicted,
            gross_return=gross_return,
            capacity=capacity,
        ),
        _observation(
            "test-1",
            DatasetSplit.FINAL_TEST,
            "2025-03-02T00:00:00Z",
            "2025-03-03T00:00:00Z",
            predicted=predicted,
            gross_return=gross_return,
            capacity=capacity,
        ),
    )


def _request(
    request_id="backtest-1",
    *,
    observations=None,
    config=None,
    purged=True,
    embargo=5,
):
    return UnifiedBacktestRequest(
        request_id=request_id,
        correlation_id="corr-p0-p3",
        operator_trigger_id="operator-trigger-1",
        config=config or _config(),
        evidence=(_evidence(),),
        observations=observations or _observations(),
        embargo_days=embargo,
        purged_validation=purged,
    )


def _result(request=None):
    return DeterministicUnifiedBacktestEngine().run(request or _request())


def _replay(**overrides):
    values = {
        "replay_id": "replay-1",
        "mode": AIReplayMode.HISTORICAL_REPRODUCTION,
        "as_of_time_utc": "2025-01-02T00:00:00Z",
        "model_role": "research-advisor",
        "model_id": "registered-model",
        "model_version": "model-v1",
        "model_training_cutoff_status": "KNOWN",
        "prompt_id": "research-prompt",
        "prompt_version": "prompt-v1",
        "output_artifact_id": "registered-ai-output",
        "registered_ai_score": Decimal("0.90"),
        "deterministic_baseline_score": Decimal("0.80"),
        "fact_alignment_score": Decimal("0.95"),
        "evidence": (_evidence(),),
    }
    values.update(overrides)
    return RegisteredAIReplay(**values)


def _candidate(**overrides):
    values = {
        "candidate_id": "candidate-1",
        "candidate_type": "factor",
        "champion_version": "champion-v1",
        "proposed_version": "challenger-v2",
        "source_result_ids": ("result-backtest-1",),
        "source_feedback_ids": ("feedback-1",),
        "declared_changes": {"quality_weight": "0.6"},
        "rationale": "Registered outcomes support a sandbox comparison.",
    }
    values.update(overrides)
    return LearningCandidate(**values)


def test_d1_boundary_blocks_invocation_rewrite_and_activation():
    boundary = CONTROLLED_LEARNING_BACKTESTING_BOUNDARY
    assert boundary.point_in_time_required is True
    assert boundary.model_invocation_allowed is False
    assert boundary.result_rewrite_allowed is False
    assert boundary.automatic_activation_allowed is False
    assert boundary.real_execution_allowed is False


def test_d1_registry_contains_all_22_p0_p3_capabilities():
    assert tuple(P0_P3_CAPABILITY_REGISTRY) == ("P0", "P1", "P2", "P3")
    assert {key: len(value) for key, value in P0_P3_CAPABILITY_REGISTRY.items()} == {
        "P0": 6,
        "P1": 6,
        "P2": 5,
        "P3": 5,
    }
    assert sum(len(value) for value in P0_P3_CAPABILITY_REGISTRY.values()) == 22


def test_d1_point_in_time_evidence_rejects_future_availability():
    with pytest.raises(ValueError, match="available_at"):
        _evidence(
            available_at_utc="2025-01-03T00:00:00Z",
            ingested_at_utc="2025-01-03T01:00:00Z",
            retrieval_time_utc="2025-01-03T01:00:00Z",
        )


def test_d1_config_snapshot_is_immutable_and_complete():
    config = _config()
    with pytest.raises(TypeError):
        config.factor_weights["quality"] = Decimal("1")
    assert config.dataset_digests["dataset"] == _DIGEST
    assert config.random_seed == 17
    assert set(config.assumptions) >= {
        "fee_bps",
        "funding",
        "liquidity",
        "roll",
        "slippage_bps",
        "tax",
    }


def test_d2_deterministic_backtest_passes_with_three_locked_splits():
    result = _result()
    assert result.status is BacktestStatus.PASS_REVIEW_REQUIRED
    assert result.metrics["observation_count"] == 3
    assert result.metrics["mean_absolute_error"] == Decimal("0")
    assert result.metrics["mean_net_return"] == Decimal("0.027")
    assert result.metrics["random_seed"] == 17


def test_d2_observation_rejects_future_feature_leakage():
    with pytest.raises(ValueError, match="availability"):
        replace(
            _observations()[0],
            feature_available_at_utc="2025-01-02T01:00:00Z",
        )


def test_d2_missing_split_and_missing_bias_controls_fail_closed():
    missing = _request(observations=_observations()[:2])
    result = _result(missing)
    assert result.status is BacktestStatus.BLOCKED_REVIEW_REQUIRED
    assert "dataset-split-coverage-missing" in result.failure_codes
    controls = _result(_request(purged=False, embargo=0))
    assert controls.status is BacktestStatus.BLOCKED_REVIEW_REQUIRED
    assert "purged-validation-required" in controls.failure_codes
    assert "embargo-window-required" in controls.failure_codes


def test_d2_walk_forward_overlap_fails_closed():
    observations = (
        _observations()[0],
        replace(
            _observations()[1],
            decision_as_of_utc="2025-01-02T12:00:00Z",
            feature_available_at_utc="2025-01-02T12:00:00Z",
        ),
        _observations()[2],
    )
    result = _result(_request(observations=observations))
    assert result.status is BacktestStatus.BLOCKED_REVIEW_REQUIRED
    assert "walk-forward-window-overlap" in result.failure_codes


def test_d2_declared_embargo_must_match_actual_time_gap():
    observations = (
        _observations()[0],
        replace(
            _observations()[1],
            decision_as_of_utc="2025-01-03T00:00:01Z",
            feature_available_at_utc="2025-01-03T00:00:01Z",
            outcome_time_utc="2025-01-04T00:00:00Z",
        ),
        _observations()[2],
    )
    result = _result(_request(observations=observations, embargo=5))
    assert result.status is BacktestStatus.BLOCKED_REVIEW_REQUIRED
    assert "embargo-window-violation" in result.failure_codes


def test_d2_evidence_as_of_after_decision_is_rejected():
    future_as_of = replace(
        _evidence(),
        as_of_time_utc="2025-12-01T00:00:00Z",
    )
    with pytest.raises(ValueError, match="future evidence as_of_time"):
        replace(_request(), evidence=(future_as_of,))


def test_d2_negative_and_capacity_results_are_preserved_as_degraded():
    result = _result(
        _request(
            observations=_observations(
                gross_return="-0.01",
                capacity=False,
            )
        )
    )
    assert result.status is BacktestStatus.DEGRADED_REVIEW_REQUIRED
    assert "negative-net-return" in result.failure_codes
    assert "liquidity-capacity-failure" in result.failure_codes


def test_d2_outcome_and_attribution_preserve_original_evidence():
    result = _result()
    label = result.outcome_labels[0]
    assert label["original_prediction"] == "0.80"
    assert label["evaluation_policy"] == "policy-v1"
    assert label["data_version"] == "config-v1"
    assert result.factor_attribution["quality"] == Decimal("0.01")
    assert result.source_evidence_ids == ("pit-evidence-1",)


def test_d2_result_registry_is_append_only_and_preserves_failures():
    first = _result()
    registry = BacktestResultRegistry().append(first)
    with pytest.raises(ValueError, match="cannot be overwritten"):
        registry.append(first)
    degraded = _result(
        _request(
            "backtest-negative",
            observations=_observations(gross_return="-0.01"),
        )
    )
    registry = registry.append(degraded)
    assert len(registry.results) == 2
    assert registry.results[1].status is BacktestStatus.DEGRADED_REVIEW_REQUIRED


def test_d3_registered_ai_historical_evaluation_passes_without_invocation():
    evaluation = RegisteredAIHistoricalEvaluationService().evaluate(_replay())
    assert evaluation.status == "PASS_REVIEW_REQUIRED"
    assert evaluation.incremental_value == Decimal("0.10")
    assert evaluation.fact_alignment_score == Decimal("0.95")
    assert evaluation.model_invocation_performed is False
    assert evaluation.advisory_only is True


def test_d3_unknown_training_cutoff_is_visible_degradation():
    evaluation = RegisteredAIHistoricalEvaluationService().evaluate(
        _replay(model_training_cutoff_status="UNKNOWN")
    )
    assert evaluation.status == "DEGRADED_REVIEW_REQUIRED"
    assert "model-training-cutoff-unknown" in evaluation.reason_codes


def test_d3_historical_replay_rejects_future_evidence():
    future = _evidence(
        available_at_utc="2025-01-03T00:00:00Z",
        ingested_at_utc="2025-01-03T01:00:00Z",
        as_of_time_utc="2025-01-04T00:00:00Z",
        retrieval_time_utc="2025-01-03T01:00:00Z",
    )
    with pytest.raises(ValueError, match="future evidence"):
        _replay(evidence=(future,))


def test_d3_low_fact_alignment_and_no_incremental_value_are_visible():
    evaluation = RegisteredAIHistoricalEvaluationService().evaluate(
        _replay(
            registered_ai_score=Decimal("0.70"),
            fact_alignment_score=Decimal("0.60"),
        )
    )
    assert evaluation.status == "DEGRADED_REVIEW_REQUIRED"
    assert "fact-alignment-below-policy" in evaluation.reason_codes
    assert "no-positive-ai-incremental-value" in evaluation.reason_codes


def test_d4_human_feedback_requires_identity_target_and_reason():
    feedback = HumanFeedback(
        feedback_id="feedback-1",
        operator_id="operator-1",
        target_artifact_id="result-backtest-1",
        classification="needs-review",
        reason="The loss attribution requires another registered experiment.",
        submitted_at_utc="2026-07-16T00:00:00Z",
    )
    assert feedback.operator_id == "operator-1"
    with pytest.raises(ValueError, match="reason"):
        replace(feedback, reason="")


def test_d4_learning_output_is_candidate_only_and_declares_changes():
    candidate = _candidate()
    assert candidate.candidate_only is True
    assert candidate.automatic_activation_allowed is False
    with pytest.raises(TypeError):
        candidate.declared_changes["quality_weight"] = "1"
    with pytest.raises(ValueError, match="declare"):
        _candidate(declared_changes={})


def test_d4_static_qualification_preserves_rejection():
    service = ControlledEvolutionService()
    checks = {name: True for name in _QUALIFICATION_CHECKS}
    checks["licensed-data-use"] = False
    qualification = service.qualify(_candidate(), checks)
    assert qualification.accepted is False
    assert qualification.reason_codes == ("licensed-data-use",)


def _qualified_candidate():
    service = ControlledEvolutionService()
    candidate = _candidate()
    checks = {name: True for name in _QUALIFICATION_CHECKS}
    return service, candidate, service.qualify(candidate, checks)


def _experiment(*, compound=False):
    service, candidate, qualification = _qualified_candidate()
    if compound:
        candidate = _candidate(
            declared_changes={
                "quality_weight": "0.6",
                "turnover_limit": "0.2",
            }
        )
        qualification = service.qualify(
            candidate,
            {name: True for name in _QUALIFICATION_CHECKS},
        )
    champion = _result(
        _request(
            "champion-backtest",
            observations=_observations(predicted="0.60", gross_return="0.01"),
        )
    )
    challenger = _result(
        _request(
            "challenger-backtest",
            observations=_observations(predicted="0.80", gross_return="0.03"),
        )
    )
    experiment = service.experiment(
        "experiment-1",
        candidate,
        qualification,
        champion,
        challenger,
    )
    return service, experiment


def test_d4_champion_challenger_single_variable_sandbox_comparison():
    _, experiment = _experiment()
    assert experiment.status == "CHALLENGER_OUTPERFORMED"
    assert experiment.experiment_label == "SINGLE_VARIABLE"
    assert experiment.metric_deltas["mean_net_return"] == Decimal("0.02")
    assert experiment.metric_deltas["mean_absolute_error"] == Decimal("-0.20")


def test_d4_compound_experiment_cannot_claim_single_variable_attribution():
    _, experiment = _experiment(compound=True)
    assert experiment.experiment_label == "COMPOUND_EXPERIMENT"
    assert len(experiment.changed_variables) == 2


def test_d5_all_18_gates_only_reach_operator_review():
    service, experiment = _experiment()
    checks = {name: True for name in EVOLUTION_GATE_CHECKS}
    decision = service.gate(experiment, checks)
    assert decision.status == "ELIGIBLE_FOR_OPERATOR_REVIEW"
    assert len(decision.gate_checks) == 18
    assert decision.explicit_operator_approval_recorded is True
    assert decision.automatic_activation_allowed is False
    assert decision.champion_overwritten is False
    assert decision.rollback_version == "champion-v1"


def test_d5_failed_gate_blocks_promotion_and_automatic_rollback():
    service, experiment = _experiment()
    checks = {name: True for name in EVOLUTION_GATE_CHECKS}
    checks["risk-review"] = False
    decision = service.gate(experiment, checks)
    assert decision.status == "BLOCKED_REVIEW_REQUIRED"
    assert "risk-review" in decision.reason_codes
    assert decision.automatic_rollback_allowed is False


def test_d5_learning_loop_audit_digest_is_deterministic():
    service, experiment = _experiment()
    checks = {name: True for name in EVOLUTION_GATE_CHECKS}
    first = service.gate(experiment, checks)
    second = service.gate(experiment, checks)
    assert first.audit_sha256 == second.audit_sha256
    assert len(first.audit_sha256) == 64


def test_d6_web_console_renders_backtest_ai_experiment_and_gate():
    backtest = _result()
    ai = RegisteredAIHistoricalEvaluationService().evaluate(_replay())
    service, experiment = _experiment()
    gate = service.gate(
        experiment,
        {name: True for name in EVOLUTION_GATE_CHECKS},
    )
    sections = build_p0_p3_console_sections(backtest, ai, experiment, gate)
    snapshot = WebConsoleSnapshot(
        correlation_id="corr-p0-p3",
        sections=sections,
        source_artifact_ids=("result-backtest-1", "registered-ai-output"),
    )
    app = FCFWebConsoleApplication(snapshot)
    models = app.dispatch("GET", "/models").body.decode("utf-8")
    reports = app.dispatch("GET", "/reports").body.decode("utf-8")
    assert "ai_historical_evaluation" in models
    assert "deterministic_backtest" in reports
    assert "challenger_experiment" in reports
    assert "controlled_evolution_gate" in reports


def test_d6_acceptance_closes_22_capabilities_and_defers_p4():
    acceptance = build_p0_p3_acceptance()
    assert acceptance.status == "D1_D6_ACCEPTED"
    assert acceptance.capability_count == 22
    assert acceptance.next_phase == "P4_GOVERNANCE_DECISION"
