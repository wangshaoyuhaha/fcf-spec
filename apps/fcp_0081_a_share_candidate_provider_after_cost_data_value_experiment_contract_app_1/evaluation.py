from __future__ import annotations

from .contracts import (
    METRIC_IDS,
    AfterCostEvidence,
    ComparableMetricObservation,
    DataValueExperimentSpecification,
    DataValueReviewPacket,
)


def evaluate_data_value_experiment(
    specification: DataValueExperimentSpecification,
    observations: tuple[ComparableMetricObservation, ...],
    after_cost: AfterCostEvidence,
) -> DataValueReviewPacket:
    if not isinstance(specification, DataValueExperimentSpecification):
        raise TypeError("specification must be DataValueExperimentSpecification")
    if not isinstance(observations, tuple) or not all(isinstance(item, ComparableMetricObservation) for item in observations):
        raise TypeError("observations must contain ComparableMetricObservation")
    if not isinstance(after_cost, AfterCostEvidence):
        raise TypeError("after_cost must be AfterCostEvidence")
    if after_cost.specification_hash != specification.specification_hash:
        raise ValueError("after-cost evidence belongs to another specification")
    if any(item.specification_hash != specification.specification_hash for item in observations):
        raise ValueError("metric observation belongs to another specification")
    metric_ids = tuple(item.metric_id for item in observations)
    if len(metric_ids) != len(set(metric_ids)):
        raise ValueError("metric observations must be unique")
    ordered = tuple(sorted(observations, key=lambda item: item.metric_id))
    missing = tuple(item for item in METRIC_IDS if item not in metric_ids)
    improved = tuple(item.metric_id for item in ordered if item.improvement() > 0)
    regressed = tuple(item.metric_id for item in ordered if item.improvement() < 0)
    value = after_cost.after_cost_value()
    rights_complete = (
        after_cost.rights_state == "REGISTERED_REVIEW_COMPLETE"
        and after_cost.retention_state == "REGISTERED_REVIEW_COMPLETE"
    )
    if missing or not rights_complete:
        decision = "INSUFFICIENT_EVIDENCE"
    elif after_cost.fixed_cost_cny > specification.authorized_spend_cny:
        decision = "STOP_COST_EXCEEDS_AUTHORIZED_SPEND"
    elif regressed or value <= 0 or not improved:
        decision = "STOP_NO_INCREMENTAL_VALUE"
    elif len(improved) < 2:
        decision = "CONTINUE_LOCAL_RESEARCH"
    else:
        decision = "OPERATOR_REVIEW_ELIGIBLE"
    return DataValueReviewPacket(
        specification_hash=specification.specification_hash,
        decision_state=decision,
        observation_hashes=tuple(item.observation_hash for item in ordered),
        after_cost_evidence_hash=after_cost.evidence_hash,
        missing_metrics=missing,
        improved_metrics=tuple(sorted(improved)),
        regressed_metrics=tuple(sorted(regressed)),
        after_cost_value_cny=value,
    )
