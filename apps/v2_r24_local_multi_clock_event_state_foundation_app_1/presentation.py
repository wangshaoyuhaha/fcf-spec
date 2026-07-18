from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import CLOCK_TYPES
from .registry import LocalMultiClockEventStateRegistry


@dataclass(frozen=True)
class LocalMultiClockEventStateReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalMultiClockEventStateRegistry,
) -> LocalMultiClockEventStateReadModel:
    return LocalMultiClockEventStateReadModel(
        payload=MappingProxyType(
            {
                "state_count": len(registry.states),
                "clock_types": CLOCK_TYPES,
                "state_hashes": tuple(state.state_hash for state in registry.states),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "network_source": False,
                "live_clock": False,
                "destructive_state_selection": False,
                "conflict_deletion": False,
                "winner_selection": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
