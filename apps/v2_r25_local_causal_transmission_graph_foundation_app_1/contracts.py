from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    EVIDENCE_GROUPS,
    RegisteredClockEventState,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1.contracts import (
    sha256_text,
)


GRAPH_TYPES = ("POLICY", "INDUSTRY_SUPPLY", "CAPITAL_TRANSMISSION")
NODE_KINDS = (
    "EVENT",
    "CLOCK_STATE",
    "POLICY",
    "INDUSTRY",
    "SUPPLY",
    "CAPITAL",
    "MARKET",
    "ASSET",
    "OUTCOME",
)
RELATION_TYPES = ("TRANSMITS", "SUPPORTS", "OPPOSES", "ALTERNATIVE_TO")
EDGE_STATES = ("ACTIVE", "INVALIDATED")


def _hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _identifiers(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(identifier(value, name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} values must be unique")
    return normalized


def _hashes(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(sha256_text(value, name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} values must be unique")
    return normalized


@dataclass(frozen=True)
class TransmissionNode:
    node_id: str
    node_kind: str
    label: str
    observed_not_inferred: bool
    source_record_hash: str | None = None
    hypothesis_id: str | None = None
    node_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_id", identifier(self.node_id, "node_id"))
        object.__setattr__(self, "label", identifier(self.label, "label"))
        node_kind = str(self.node_kind).strip().upper()
        if node_kind not in NODE_KINDS:
            raise ValueError("node_kind is not registered")
        object.__setattr__(self, "node_kind", node_kind)
        if not isinstance(self.observed_not_inferred, bool):
            raise ValueError("observed_not_inferred must be boolean")
        if self.observed_not_inferred:
            if self.source_record_hash is None or self.hypothesis_id is not None:
                raise ValueError("observed node requires source record only")
            object.__setattr__(
                self,
                "source_record_hash",
                sha256_text(self.source_record_hash, "source_record_hash"),
            )
        else:
            if self.hypothesis_id is None or self.source_record_hash is not None:
                raise ValueError("inferred node requires hypothesis id only")
            object.__setattr__(
                self, "hypothesis_id", identifier(self.hypothesis_id, "hypothesis_id")
            )
        payload = {
            "hypothesis_id": self.hypothesis_id,
            "label": self.label,
            "node_id": self.node_id,
            "node_kind": self.node_kind,
            "observed_not_inferred": self.observed_not_inferred,
            "source_record_hash": self.source_record_hash,
        }
        object.__setattr__(self, "node_hash", _hash(payload))


@dataclass(frozen=True)
class TransmissionEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    evidence_group: str
    lag_seconds: int
    decay_half_life_seconds: int
    evidence_record_hashes: tuple[str, ...]
    source_state_hashes: tuple[str, ...]
    alternative_explanation_ids: tuple[str, ...]
    invalidation_condition_ids: tuple[str, ...]
    correlation_group_id: str
    available_at_utc: str
    edge_state: str = "ACTIVE"
    operator_registered: bool = True
    edge_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("edge_id", "source_node_id", "target_node_id", "correlation_group_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        if self.source_node_id == self.target_node_id:
            raise ValueError("transmission edge cannot be a self-loop")
        for name, allowed in (
            ("relation_type", RELATION_TYPES),
            ("evidence_group", EVIDENCE_GROUPS),
            ("edge_state", EDGE_STATES),
        ):
            value = str(getattr(self, name)).strip().upper()
            if value not in allowed:
                raise ValueError(f"{name} is not registered")
            object.__setattr__(self, name, value)
        if isinstance(self.lag_seconds, bool) or self.lag_seconds < 0:
            raise ValueError("lag_seconds must be nonnegative")
        if (
            isinstance(self.decay_half_life_seconds, bool)
            or self.decay_half_life_seconds <= 0
        ):
            raise ValueError("decay_half_life_seconds must be positive")
        object.__setattr__(
            self,
            "evidence_record_hashes",
            _hashes(tuple(self.evidence_record_hashes), "evidence_record_hash"),
        )
        object.__setattr__(
            self,
            "source_state_hashes",
            _hashes(tuple(self.source_state_hashes), "source_state_hash"),
        )
        object.__setattr__(
            self,
            "alternative_explanation_ids",
            _identifiers(
                tuple(self.alternative_explanation_ids), "alternative_explanation_id"
            ),
        )
        object.__setattr__(
            self,
            "invalidation_condition_ids",
            _identifiers(
                tuple(self.invalidation_condition_ids), "invalidation_condition_id"
            ),
        )
        if not self.alternative_explanation_ids:
            raise ValueError("transmission edge requires an alternative explanation")
        if not self.invalidation_condition_ids:
            raise ValueError("transmission edge requires an invalidation condition")
        if self.evidence_group in {"SUPPORTING", "OPPOSING", "NEUTRAL"} and not (
            self.evidence_record_hashes and self.source_state_hashes
        ):
            raise ValueError("usable edge requires event and state evidence lineage")
        if self.evidence_group in {"MISSING", "STALE", "BLOCKED"} and self.edge_state == "ACTIVE":
            raise ValueError("unusable evidence cannot create an active edge")
        if self.edge_state == "INVALIDATED" and self.evidence_group not in {
            "OPPOSING",
            "STALE",
            "BLOCKED",
        }:
            raise ValueError("invalidated edge must preserve opposing or unusable evidence")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if self.operator_registered is not True:
            raise ValueError("transmission edge requires Operator registration")
        payload = {
            "alternative_explanation_ids": self.alternative_explanation_ids,
            "available_at_utc": self.available_at_utc,
            "correlation_group_id": self.correlation_group_id,
            "decay_half_life_seconds": self.decay_half_life_seconds,
            "edge_id": self.edge_id,
            "edge_state": self.edge_state,
            "evidence_group": self.evidence_group,
            "evidence_record_hashes": self.evidence_record_hashes,
            "invalidation_condition_ids": self.invalidation_condition_ids,
            "lag_seconds": self.lag_seconds,
            "operator_registered": self.operator_registered,
            "relation_type": self.relation_type,
            "source_node_id": self.source_node_id,
            "source_state_hashes": self.source_state_hashes,
            "target_node_id": self.target_node_id,
        }
        object.__setattr__(self, "edge_hash", _hash(payload))


@dataclass(frozen=True)
class RegisteredCausalTransmissionGraph:
    graph_id: str
    graph_version: str
    graph_type: str
    market: str
    horizon: str
    effective_from_utc: str
    effective_to_utc: str
    available_at_utc: str
    source_events: tuple[InstitutionalCalendarEvent, ...]
    source_states: tuple[RegisteredClockEventState, ...]
    nodes: tuple[TransmissionNode, ...]
    edges: tuple[TransmissionEdge, ...]
    causal_proof_claimed: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    graph_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("graph_id", "graph_version", "market", "horizon"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        graph_type = str(self.graph_type).strip().upper()
        if graph_type not in GRAPH_TYPES:
            raise ValueError("graph_type is not registered")
        object.__setattr__(self, "graph_type", graph_type)
        for name in ("effective_from_utc", "effective_to_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.effective_to_utc) <= instant(self.effective_from_utc):
            raise ValueError("transmission graph end must follow start")
        events = tuple(self.source_events)
        states = tuple(self.source_states)
        nodes = tuple(self.nodes)
        edges = tuple(self.edges)
        if not events or not all(isinstance(item, InstitutionalCalendarEvent) for item in events):
            raise ValueError("graph requires registered R23 event evidence")
        if not states or not all(isinstance(item, RegisteredClockEventState) for item in states):
            raise ValueError("graph requires registered R24 clock states")
        if len({item.record_hash for item in events}) != len(events):
            raise ValueError("duplicate source event evidence is prohibited")
        if len({item.state_hash for item in states}) != len(states):
            raise ValueError("duplicate source state evidence is prohibited")
        event_hashes = {item.record_hash for item in events}
        state_hashes = {item.state_hash for item in states}
        if any(item.market != self.market or item.horizon != self.horizon for item in events):
            raise ValueError("event evidence market and horizon must match graph")
        if any(item.market != self.market or item.horizon != self.horizon for item in states):
            raise ValueError("clock state market and horizon must match graph")
        if any(item.source_event.record_hash not in event_hashes for item in states):
            raise ValueError("clock state lineage must resolve to graph event evidence")
        if len(nodes) < 2 or not all(isinstance(item, TransmissionNode) for item in nodes):
            raise ValueError("graph requires at least two transmission nodes")
        if not edges or not all(isinstance(item, TransmissionEdge) for item in edges):
            raise ValueError("graph requires transmission edges")
        if len({item.node_id for item in nodes}) != len(nodes):
            raise ValueError("duplicate transmission node id is prohibited")
        if len({item.edge_id for item in edges}) != len(edges):
            raise ValueError("duplicate transmission edge id is prohibited")
        node_ids = {item.node_id for item in nodes}
        for node in nodes:
            if node.source_record_hash is not None and node.source_record_hash not in event_hashes:
                raise ValueError("observed node source must resolve to graph event evidence")
        for edge in edges:
            if edge.source_node_id not in node_ids or edge.target_node_id not in node_ids:
                raise ValueError("edge endpoints must resolve to graph nodes")
            if not set(edge.evidence_record_hashes).issubset(event_hashes):
                raise ValueError("edge event evidence must resolve to graph lineage")
            if not set(edge.source_state_hashes).issubset(state_hashes):
                raise ValueError("edge state evidence must resolve to graph lineage")
        available = instant(self.available_at_utc)
        lineage_times = (
            *(instant(item.ingested_at_utc) for item in events),
            *(instant(item.available_at_utc) for item in states),
            *(instant(item.available_at_utc) for item in edges),
        )
        if any(available < value for value in lineage_times):
            raise ValueError("graph availability cannot precede evidence lineage")
        if self.causal_proof_claimed or self.factor_activated:
            raise ValueError("graph must remain a non-activated causal hypothesis")
        if self.operator_registered is not True:
            raise ValueError("transmission graph requires Operator registration")
        object.__setattr__(self, "source_events", events)
        object.__setattr__(self, "source_states", states)
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)
        payload = {
            "available_at_utc": self.available_at_utc,
            "causal_proof_claimed": self.causal_proof_claimed,
            "edge_hashes": [item.edge_hash for item in edges],
            "effective_from_utc": self.effective_from_utc,
            "effective_to_utc": self.effective_to_utc,
            "factor_activated": self.factor_activated,
            "graph_id": self.graph_id,
            "graph_type": self.graph_type,
            "graph_version": self.graph_version,
            "horizon": self.horizon,
            "market": self.market,
            "node_hashes": [item.node_hash for item in nodes],
            "operator_registered": self.operator_registered,
            "source_event_hashes": [item.record_hash for item in events],
            "source_state_hashes": [item.state_hash for item in states],
        }
        object.__setattr__(self, "graph_hash", _hash(payload))
