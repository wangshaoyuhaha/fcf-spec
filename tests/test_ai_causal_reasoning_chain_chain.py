"""Tests for deterministic causal chain construction."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_causal_reasoning_chain import (
    CausalChainViolation,
    build_deterministic_causal_chain,
    build_registered_causal_claim_record,
    build_registered_causal_evidence_reference,
    build_registered_causal_premise_record,
    validate_causal_chain_edge_record,
    validate_deterministic_causal_chain,
)


def _premise(
    claim_id: str,
    premise_id: str,
    status: str = "REGISTERED",
) -> dict:
    return build_registered_causal_premise_record(
        premise_id=premise_id,
        claim_id=claim_id,
        premise_text="Registered causal premise.",
        registration_status=status,
        source_artifact_ids=[
            f"source-{premise_id}"
        ],
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _evidence(
    claim_id: str,
    evidence_id: str,
    role: str,
    artifact_type: str,
    status: str = "REGISTERED",
) -> dict:
    return build_registered_causal_evidence_reference(
        evidence_ref_id=evidence_id,
        claim_id=claim_id,
        artifact_id=f"artifact-{evidence_id}",
        artifact_type=artifact_type,
        evidence_role=role,
        registration_status=status,
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _claim(
    claim_id: str,
    cause_id: str,
    effect_id: str,
    *,
    support_status: str = "REGISTERED",
    include_premise: bool = True,
) -> dict:
    premises = (
        [_premise(
            claim_id,
            f"premise-{claim_id}",
        )]
        if include_premise
        else []
    )

    evidence = [
        _evidence(
            claim_id,
            f"support-{claim_id}",
            "SUPPORTING",
            "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
            support_status,
        ),
        _evidence(
            claim_id,
            f"counter-{claim_id}",
            "COUNTEREVIDENCE",
            "REGISTERED_COUNTEREVIDENCE_ARTIFACT",
        ),
        _evidence(
            claim_id,
            f"alternative-{claim_id}",
            "ALTERNATIVE_EXPLANATION",
            "REGISTERED_ALTERNATIVE_EXPLANATION_ARTIFACT",
        ),
    ]

    return build_registered_causal_claim_record(
        claim_id=claim_id,
        claim_text=f"{cause_id} may contribute to {effect_id}.",
        cause_ref_id=cause_id,
        effect_ref_id=effect_id,
        claim_type="CONTRIBUTORY_CAUSAL_CLAIM",
        claim_registration_status="REGISTERED",
        premise_records=premises,
        evidence_references=evidence,
        counterevidence_review_status="REGISTERED_PRESENT",
        alternative_explanation_review_status=(
            "REGISTERED_PRESENT"
        ),
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _chain() -> dict:
    return build_deterministic_causal_chain(
        chain_id="chain-001",
        claim_records=[
            _claim("claim-002", "factor-b", "outcome-c"),
            _claim("claim-001", "factor-a", "factor-b"),
        ],
    )


def test_valid_chain_passes_validation() -> None:
    assert validate_deterministic_causal_chain(
        _chain()
    ) == []


def test_claims_are_canonical() -> None:
    chain = _chain()

    assert [
        record["claim_id"]
        for record in chain["claim_records"]
    ] == [
        "claim-001",
        "claim-002",
    ]


def test_edges_are_deterministic() -> None:
    chain = _chain()

    assert [
        edge["claim_id"]
        for edge in chain["edge_records"]
    ] == [
        "claim-001",
        "claim-002",
    ]


def test_chain_nodes_roots_and_terminals() -> None:
    chain = _chain()

    assert chain["node_ids"] == [
        "factor-a",
        "factor-b",
        "outcome-c",
    ]

    assert chain["root_node_ids"] == [
        "factor-a"
    ]

    assert chain["terminal_node_ids"] == [
        "outcome-c"
    ]


def test_complete_chain_is_ready_for_assessment() -> None:
    chain = _chain()

    assert chain["chain_status"] == (
        "READY_FOR_ASSESSMENT"
    )

    assert chain["reason_codes"] == []


def test_review_required_claim_propagates_to_chain() -> None:
    chain = build_deterministic_causal_chain(
        chain_id="chain-review",
        claim_records=[
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                include_premise=False,
            )
        ],
    )

    assert chain["chain_status"] == "REVIEW_REQUIRED"

    assert chain["reason_codes"] == [
        "CLAIM_REVIEW_REQUIRED:claim-001"
    ]


def test_blocked_claim_propagates_to_chain() -> None:
    chain = build_deterministic_causal_chain(
        chain_id="chain-blocked",
        claim_records=[
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                support_status="BLOCKED",
            )
        ],
    )

    assert chain["chain_status"] == "BLOCKED"

    assert chain["reason_codes"] == [
        "CLAIM_BLOCKED:claim-001"
    ]


def test_truth_probability_and_winner_remain_unassigned() -> None:
    chain = _chain()

    assert chain["causal_truth_status"] == (
        "UNDETERMINED"
    )

    assert chain["probability_status"] == (
        "NOT_ASSIGNED"
    )

    assert chain["winner_status"] == "NOT_SELECTED"


def test_edge_preserves_registered_evidence_groups() -> None:
    edge = _chain()["edge_records"][0]

    assert edge["premise_ids"] == [
        "premise-claim-001"
    ]

    assert edge["supporting_evidence_ref_ids"] == [
        "support-claim-001"
    ]

    assert edge["counterevidence_ref_ids"] == [
        "counter-claim-001"
    ]

    assert edge[
        "alternative_explanation_ref_ids"
    ] == [
        "alternative-claim-001"
    ]


def test_edge_validation_passes() -> None:
    edge = _chain()["edge_records"][0]

    assert validate_causal_chain_edge_record(
        edge
    ) == []


def test_empty_claim_list_is_rejected() -> None:
    with pytest.raises(
        CausalChainViolation,
        match="claim_records_empty",
    ):
        build_deterministic_causal_chain(
            chain_id="chain-empty",
            claim_records=[],
        )


def test_duplicate_claim_ids_are_rejected() -> None:
    claim = _claim(
        "claim-001",
        "factor-a",
        "factor-b",
    )

    with pytest.raises(
        CausalChainViolation,
        match="claim_ids_must_be_unique",
    ):
        build_deterministic_causal_chain(
            chain_id="chain-duplicate",
            claim_records=[claim, deepcopy(claim)],
        )


def test_mixed_correlation_ids_are_rejected() -> None:
    first = _claim(
        "claim-001",
        "factor-a",
        "factor-b",
    )

    second = _claim(
        "claim-002",
        "factor-b",
        "outcome-c",
    )

    second["correlation_id"] = "correlation-002"

    for premise in second["premise_records"]:
        premise["correlation_id"] = "correlation-002"

    for evidence in second["evidence_references"]:
        evidence["correlation_id"] = "correlation-002"

    with pytest.raises(
        CausalChainViolation,
        match="correlation_id_mismatch",
    ):
        build_deterministic_causal_chain(
            chain_id="chain-mixed",
            claim_records=[first, second],
        )


def test_validation_detects_edge_mutation() -> None:
    chain = _chain()

    chain["edge_records"][0]["effect_ref_id"] = (
        "changed-effect"
    )

    errors = validate_deterministic_causal_chain(
        chain
    )

    assert (
        "edge_records_do_not_match_claim_records"
        in errors
    )


def test_validation_rejects_causal_truth_assignment() -> None:
    chain = _chain()
    chain["causal_truth_status"] = "CONFIRMED"

    assert "causal_truth_status_invalid" in (
        validate_deterministic_causal_chain(chain)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _chain()
    second = _chain()

    first["claim_records"][0]["claim_text"] = (
        "Changed."
    )

    first["edge_records"][0][
        "supporting_evidence_ref_ids"
    ].append("invented-evidence")

    first["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert second == _chain()
    assert first != second


def test_non_mapping_chain_and_edge_are_rejected() -> None:
    assert validate_deterministic_causal_chain(
        []
    ) == ["causal_chain_must_be_mapping"]

    assert validate_causal_chain_edge_record(
        []
    ) == ["edge_record_must_be_mapping"]
