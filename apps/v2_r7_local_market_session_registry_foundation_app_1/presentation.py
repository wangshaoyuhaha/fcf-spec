from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalMarketSessionRegistry


@dataclass(frozen=True)
class LocalMarketSessionReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalMarketSessionRegistry) -> LocalMarketSessionReadModel:
    payload = MappingProxyType(
        {
            "definition_count": len(registry.definitions),
            "definition_hashes": tuple(
                item.definition_hash for item in registry.definitions
            ),
            "registered_artifact_only": True,
            "operator_review_required": True,
            "network_source": False,
            "system_clock_authority": False,
            "hardcoded_venue_schedule": False,
            "signal_or_recommendation": False,
            "order_or_execution": False,
        }
    )
    return LocalMarketSessionReadModel(payload=payload)
