from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    RegisteredClockEventState,
)
from apps.v2_r25_local_causal_transmission_graph_foundation_app_1 import (
    V2_R25_LOCAL_CAUSAL_TRANSMISSION_GRAPH_BOUNDARY,
    LocalCausalTransmissionGraphRegistry,
    RegisteredCausalTransmissionGraph,
    TransmissionEdge,
    TransmissionNode,
    V2R25LocalCausalTransmissionGraphBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_causal_transmission_graphs,
)


def _source() -> InstitutionalCalendarSource:
    return InstitutionalCalendarSource(
        source_id="registered-official-source",
        source_kind="OFFICIAL",
        registered_artifact_id="registered-causal-source",
        artifact_version="artifact-v1",
        license_id="official-local-research-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )


def _event() -> InstitutionalCalendarEvent:
    return InstitutionalCalendarEvent(
        record_id="policy-event-r0",
        calendar_id="institutional-calendar-v1",
        event_id="policy-event",
        event_type="POLICY_MEETING",
        market="a-share",
        horizon="event-window",
        event_at_utc="2026-01-02T10:00:00Z",
        publication_at_utc="2026-01-02T08:00:00Z",
        first_legally_available_at_utc="2026-01-02T08:01:00Z",
        retrieved_at_utc="2026-01-02T08:02:00Z",
        ingested_at_utc="2026-01-02T08:03:00Z",
        first_tradable_at_utc="2026-01-02T08:05:00Z",
        source=_source(),
        content_sha256="a" * 64,
    )


def _state(event: InstitutionalCalendarEvent) -> RegisteredClockEventState:
    return RegisteredClockEventState(
        state_id="institutional-policy-state",
        state_version="state-v1",
        clock_type="INSTITUTIONAL",
        state_kind="POST_EVENT_DIGESTION",
        evidence_group="NEUTRAL",
        hypothesis_id="registered-policy-context",
        market="a-share",
        horizon="event-window",
        effective_from_utc="2026-01-02T08:00:00Z",
        effective_to_utc="2026-01-02T12:00:00Z",
        available_at_utc="2026-01-02T08:10:00Z",
        source_event=event,
        confidence_bps=5000,
    )


def _node_pair(event: InstitutionalCalendarEvent) -> tuple[TransmissionNode, ...]:
    return (
        TransmissionNode(
            node_id="policy-release",
            node_kind="EVENT",
            label="registered-policy-release",
            observed_not_inferred=True,
            source_record_hash=event.record_hash,
        ),
        TransmissionNode(
            node_id="industry-demand",
            node_kind="INDUSTRY",
            label="industry-demand-hypothesis",
            observed_not_inferred=False,
            hypothesis_id="policy-to-demand-hypothesis",
        ),
    )


def _edge(
    event: InstitutionalCalendarEvent,
    state: RegisteredClockEventState,
    **changes: object,
) -> TransmissionEdge:
    values: dict[str, object] = {
        "edge_id": "policy-demand-edge",
        "source_node_id": "policy-release",
        "target_node_id": "industry-demand",
        "relation_type": "TRANSMITS",
        "evidence_group": "SUPPORTING",
        "lag_seconds": 3600,
        "decay_half_life_seconds": 86400,
        "evidence_record_hashes": (event.record_hash,),
        "source_state_hashes": (state.state_hash,),
        "alternative_explanation_ids": ("global-demand-shift",),
        "invalidation_condition_ids": ("policy-language-reversal",),
        "correlation_group_id": "policy-release-evidence",
        "available_at_utc": "2026-01-02T08:11:00Z",
    }
    values.update(changes)
    return TransmissionEdge(**values)  # type: ignore[arg-type]


def _graph(**changes: object) -> RegisteredCausalTransmissionGraph:
    event = _event()
    state = _state(event)
    values: dict[str, object] = {
        "graph_id": "policy-transmission-graph",
        "graph_version": "graph-v1",
        "graph_type": "POLICY",
        "market": "a-share",
        "horizon": "event-window",
        "effective_from_utc": "2026-01-02T08:00:00Z",
        "effective_to_utc": "2026-01-02T12:00:00Z",
        "available_at_utc": "2026-01-02T08:12:00Z",
        "source_events": (event,),
        "source_states": (state,),
        "nodes": _node_pair(event),
        "edges": (_edge(event, state),),
    }
    values.update(changes)
    return RegisteredCausalTransmissionGraph(**values)  # type: ignore[arg-type]


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R25_LOCAL_CAUSAL_TRANSMISSION_GRAPH_BOUNDARY

    assert boundary.registered_artifact_only is True
    assert boundary.causal_proof_claim_allowed is False
    assert boundary.automatic_edge_selection_allowed is False
    assert boundary.factor_activation_allowed is False
    assert boundary.order_or_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R25LocalCausalTransmissionGraphBoundary(causal_proof_claim_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.edge_deletion_allowed = True  # type: ignore[misc]


def test_d2_nodes_separate_observed_evidence_from_inference() -> None:
    event = _event()
    with pytest.raises(ValueError, match="observed node requires source record only"):
        TransmissionNode(
            node_id="bad-observed",
            node_kind="EVENT",
            label="bad-observed",
            observed_not_inferred=True,
            hypothesis_id="invented-source",
        )
    with pytest.raises(ValueError, match="inferred node requires hypothesis id only"):
        TransmissionNode(
            node_id="bad-inferred",
            node_kind="POLICY",
            label="bad-inferred",
            observed_not_inferred=False,
            source_record_hash=event.record_hash,
        )


def test_d2_edges_require_lineage_alternatives_and_invalidation() -> None:
    event = _event()
    state = _state(event)
    with pytest.raises(ValueError, match="alternative explanation"):
        _edge(event, state, alternative_explanation_ids=())
    with pytest.raises(ValueError, match="invalidation condition"):
        _edge(event, state, invalidation_condition_ids=())
    with pytest.raises(ValueError, match="event and state evidence lineage"):
        _edge(event, state, source_state_hashes=())
    with pytest.raises(ValueError, match="unusable evidence"):
        _edge(event, state, evidence_group="STALE")


def test_d3_graph_rejects_broken_lineage_and_causal_activation() -> None:
    graph = _graph()
    event = graph.source_events[0]
    state = graph.source_states[0]
    bad_edge = _edge(event, state, evidence_record_hashes=("b" * 64,))
    with pytest.raises(ValueError, match="edge event evidence"):
        _graph(edges=(bad_edge,))
    with pytest.raises(ValueError, match="non-activated causal hypothesis"):
        _graph(causal_proof_claimed=True)
    with pytest.raises(ValueError, match="non-activated causal hypothesis"):
        _graph(factor_activated=True)


def test_d3_registry_is_append_only_and_rejects_duplicates() -> None:
    graph = _graph()
    registry = LocalCausalTransmissionGraphRegistry().append(graph)

    with pytest.raises(ValueError, match="duplicate causal transmission graph identity"):
        registry.append(graph)
    assert registry.graphs == (graph,)


def test_d4_resolution_is_point_in_time_and_half_open() -> None:
    registry = LocalCausalTransmissionGraphRegistry().append(_graph())
    unavailable = resolve_causal_transmission_graphs(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:11:59Z",
        as_of_utc="2026-01-02T08:11:59Z",
    )
    resolved = resolve_causal_transmission_graphs(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    expired = resolve_causal_transmission_graphs(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T12:00:00Z",
        as_of_utc="2026-01-02T12:00:00Z",
    )

    assert unavailable.state == "MISSING"
    assert resolved.state == "RESOLVED"
    assert expired.state == "MISSING"


def test_d4_future_observation_is_rejected() -> None:
    with pytest.raises(ValueError, match="future observation"):
        resolve_causal_transmission_graphs(
            LocalCausalTransmissionGraphRegistry().append(_graph()),
            market="a-share",
            horizon="event-window",
            observed_at_utc="2026-01-02T09:00:00Z",
            as_of_utc="2026-01-02T08:59:59Z",
        )


def test_d5_contradiction_correlation_and_alternatives_are_preserved() -> None:
    graph = _graph()
    event = graph.source_events[0]
    state = graph.source_states[0]
    opposing = _edge(
        event,
        state,
        edge_id="policy-demand-opposing-edge",
        evidence_group="OPPOSING",
        edge_state="INVALIDATED",
        alternative_explanation_ids=("inventory-cycle",),
        invalidation_condition_ids=("observed-demand-contraction",),
    )
    graph = replace(graph, edges=(*graph.edges, opposing))
    snapshot = resolve_causal_transmission_graphs(
        LocalCausalTransmissionGraphRegistry().append(graph),
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )

    assert snapshot.evidence_groups["SUPPORTING"] == ("policy-demand-edge",)
    assert snapshot.evidence_groups["OPPOSING"] == ("policy-demand-opposing-edge",)
    assert snapshot.correlation_groups["policy-release-evidence"] == (
        "policy-demand-edge",
        "policy-demand-opposing-edge",
    )
    assert snapshot.invalidated_edge_ids == ("policy-demand-opposing-edge",)
    assert snapshot.alternative_explanations["policy-demand-edge"] == (
        "global-demand-shift",
    )
    assert "CORRELATED_EVIDENCE_PRESERVED_NOT_DOUBLE_COUNTED" in snapshot.reason_codes
    assert snapshot.selected_edge_id is None


def test_d5_market_horizon_isolation_and_hash_determinism() -> None:
    registry = LocalCausalTransmissionGraphRegistry().append(_graph())
    first = resolve_causal_transmission_graphs(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    repeated = resolve_causal_transmission_graphs(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    isolated = resolve_causal_transmission_graphs(
        registry,
        market="btc",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )

    assert first.snapshot_hash == repeated.snapshot_hash
    assert isolated.state == "MISSING"
    assert isolated.active_graphs == ()


def test_d6_read_model_and_acceptance_are_read_only() -> None:
    registry = LocalCausalTransmissionGraphRegistry().append(_graph())
    snapshot = resolve_causal_transmission_graphs(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["causal_hypotheses_only"] is True
    assert model.payload["causal_proof"] is False
    assert model.payload["factor_activation"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.automatic_approval is False
    assert acceptance.factor_activated is False
    assert acceptance.action_created is False
    with pytest.raises(TypeError):
        model.payload["causal_proof"] = True  # type: ignore[index]
