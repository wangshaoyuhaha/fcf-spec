from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.fcp_0081_a_share_candidate_provider_after_cost_data_value_experiment_contract_app_1 import (
    DECISION_STATES,
    LOWER_IS_BETTER,
    METRIC_IDS,
    RETENTION_STATES,
    RIGHTS_STATES,
    AfterCostEvidence,
    ComparableMetricObservation,
    DataValueExperimentSpecification,
    evaluate_data_value_experiment,
)


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64


def specification(**overrides):
    values = {
        "experiment_id": "experiment-a-share-provider-v1",
        "baseline_candidate_id": "miniqmt-local-baseline",
        "candidate_id": "tushare-local-candidate",
        "baseline_profile_hash": SHA_A,
        "candidate_profile_hash": SHA_B,
        "baseline_artifact_sha256": SHA_C,
        "candidate_artifact_sha256": SHA_D,
        "instrument_ids": ("000001.XSHE", "600000.XSHG"),
        "start_date": "2026-01-01",
        "end_date": "2026-06-30",
    }
    values.update(overrides)
    return DataValueExperimentSpecification(**values)


def metric(spec, metric_id, baseline="0.8", candidate="0.9", **overrides):
    if metric_id in LOWER_IS_BETTER:
        baseline, candidate = "10", "5"
        if metric_id == "CONFLICT_RATE":
            baseline, candidate = "0.1", "0.05"
    values = {
        "specification_hash": spec.specification_hash,
        "metric_id": metric_id,
        "baseline_value": baseline,
        "candidate_value": candidate,
        "comparable_window_hash": SHA_A,
        "evidence_sha256": SHA_B,
        "observed_at_utc": "2026-07-23T06:30:00Z",
    }
    values.update(overrides)
    return ComparableMetricObservation(**values)


def observations(spec, **candidate_overrides):
    return tuple(
        metric(
            spec,
            item,
            **(
                {"candidate_value": candidate_overrides[item]}
                if item in candidate_overrides
                else {}
            ),
        )
        for item in METRIC_IDS
    )


def cost(spec, **overrides):
    values = {
        "specification_hash": spec.specification_hash,
        "fixed_cost_cny": "0",
        "measured_benefit_cny": "10",
        "cost_evidence_sha256": SHA_C,
        "benefit_evidence_sha256": SHA_D,
        "rights_state": "REGISTERED_REVIEW_COMPLETE",
        "retention_state": "REGISTERED_REVIEW_COMPLETE",
        "observed_at_utc": "2026-07-23T06:31:00Z",
    }
    values.update(overrides)
    return AfterCostEvidence(**values)


def test_d1_vocabularies_are_closed_and_exact():
    assert METRIC_IDS == tuple(sorted(METRIC_IDS))
    assert LOWER_IS_BETTER == ("CONFLICT_RATE", "FRESHNESS_DELAY_SECONDS")
    assert RIGHTS_STATES == ("REGISTERED_REVIEW_COMPLETE", "UNRESOLVED")
    assert RETENTION_STATES == ("REGISTERED_REVIEW_COMPLETE", "UNRESOLVED")
    assert DECISION_STATES == (
        "CONTINUE_LOCAL_RESEARCH",
        "INSUFFICIENT_EVIDENCE",
        "OPERATOR_REVIEW_ELIGIBLE",
        "STOP_COST_EXCEEDS_AUTHORIZED_SPEND",
        "STOP_NO_INCREMENTAL_VALUE",
    )


def test_d2_specification_is_immutable_deterministic_and_zero_spend():
    left = specification()
    right = specification()
    assert left.specification_hash == right.specification_hash
    assert left.authorized_spend_cny == Decimal("0")
    assert left.provider_selected is False
    assert left.purchase_allowed is False
    assert left.renewal_allowed is False
    assert left.cancellation_allowed is False
    with pytest.raises(FrozenInstanceError):
        left.candidate_id = "changed"


@pytest.mark.parametrize(
    "overrides",
    (
        {"baseline_candidate_id": "same", "candidate_id": "same"},
        {"instrument_ids": ()},
        {"instrument_ids": ("000001.XSHE", "000001.XSHE")},
        {"instrument_ids": ("BTCUSDT",)},
        {"start_date": "2026-07-01", "end_date": "2026-06-30"},
        {"required_metrics": METRIC_IDS[:-1]},
        {"authorized_spend_cny": "1"},
        {"authorized_spend_cny": 0.0},
        {"local_registered_artifacts_only": False},
        {"provider_selected": True},
        {"purchase_allowed": True},
        {"renewal_allowed": True},
        {"cancellation_allowed": True},
        {"operator_review_required": False},
    ),
)
def test_d2_specification_rejects_scope_or_comparability_drift(overrides):
    with pytest.raises((TypeError, ValueError)):
        specification(**overrides)


def test_d3_metric_observation_is_exact_and_hash_stable():
    spec = specification()
    left = metric(spec, "COVERAGE_RATIO")
    right = metric(spec, "COVERAGE_RATIO")
    assert left.observation_hash == right.observation_hash
    assert left.improvement() == Decimal("0.1")
    assert metric(spec, "FRESHNESS_DELAY_SECONDS").improvement() == Decimal("5")


