from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalEventReactionQualityRegistry


@dataclass(frozen=True)
class LocalEventReactionQualityReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalEventReactionQualityRegistry,
) -> LocalEventReactionQualityReadModel:
    return LocalEventReactionQualityReadModel(
        payload=MappingProxyType(
            {
                "window_count": len(registry.windows),
                "observation_count": len(registry.observations),
                "quality_count": len(registry.quality_records),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "ai_generated_label": False,
                "participant_intent_inference": False,
                "immature_outcome_promotion": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
