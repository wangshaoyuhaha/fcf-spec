from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import V2_R1_FACTOR_CONTRACT_BOUNDARY
from .registries import FactorRegistry, ForecastTargetRegistry
from .state_sync import StateSyncAnchor


@dataclass(frozen=True)
class V2R1ReadModel:
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.payload, Mapping):
            raise ValueError("read model payload must be a mapping")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_v2_r1_read_model(
    factor_registry: FactorRegistry,
    target_registry: ForecastTargetRegistry,
    anchors: tuple[StateSyncAnchor, ...],
    *,
    as_of_utc: str,
) -> V2R1ReadModel:
    factor_ids = tuple(sorted(factor_registry.definitions))
    target_ids = tuple(sorted(target_registry.definitions))
    ordered_anchors = tuple(sorted(anchors, key=lambda item: item.event_id))
    if len({anchor.event_id for anchor in ordered_anchors}) != len(ordered_anchors):
        raise ValueError("State-Sync event ids must be unique")
    payload = {
        "phase": "V2-R1-FACTOR-CONTRACT-FOUNDATION-APP-1",
        "mode": "paper-only",
        "factor_count": len(factor_ids),
        "factor_ids": factor_ids,
        "factor_lifecycle": MappingProxyType(
            {
                factor_id: factor_registry.current_lifecycle(factor_id).value
                for factor_id in factor_ids
            }
        ),
        "forecast_target_count": len(target_ids),
        "forecast_target_ids": target_ids,
        "state_sync_count": len(ordered_anchors),
        "state_sync": tuple(
            MappingProxyType(
                {
                    "event_id": anchor.event_id,
                    "instrument_id": anchor.instrument_id,
                    "state_hash": anchor.state_hash,
                    "status": anchor.status_at(as_of_utc),
                    "expires_at_utc": anchor.expires_at_utc,
                    "registered_artifact_id": anchor.registered_artifact_id,
                }
            )
            for anchor in ordered_anchors
        ),
        "read_only": V2_R1_FACTOR_CONTRACT_BOUNDARY.read_only_presentation,
        "operator_review_required": (
            V2_R1_FACTOR_CONTRACT_BOUNDARY.operator_review_required
        ),
        "deterministic_engine_authority": True,
        "registered_evidence_authority": True,
        "ai_advisory_only": True,
        "factor_calculation_allowed": False,
        "official_scoring_allowed": False,
        "automatic_activation_allowed": False,
        "order_path_allowed": False,
        "real_execution_allowed": False,
    }
    return V2R1ReadModel(payload=payload)
