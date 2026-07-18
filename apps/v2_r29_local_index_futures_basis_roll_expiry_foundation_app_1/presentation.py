from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalIndexFuturesBasisRollExpiryRegistry


@dataclass(frozen=True)
class LocalIndexFuturesBasisRollExpiryReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalIndexFuturesBasisRollExpiryRegistry,
) -> LocalIndexFuturesBasisRollExpiryReadModel:
    return LocalIndexFuturesBasisRollExpiryReadModel(
        MappingProxyType(
            {
                "contract_count": len(registry.contracts),
                "observation_count": len(registry.observations),
                "record_count": len(registry.records),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "fixed_third_friday_override": False,
                "bottom_claim": False,
                "participant_intent_claim": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