@pytest.mark.parametrize(
    "overrides",
    (
        {"metric_id": "UNKNOWN"},
        {"metric_id": "COVERAGE_RATIO", "candidate_value": "1.1"},
        {"metric_id": "COVERAGE_RATIO", "candidate_value": 0.9},
        {"metric_id": "COVERAGE_RATIO", "observed_not_inferred": False},
        {"metric_id": "COVERAGE_RATIO", "observed_at_utc": "2026-07-23T14:30:00+08:00"},
    ),
)
def test_d3_metric_observation_rejects_unsafe_evidence(overrides):
    spec = specification()
    metric_id = overrides.pop("metric_id")
    with pytest.raises(ValueError):
        metric(spec, metric_id, **overrides)


def test_d3_after_cost_evidence_is_exact_and_quote_non_authorizing():
    spec = specification()
    evidence = cost(spec, fixed_cost_cny="5", measured_benefit_cny="3")
    assert evidence.after_cost_value() == Decimal("-2")
    assert evidence.provider_quote_is_authority is False
    with pytest.raises(ValueError, match="quote"):
        cost(spec, provider_quote_is_authority=True)


def test_d4_missing_metrics_fail_closed():
    spec = specification()
    result = evaluate_data_value_experiment(spec, observations(spec)[:-1], cost(spec))
    assert result.decision_state == "INSUFFICIENT_EVIDENCE"
    assert result.missing_metrics == (METRIC_IDS[-1],)


@pytest.mark.parametrize("field", ("rights_state", "retention_state"))
def test_d4_unresolved_rights_or_retention_fail_closed(field):
    spec = specification()
    result = evaluate_data_value_experiment(spec, observations(spec), cost(spec, **{field: "UNRESOLVED"}))
    assert result.decision_state == "INSUFFICIENT_EVIDENCE"


def test_d4_positive_cost_exceeds_current_zero_spend_boundary():
    spec = specification()
    result = evaluate_data_value_experiment(spec, observations(spec), cost(spec, fixed_cost_cny="1"))
    assert result.decision_state == "STOP_COST_EXCEEDS_AUTHORIZED_SPEND"
    assert result.purchase_authorized is False


def test_d4_regression_stops_even_when_measured_benefit_is_positive():
    spec = specification()
    rows = observations(spec, COVERAGE_RATIO="0.7")
    result = evaluate_data_value_experiment(spec, rows, cost(spec))
    assert result.decision_state == "STOP_NO_INCREMENTAL_VALUE"
    assert result.regressed_metrics == ("COVERAGE_RATIO",)


def test_d4_nonpositive_after_cost_value_stops():
    spec = specification()
    result = evaluate_data_value_experiment(spec, observations(spec), cost(spec, measured_benefit_cny="0"))
    assert result.decision_state == "STOP_NO_INCREMENTAL_VALUE"


def test_d4_one_improvement_continues_local_research_only():
    spec = specification()
    rows = tuple(
        metric(
            spec,
            item,
            **(
                {"baseline_value": "0.1", "candidate_value": "0.1"}
                if item in LOWER_IS_BETTER
                else {
                    "baseline_value": "0.8",
                    "candidate_value": "0.9" if item == "COVERAGE_RATIO" else "0.8",
                }
            ),
        )
        for item in METRIC_IDS
    )
    result = evaluate_data_value_experiment(spec, rows, cost(spec))
    assert result.decision_state == "CONTINUE_LOCAL_RESEARCH"
    assert result.improved_metrics == ("COVERAGE_RATIO",)


def test_d4_complete_incremental_value_is_operator_review_eligible_only():
    spec = specification()
    result = evaluate_data_value_experiment(spec, observations(spec), cost(spec))
    assert result.decision_state == "OPERATOR_REVIEW_ELIGIBLE"
    assert result.operator_review_required is True
    assert result.provider_selected is False
    assert result.purchase_authorized is False
    assert result.renewal_authorized is False
    assert result.cancellation_authorized is False
    assert result.claims_profitability is False
    assert result.closes_gap is False


def test_d4_duplicate_or_cross_experiment_observations_are_rejected():
    spec = specification()
    rows = observations(spec)
    with pytest.raises(ValueError, match="unique"):
        evaluate_data_value_experiment(spec, rows + (rows[0],), cost(spec))
    other = specification(experiment_id="other-experiment")
    with pytest.raises(ValueError, match="another specification"):
        evaluate_data_value_experiment(spec, (metric(other, METRIC_IDS[0]),), cost(spec))
    with pytest.raises(ValueError, match="another specification"):
        evaluate_data_value_experiment(spec, rows, cost(other))


def test_d5_review_packet_hash_is_order_independent_for_observations():
    spec = specification()
    rows = observations(spec)
    left = evaluate_data_value_experiment(spec, rows, cost(spec))
    right = evaluate_data_value_experiment(spec, tuple(reversed(rows)), cost(spec))
    assert left.packet_hash == right.packet_hash


def test_d6_contract_contains_no_provider_endpoint_or_credential():
    spec = specification()
    payload = str(spec.payload()).upper()
    assert not any(term in payload for term in ("TOKEN", "PASSWORD", "SECRET", "HTTP://", "HTTPS://", "TCP://"))
