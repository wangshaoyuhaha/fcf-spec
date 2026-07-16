from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .boundary import CONTROLLED_LEARNING_BACKTESTING_BOUNDARY
from .contracts import (
    BacktestResult,
    BacktestStatus,
    DatasetSplit,
    UnifiedBacktestRequest,
    utc_time,
)


class DeterministicUnifiedBacktestEngine:
    def run(self, request: UnifiedBacktestRequest) -> BacktestResult:
        CONTROLLED_LEARNING_BACKTESTING_BOUNDARY.__post_init__()
        failures = []
        splits = {item.split for item in request.observations}
        required = {
            DatasetSplit.TRAIN,
            DatasetSplit.VALIDATION,
            DatasetSplit.FINAL_TEST,
        }
        if splits != required:
            failures.append("dataset-split-coverage-missing")
        if not request.purged_validation:
            failures.append("purged-validation-required")
        if request.embargo_days < 1:
            failures.append("embargo-window-required")
        ordered_by_split = {
            split: sorted(
                (
                    item
                    for item in request.observations
                    if item.split is split
                ),
                key=lambda item: utc_time(
                    item.decision_as_of_utc,
                    "decision_as_of_utc",
                ),
            )
            for split in required
        }
        if all(ordered_by_split.values()):
            train_end = max(
                utc_time(item.outcome_time_utc, "outcome_time_utc")
                for item in ordered_by_split[DatasetSplit.TRAIN]
            )
            validation_start = min(
                utc_time(item.decision_as_of_utc, "decision_as_of_utc")
                for item in ordered_by_split[DatasetSplit.VALIDATION]
            )
            validation_end = max(
                utc_time(item.outcome_time_utc, "outcome_time_utc")
                for item in ordered_by_split[DatasetSplit.VALIDATION]
            )
            final_start = min(
                utc_time(item.decision_as_of_utc, "decision_as_of_utc")
                for item in ordered_by_split[DatasetSplit.FINAL_TEST]
            )
            if train_end >= validation_start or validation_end >= final_start:
                failures.append("walk-forward-window-overlap")
        observations = request.observations
        absolute_errors = [
            abs(item.predicted_score - item.actual_outcome)
            for item in observations
        ]
        net_returns = [
            item.gross_return - item.transaction_cost - item.slippage_cost
            for item in observations
        ]
        capacity_failures = sum(not item.capacity_passed for item in observations)
        if capacity_failures:
            failures.append("liquidity-capacity-failure")
        regime_values = defaultdict(list)
        factor_values = defaultdict(list)
        for item, net_return in zip(observations, net_returns):
            regime_values[item.regime_id].append(net_return)
            for factor_id, value in item.factor_attribution.items():
                factor_values[factor_id].append(value)
        count = Decimal(len(observations))
        mean_error = sum(absolute_errors, Decimal("0")) / count
        mean_net_return = sum(net_returns, Decimal("0")) / count
        if mean_net_return < 0:
            failures.append("negative-net-return")
        blocked_codes = {
            "dataset-split-coverage-missing",
            "purged-validation-required",
            "embargo-window-required",
            "walk-forward-window-overlap",
        }
        status = (
            BacktestStatus.BLOCKED_REVIEW_REQUIRED
            if blocked_codes.intersection(failures)
            else (
                BacktestStatus.DEGRADED_REVIEW_REQUIRED
                if failures
                else BacktestStatus.PASS_REVIEW_REQUIRED
            )
        )
        outcomes = tuple(
            {
                "actual_outcome": str(item.actual_outcome),
                "data_version": request.config.config_snapshot_id,
                "evaluation_policy": request.config.policy_version,
                "observation_id": item.observation_id,
                "observation_time_utc": item.outcome_time_utc,
                "original_prediction": str(item.predicted_score),
                "split": item.split.value,
            }
            for item in observations
        )
        return BacktestResult(
            result_id=f"result-{request.request_id}",
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            config_snapshot_id=request.config.config_snapshot_id,
            status=status,
            metrics={
                "capacity_failure_count": capacity_failures,
                "mean_absolute_error": mean_error,
                "mean_net_return": mean_net_return,
                "minimum_net_return": min(net_returns),
                "observation_count": len(observations),
                "random_seed": request.config.random_seed,
            },
            regime_metrics={
                key: sum(values, Decimal("0")) / Decimal(len(values))
                for key, values in regime_values.items()
            },
            factor_attribution={
                key: sum(values, Decimal("0")) / Decimal(len(values))
                for key, values in factor_values.items()
            },
            failure_codes=tuple(failures),
            outcome_labels=outcomes,
            source_evidence_ids=tuple(
                item.evidence_id for item in request.evidence
            ),
        )
