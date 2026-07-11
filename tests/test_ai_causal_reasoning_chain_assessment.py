"""Tests for deterministic causal-chain governance assessment."""

from copy import deepcopy

from fcf.sidecars.ai_causal_reasoning_chain import (
    build_causal_reasoning_assessment,
    build_deterministic_causal_chain,
    build_registered_causal_claim_record,
    build_registered_causal_evidence_reference,
    build_registered_causal_premise_record,
    validate_causal_reasoning_assessment,
)


def _premise(
    claim_id: str,
    *,
    include: bool = True,
) -> list[dict]:
    if not include:
        return []

    return [
        build_registered_causal_premise_record(
            premise_id=f"premise-{claim_id}",
            claim_id=claim_id,
            premise_text="Registered causal premise.",
            registration_status="REGISTERED",
            source_artifact_ids=[
                f"source-{claim_id}"
            ],
            correlation_id="correlation-001",
            research_run_id="research-run-001",
        )
    ]


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
    premise_present: bool = True,
    support_present: bool = True,
    support_status: str = "REGISTERED",
    counter_status: str = "REGISTERED_PRESENT",
    alternative_status: str = "REGISTERED_PRESENT",
) -> dict:
    evidence: list[dict] = []

    if support_present:
        evidence.append(
            _evidence(
                claim_id,
                f"support-{claim_id}",
                "SUPPORTING",
                "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
                support_status,
            )
        )

    if counter_status == "REGISTERED_PRESENT":
        evidence.append(
            _evidence(
                claim_id,
                f"counter-{claim_id}",
                "COUNTEREVIDENCE",
                "REGISTERED_COUNTEREVIDENCE_ARTIFACT",
            )
        )

    if alternative_status == "REGISTERED_PRESENT":
        evidence.append(
            _evidence(
                claim_id,
                f"alternative-{claim_id}",
                "ALTERNATIVE_EXPLANATION",
                "REGISTERED_ALTERNATIVE_EXPLANATION_ARTIFACT",
            )
        )

    return build_registered_causal_claim_record(
        claim_id=claim_id,
        claim_text=f"{cause_id} may contribute to {effect_id}.",
        cause_ref_id=cause_id,
        effect_ref_id=effect_id,
        claim_type="CONTRIBUTORY_CAUSAL_CLAIM",
        claim_registration_status="REGISTERED",
        premise_records=_premise(
            claim_id,
            include=premise_present,
        ),
        evidence_references=evidence,
        counterevidence_review_status=counter_status,
        alternative_explanation_review_status=(
            alternative_status
        ),
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _chain(
    claims: list[dict] | None = None,
) -> dict:
    return build_deterministic_causal_chain(
        chain_id="chain-001",
        claim_records=(
            claims
            if claims is not None
            else [
                _claim(
                    "claim-001",
                    "factor-a",
                    "factor-b",
                ),
                _claim(
                    "claim-002",
                    "factor-b",
                    "outcome-c",
                ),
            ]
        ),
    )


def _assessment(
    claims: list[dict] | None = None,
) -> dict:
    return build_causal_reasoning_assessment(
        assessment_id="assessment-001",
        source_chain=_chain(claims),
    )


def _finding_types(
    assessment: dict,
) -> set[str]:
    return {
        finding["finding_type"]
        for finding in assessment["finding_records"]
    }


def test_valid_assessment_passes_validation() -> None:
    assert validate_causal_reasoning_assessment(
        _assessment()
    ) == []


def test_connected_chain_is_ready_for_review_packet() -> None:
    assessment = _assessment()

    assert assessment["component_count"] == 1
    assert assessment["cycle_paths"] == []
    assert assessment["assessment_status"] == (
        "READY_FOR_REVIEW_PACKET"
    )


def test_registered_counterevidence_is_surfaced() -> None:
    assessment = _assessment()

    assert "REGISTERED_COUNTEREVIDENCE_SIGNAL" in (
        _finding_types(assessment)
    )


def test_registered_alternative_is_surfaced() -> None:
    assessment = _assessment()

    assert (
        "REGISTERED_ALTERNATIVE_EXPLANATION_SIGNAL"
        in _finding_types(assessment)
    )


def test_disconnected_components_require_review() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
            ),
            _claim(
                "claim-002",
                "factor-x",
                "outcome-y",
            ),
        ]
    )

    assert assessment["component_count"] == 2
    assert assessment["assessment_status"] == (
        "REVIEW_REQUIRED"
    )
    assert "DISCONNECTED_COMPONENTS" in (
        _finding_types(assessment)
    )


