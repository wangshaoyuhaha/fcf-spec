from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalEquitySupplyPressureRegistry


@dataclass(frozen=True)
class LocalEquitySupplyPressureReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalEquitySupplyPressureRegistry) -> LocalEquitySupplyPressureReadModel:
    return LocalEquitySupplyPressureReadModel(
        MappingProxyType(
            {
                "event_count": len(registry.events),
                "observation_count": len(registry.observations),
                "record_count": len(registry.records),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "unlock_equals_sale_claim": False,
                "forced_sale_claim": False,
                "holder_intent_claim": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
