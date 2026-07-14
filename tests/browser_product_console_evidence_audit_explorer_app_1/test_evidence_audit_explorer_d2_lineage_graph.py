from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    ConsoleArtifactRecord,
    ConsoleReadModel,
    EvidenceIntegrityState,
    EvidenceRelation,
    build_evidence_artifact_graph,
    build_evidence_correlation_lineage,
    build_evidence_provenance_chain,
)


def _record(
    artifact_id: str,
    artifact_type: str,
    payload: dict,
) -> ConsoleArtifactRecord:
    return ConsoleArtifactRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        relative_path=f"registered/{artifact_id}.json",
        content_sha256="a" * 64,
        payload=payload,
    )


def _model(
    records: tuple[ConsoleArtifactRecord, ...],
) -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-d2",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=tuple(
            record.artifact_id for record in records
        ),
        artifact_records=records,
    )


def test_d2_builds_registered_artifact_graph_deterministically():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record(
                    "validation-1",
                    "paper_validation",
                    {
                        "validates_artifact_id": "candidate-1",
                        "status": "PASS",
                    },
                ),
                _record(
                    "data-1",
                    "data_snapshot",
                    {"as_of": "2026-07-14"},
                ),
                _record(
                    "candidate-1",
                    "ranked_watchlist",
                    {
                        "source_artifact_id": "data-1",
                        "status": "REVIEW_REQUIRED",
                    },
                ),
            )
        )
    )

    assert graph.state == "AVAILABLE"
    assert tuple(node.artifact_id for node in graph.nodes) == (
        "data-1",
        "validation-1",
        "candidate-1",
    )
    assert all(
        node.integrity_state is EvidenceIntegrityState.VERIFIED
        for node in graph.nodes
    )
    assert tuple(
        (
            item.source_artifact_id,
            item.relation,
            item.target_artifact_id,
        )
        for item in graph.relationships
    ) == (
        (
            "candidate-1",
            EvidenceRelation.DERIVED_FROM,
            "data-1",
        ),
        (
            "validation-1",
            EvidenceRelation.VALIDATES,
            "candidate-1",
        ),
    )


def test_d2_graph_exposes_registered_lookup_and_adjacency():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record("data-1", "data_snapshot", {}),
                _record(
                    "candidate-1",
                    "ranked_watchlist",
                    {"source_artifact_id": "data-1"},
                ),
            )
        )
    )

    assert graph.by_artifact_id("data-1").artifact_type == (
        "data_snapshot"
    )
    assert tuple(
        item.target_artifact_id
        for item in graph.outgoing("candidate-1")
    ) == ("data-1",)
    assert tuple(
        item.source_artifact_id
        for item in graph.incoming("data-1")
    ) == ("candidate-1",)

    with pytest.raises(KeyError):
        graph.by_artifact_id("not-registered")


def test_d2_unregistered_reference_marks_graph_incomplete():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record(
                    "candidate-1",
                    "ranked_watchlist",
                    {
                        "source_artifact_ids": [
                            "data-missing",
                            "data-missing",
                        ]
                    },
                ),
            )
        )
    )

    assert graph.state == "INCOMPLETE"
    assert graph.relationships == ()
    assert graph.unresolved_artifact_ids == (
        "data-missing",
    )


@pytest.mark.parametrize(
    "payload",
    (
        {"source_artifact_ids": {"bad": "mapping"}},
        {"source_artifact_ids": [""]},
        {"source_artifact_id": "candidate-1"},
    ),
)
def test_d2_graph_rejects_malformed_or_self_reference(payload):
    with pytest.raises(ValueError):
        build_evidence_artifact_graph(
            _model(
                (
                    _record(
                        "candidate-1",
                        "ranked_watchlist",
                        payload,
                    ),
                )
            )
        )