def test_cycle_blocks_assessment() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
            ),
            _claim(
                "claim-002",
                "factor-b",
                "factor-a",
            ),
        ]
    )

    assert assessment["cycle_paths"]
    assert assessment["assessment_status"] == "BLOCKED"
    assert "CYCLE_DETECTED" in (
        _finding_types(assessment)
    )


def test_duplicate_directional_edge_requires_review() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
            ),
            _claim(
                "claim-002",
                "factor-a",
                "factor-b",
            ),
        ]
    )

    assert assessment[
        "duplicate_directional_edge_groups"
    ]
    assert "DUPLICATE_DIRECTIONAL_EDGE" in (
        _finding_types(assessment)
    )
    assert assessment["assessment_status"] == (
        "REVIEW_REQUIRED"
    )


def test_reverse_edge_pair_is_detected() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
            ),
            _claim(
                "claim-002",
                "factor-b",
                "factor-a",
            ),
        ]
    )

    assert assessment["reverse_edge_pairs"]
    assert "CONFLICTING_REVERSE_EDGE" in (
        _finding_types(assessment)
    )


def test_missing_premise_requires_review() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                premise_present=False,
            )
        ]
    )

    assert "MISSING_REGISTERED_PREMISE" in (
        _finding_types(assessment)
    )
    assert assessment["assessment_status"] == (
        "REVIEW_REQUIRED"
    )


def test_missing_support_requires_review() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                support_present=False,
            )
        ]
    )

    assert "MISSING_SUPPORTING_EVIDENCE" in (
        _finding_types(assessment)
    )


def test_counterevidence_not_reviewed_requires_review() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                counter_status="NOT_REVIEWED",
            )
        ]
    )

    assert "COUNTEREVIDENCE_NOT_REVIEWED" in (
        _finding_types(assessment)
    )


def test_alternative_not_reviewed_requires_review() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                alternative_status="NOT_REVIEWED",
            )
        ]
    )

    assert (
        "ALTERNATIVE_EXPLANATION_NOT_REVIEWED"
        in _finding_types(assessment)
    )


def test_blocked_source_claim_blocks_assessment() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                support_status="BLOCKED",
            )
        ]
    )

    assert "BLOCKED_SOURCE_CLAIM" in (
        _finding_types(assessment)
    )
    assert assessment["assessment_status"] == "BLOCKED"


def test_truth_probability_and_winner_remain_unassigned() -> None:
    assessment = _assessment()

    assert assessment["causal_truth_status"] == (
        "UNDETERMINED"
    )
    assert assessment["probability_status"] == (
        "NOT_ASSIGNED"
    )
    assert assessment["winner_status"] == (
        "NOT_SELECTED"
    )


def test_validation_detects_finding_mutation() -> None:
    assessment = _assessment()
    assessment["finding_records"][0][
        "detail_code"
    ] = "MUTATED"

    errors = validate_causal_reasoning_assessment(
        assessment
    )

    assert "finding_records_mismatch" in errors


def test_validation_rejects_causal_truth_assignment() -> None:
    assessment = _assessment()
    assessment["causal_truth_status"] = "CONFIRMED"

    assert "causal_truth_status_invalid" in (
        validate_causal_reasoning_assessment(
            assessment
        )
    )


def test_builder_returns_fresh_containers() -> None:
    first = _assessment()
    second = _assessment()

    first["source_chain"]["node_ids"].append(
        "invented-node"
    )
    first["finding_records"][0]["severity"] = (
        "CRITICAL"
    )
    first["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert second == _assessment()
    assert first != second


def test_non_mapping_assessment_is_rejected() -> None:
    assert validate_causal_reasoning_assessment(
        []
    ) == ["assessment_must_be_mapping"]
