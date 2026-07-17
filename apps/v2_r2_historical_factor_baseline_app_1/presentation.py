from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .baseline import HistoricalBaseline
from .boundary import V2_R2_HISTORICAL_BASELINE_BOUNDARY


@dataclass(frozen=True)
class HistoricalBaselineReadModel:
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_read_model(baseline: HistoricalBaseline) -> HistoricalBaselineReadModel:
    boundary = V2_R2_HISTORICAL_BASELINE_BOUNDARY
    return HistoricalBaselineReadModel(
        {
            "phase": "V2-R2-HISTORICAL-FACTOR-BASELINE-APP-1",
            "status": baseline.status,
            "sample_count": baseline.sample_count,
            "replay_hash": baseline.replay_hash,
            "observation_ids": baseline.observation_ids,
            "read_only": boundary.read_only_presentation,
            "operator_review_required": boundary.operator_review_required,
            "registered_artifact_only": boundary.registered_artifact_only,
            "factor_activation_allowed": False,
            "official_scoring_allowed": False,
            "candidate_ranking_allowed": False,
            "order_path_allowed": False,
            "real_execution_allowed": False,
        }
    )