def test_d2_correlation_lineage_summarizes_graph():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record("data-1", "data_snapshot", {}),
                _record("data-2", "data_snapshot", {}),
                _record(
                    "candidate-1",
                    "ranked_watchlist",
                    {
                        "source_artifact_ids": [
                            "data-1",
                            "data-2",
                        ]
                    },
                ),
            )
        )
    )
    lineage = build_evidence_correlation_lineage(graph)

    assert lineage.correlation_id == "corr-d2"
    assert lineage.state == "AVAILABLE"
    assert lineage.artifact_ids == (
        "data-1",
        "data-2",
        "candidate-1",
    )
    assert dict(lineage.artifact_type_counts) == {
        "data_snapshot": 2,
        "ranked_watchlist": 1,
    }
    assert lineage.relationship_count == 2


def test_d2_provenance_chain_traces_registered_upstream():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record("data-1", "data_snapshot", {}),
                _record(
                    "candidate-1",
                    "ranked_watchlist",
                    {"source_artifact_id": "data-1"},
                ),
                _record(
                    "validation-1",
                    "paper_validation",
                    {
                        "validates_artifact_id": "candidate-1"
                    },
                ),
                _record(
                    "review-1",
                    "operator_review",
                    {
                        "reviewed_artifact_id": "validation-1"
                    },
                ),
                _record(
                    "archive-1",
                    "report_archive",
                    {
                        "archived_artifact_id": "review-1"
                    },
                ),
            )
        )
    )

    chain = build_evidence_provenance_chain(
        graph,
        "archive-1",
    )

    assert chain.state == "AVAILABLE"
    assert tuple(
        (step.depth, step.artifact_id)
        for step in chain.steps
    ) == (
        (0, "archive-1"),
        (1, "review-1"),
        (2, "validation-1"),
        (3, "candidate-1"),
        (4, "data-1"),
    )
    assert tuple(
        step.relation
        for step in chain.steps[1:]
    ) == (
        EvidenceRelation.ARCHIVES,
        EvidenceRelation.REVIEWS,
        EvidenceRelation.VALIDATES,
        EvidenceRelation.DERIVED_FROM,
    )


def test_d2_provenance_chain_detects_cycle_without_looping():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record(
                    "artifact-a",
                    "manifest",
                    {"source_artifact_id": "artifact-b"},
                ),
                _record(
                    "artifact-b",
                    "audit_receipt",
                    {"source_artifact_id": "artifact-a"},
                ),
            )
        )
    )

    chain = build_evidence_provenance_chain(
        graph,
        "artifact-a",
    )

    assert chain.state == "INCOMPLETE"
    assert chain.cycle_detected is True
    assert tuple(
        step.artifact_id for step in chain.steps
    ) == ("artifact-a", "artifact-b")


def test_d2_provenance_chain_enforces_depth_limit():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record("data-1", "data_snapshot", {}),
                _record(
                    "candidate-1",
                    "ranked_watchlist",
                    {"source_artifact_id": "data-1"},
                ),
                _record(
                    "validation-1",
                    "paper_validation",
                    {
                        "validates_artifact_id": "candidate-1"
                    },
                ),
            )
        )
    )

    chain = build_evidence_provenance_chain(
        graph,
        "validation-1",
        max_depth=1,
    )

    assert chain.state == "INCOMPLETE"
    assert chain.max_depth_reached is True
    assert tuple(
        step.artifact_id for step in chain.steps
    ) == ("validation-1", "candidate-1")


def test_d2_empty_model_builds_empty_graph_and_lineage():
    graph = build_evidence_artifact_graph(_model(()))
    lineage = build_evidence_correlation_lineage(graph)

    assert graph.state == "EMPTY"
    assert graph.nodes == ()
    assert graph.relationships == ()
    assert lineage.state == "EMPTY"
    assert lineage.artifact_ids == ()


def test_d2_graph_does_not_infer_risk_or_contradiction_evidence():
    graph = build_evidence_artifact_graph(
        _model(
            (
                _record(
                    "ai-1",
                    "ai_explanation",
                    {
                        "risk_flags": ["RISK_A"],
                        "contradiction_codes": ["CONTRA_A"],
                    },
                ),
            )
        )
    )

    node = graph.by_artifact_id("ai-1")
    assert node.risk_flags == ()
    assert node.contradiction_codes == ()
