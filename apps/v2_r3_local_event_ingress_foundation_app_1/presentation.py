from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import V2_R3_LOCAL_EVENT_INGRESS_BOUNDARY
from .ingress import BoundedLocalEventIngress
from .replay import ReplayCheckpoint, events_hash


@dataclass(frozen=True)
class LocalEventIngressReadModel:
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_read_model(
    ingress: BoundedLocalEventIngress,
    checkpoint: ReplayCheckpoint,
) -> LocalEventIngressReadModel:
    boundary = V2_R3_LOCAL_EVENT_INGRESS_BOUNDARY
    checkpoint_valid = (
        checkpoint.event_count == len(ingress.events)
        and checkpoint.events_hash == events_hash(ingress.events)
        and dict(checkpoint.last_sequences) == dict(ingress.last_sequences)
    )
    return LocalEventIngressReadModel(
        {
            "phase": "V2-R3-LOCAL-EVENT-INGRESS-FOUNDATION-APP-1",
            "status": (
                "READY_FOR_OPERATOR_REVIEW" if checkpoint_valid else "BLOCKED"
            ),
            "event_count": len(ingress.events),
            "stream_count": len(ingress.last_sequences),
            "last_sequences": MappingProxyType(dict(ingress.last_sequences)),
            "checkpoint_id": checkpoint.checkpoint_id,
            "checkpoint_hash": checkpoint.events_hash,
            "read_only": boundary.read_only_presentation,
            "operator_review_required": boundary.operator_review_required,
            "registered_artifact_only": boundary.registered_artifact_only,
            "external_source_allowed": False,
            "market_selection_allowed": False,
            "factor_activation_allowed": False,
            "official_scoring_allowed": False,
            "candidate_ranking_allowed": False,
            "order_path_allowed": False,
            "real_execution_allowed": False,
        }
    )
