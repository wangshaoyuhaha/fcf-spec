from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalConsensusExpectationGapRegistry


@dataclass(frozen=True)
class LocalConsensusExpectationGapReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalConsensusExpectationGapRegistry,
) -> LocalConsensusExpectationGapReadModel:
    return LocalConsensusExpectationGapReadModel(
        payload=MappingProxyType(
            {
                "consensus_count": len(registry.consensus_snapshots),
                "actual_count": len(registry.actual_observations),
                "gap_count": len(registry.gap_records),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "ai_generated_consensus": False,
                "consensus_imputation": False,
                "future_revision": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
