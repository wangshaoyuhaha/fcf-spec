from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import EVIDENCE_GROUPS

from .contracts import GRAPH_TYPES, RegisteredCausalTransmissionGraph
from .registry import LocalCausalTransmissionGraphRegistry


@dataclass(frozen=True)
class CausalTransmissionGraphSnapshot:
    market: str
    horizon: str
    observed_at_utc: str
    evaluated_at_utc: str
    state: str
    active_graphs: tuple[RegisteredCausalTransmissionGraph, ...]
    graph_groups: Mapping[str, tuple[str, ...]]
    evidence_groups: Mapping[str, tuple[str, ...]]
    correlation_groups: Mapping[str, tuple[str, ...]]
    alternative_explanations: Mapping[str, tuple[str, ...]]
    invalidation_conditions: Mapping[str, tuple[str, ...]]
    invalidated_edge_ids: tuple[str, ...]
    conclusion_policy: str
    selected_edge_id: None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"MISSING", "RESOLVED"}:
            raise ValueError("invalid causal transmission snapshot state")
        if self.conclusion_policy != "HYPOTHESES_ONLY_NO_CAUSAL_PROOF":
            raise ValueError("causal transmission conclusion policy is not closed")
        if self.selected_edge_id is not None:
            raise ValueError("causal transmission snapshot cannot select an edge")
        if self.operator_review_required is not True:
            raise ValueError("causal transmission snapshot requires Operator review")


def resolve_causal_transmission_graphs(
    registry: LocalCausalTransmissionGraphRegistry,
    *,
    market: str,
    horizon: str,
    observed_at_utc: str,
    as_of_utc: str,
) -> CausalTransmissionGraphSnapshot:
    market_id = identifier(market, "market")
    horizon_id = identifier(horizon, "horizon")
    observed_text = utc(observed_at_utc, "observed_at_utc")
    evaluated_text = utc(as_of_utc, "as_of_utc")
    observed = instant(observed_text)
    as_of = instant(evaluated_text)
    if observed > as_of:
        raise ValueError("causal transmission resolution cannot use future observation")
    active = tuple(
        sorted(
            (
                graph
                for graph in registry.graphs
                if graph.market == market_id
                and graph.horizon == horizon_id
                and instant(graph.available_at_utc) <= as_of
                and instant(graph.effective_from_utc)
                <= observed
                < instant(graph.effective_to_utc)
            ),
            key=lambda item: (
                GRAPH_TYPES.index(item.graph_type),
                item.effective_from_utc,
                item.graph_id,
                item.graph_version,
            ),
        )
    )
    edges = tuple(edge for graph in active for edge in graph.edges)
    graph_values = {
        graph_type: tuple(
            graph.graph_id for graph in active if graph.graph_type == graph_type
        )
        for graph_type in GRAPH_TYPES
    }
    evidence_values = {
        group: tuple(sorted(edge.edge_id for edge in edges if edge.evidence_group == group))
        for group in EVIDENCE_GROUPS
    }
    correlation_ids = sorted({edge.correlation_group_id for edge in edges})
    correlation_values = {
        group_id: tuple(
            sorted(edge.edge_id for edge in edges if edge.correlation_group_id == group_id)
        )
        for group_id in correlation_ids
    }
    alternatives = {
        edge.edge_id: edge.alternative_explanation_ids for edge in sorted(edges, key=lambda item: item.edge_id)
    }
    invalidations = {
        edge.edge_id: edge.invalidation_condition_ids for edge in sorted(edges, key=lambda item: item.edge_id)
    }
    invalidated = tuple(
        sorted(edge.edge_id for edge in edges if edge.edge_state == "INVALIDATED")
    )
    state = "RESOLVED" if active else "MISSING"
    reasons = [
        "REGISTERED_CAUSAL_HYPOTHESES_RESOLVED"
        if active
        else "NO_REGISTERED_CAUSAL_HYPOTHESIS_AT_AS_OF"
    ]
    if any(len(values) > 1 for values in correlation_values.values()):
        reasons.append("CORRELATED_EVIDENCE_PRESERVED_NOT_DOUBLE_COUNTED")
    if evidence_values["OPPOSING"] or invalidated:
        reasons.append("CONTRADICTORY_OR_INVALIDATED_EDGES_PRESERVED")
    payload = {
        "active_graph_hashes": [item.graph_hash for item in active],
        "alternative_explanations": alternatives,
        "conclusion_policy": "HYPOTHESES_ONLY_NO_CAUSAL_PROOF",
        "correlation_groups": correlation_values,
        "evaluated_at_utc": evaluated_text,
        "evidence_groups": evidence_values,
        "graph_groups": graph_values,
        "horizon": horizon_id,
        "invalidated_edge_ids": invalidated,
        "invalidation_conditions": invalidations,
        "market": market_id,
        "observed_at_utc": observed_text,
        "reason_codes": reasons,
        "selected_edge_id": None,
        "state": state,
    }
    snapshot_hash = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
            "ascii"
        )
    ).hexdigest()
    return CausalTransmissionGraphSnapshot(
        market=market_id,
        horizon=horizon_id,
        observed_at_utc=observed_text,
        evaluated_at_utc=evaluated_text,
        state=state,
        active_graphs=active,
        graph_groups=MappingProxyType(graph_values),
        evidence_groups=MappingProxyType(evidence_values),
        correlation_groups=MappingProxyType(correlation_values),
        alternative_explanations=MappingProxyType(alternatives),
        invalidation_conditions=MappingProxyType(invalidations),
        invalidated_edge_ids=invalidated,
        conclusion_policy="HYPOTHESES_ONLY_NO_CAUSAL_PROOF",
        selected_edge_id=None,
        reason_codes=tuple(reasons),
        operator_review_required=True,
        snapshot_hash=snapshot_hash,
    )
