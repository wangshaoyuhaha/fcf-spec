from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import GRAPH_TYPES
from .registry import LocalCausalTransmissionGraphRegistry


@dataclass(frozen=True)
class LocalCausalTransmissionGraphReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalCausalTransmissionGraphRegistry,
) -> LocalCausalTransmissionGraphReadModel:
    return LocalCausalTransmissionGraphReadModel(
        payload=MappingProxyType(
            {
                "graph_count": len(registry.graphs),
                "graph_types": GRAPH_TYPES,
                "graph_hashes": tuple(graph.graph_hash for graph in registry.graphs),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "causal_hypotheses_only": True,
                "causal_proof": False,
                "automatic_edge_selection": False,
                "edge_deletion": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
