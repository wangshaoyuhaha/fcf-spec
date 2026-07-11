"""Tests for causal reasoning D2 registered evidence schemas."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_causal_reasoning_chain import (
    CausalSchemaViolation,
    build_registered_causal_claim_record,
    build_registered_causal_evidence_reference,
    build_registered_causal_premise_record,
    validate_registered_causal_claim_record,
    validate_registered_causal_evidence_reference,
    validate_registered_causal_premise_record,
)


def _premise(
    premise_id: str = "premise-001",
    status: str = "REGISTERED",
) -> dict:
    return build_registered_causal_premise_record(
        premise_id=premise_id,
        claim_id="claim-001",
        premise_text="Registered premise text.",
        registration_status=status,
        source_artifact_ids=["source-artifact-001"],
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _evidence(
    evidence_ref_id: str,
    role: str,
    artifact_type: str,
    status: str = "REGISTERED",
) -> dict:
    return build_registered_causal_evidence_reference(
        evidence_ref_id=evidence_ref_id,
        claim_id="claim-001",
        artifact_id=f"artifact-{evidence_ref_id}",
        artifact_type=artifact_type,
        evidence_role=role,
        registration_status=status,
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _supporting() -> dict:
    return _evidence(
        "evidence-support-001",
        "SUPPORTING",
        "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
    )


def _counterevidence() -> dict:
    return _evidence(
        "evidence-counter-001",
        "COUNTEREVIDENCE",
        "REGISTERED_COUNTEREVIDENCE_ARTIFACT",
    )


def _alternative() -> dict:
    return _evidence(
        "evidence-alternative-001",
        "ALTERNATIVE_EXPLANATION",
        "REGISTERED_ALTERNATIVE_EXPLANATION_ARTIFACT",
    )


def _claim(
    premises: list[dict] | None = None,
    evidence: list[dict] | None = None,
    claim_status: str = "REGISTERED",
    counter_status: str = "REGISTERED_PRESENT",
    alternative_status: str = "REGISTERED_PRESENT",
) -> dict:
    return build_registered_causal_claim_record(
        claim_id="claim-001",
        claim_text="Registered cause may contribute to effect.",
        cause_ref_id="cause-001",
        effect_ref_id="effect-001",
        claim_type="CONTRIBUTORY_CAUSAL_CLAIM",
        claim_registration_status=claim_status,
        premise_records=(
            premises
            if premises is not None
            else [_premise()]
        ),
        evidence_references=(
            evidence
            if evidence is not None
            else [
                _supporting(),
                _counterevidence(),
                _alternative(),
            ]
        ),
        counterevidence_review_status=counter_status,
        alternative_explanation_review_status=(
            alternative_status
        ),
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def test_premise_validation_passes() -> None:
    assert validate_registered_causal_premise_record(
        _premise()
    ) == []


def test_evidence_reference_validation_passes() -> None:
    assert (
        validate_registered_causal_evidence_reference(
            _supporting()
        )
        == []
    )


def test_complete_claim_validation_passes() -> None:
    assert validate_registered_causal_claim_record(
        _claim()
    ) == []


def test_complete_claim_is_recorded() -> None:
    claim = _claim()

    assert claim["record_status"] == "RECORDED"
    assert claim["reason_codes"] == []


def test_truth_probability_and_winner_remain_unassigned() -> None:
    claim = _claim()

    assert claim["causal_truth_status"] == "UNDETERMINED"
    assert claim["probability_status"] == "NOT_ASSIGNED"
    assert claim["winner_status"] == "NOT_SELECTED"


def test_missing_support_requires_review() -> None:
    claim = _claim(
        evidence=[
            _counterevidence(),
            _alternative(),
        ]
    )

    assert claim["record_status"] == "REVIEW_REQUIRED"
    assert "MISSING_SUPPORTING_EVIDENCE" in (
        claim["reason_codes"]
    )


def test_missing_premise_requires_review() -> None:
    claim = _claim(premises=[])

    assert claim["record_status"] == "REVIEW_REQUIRED"
    assert "MISSING_REGISTERED_PREMISES" in (
        claim["reason_codes"]
    )


def test_not_reviewed_counterevidence_requires_review() -> None:
    claim = _claim(
        evidence=[
            _supporting(),
            _alternative(),
        ],
        counter_status="NOT_REVIEWED",
    )

    assert claim["record_status"] == "REVIEW_REQUIRED"
    assert "COUNTEREVIDENCE_NOT_REVIEWED" in (
        claim["reason_codes"]
    )


def test_blocked_evidence_blocks_claim_record() -> None:
    blocked_support = _evidence(
        "evidence-support-001",
        "SUPPORTING",
        "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
        status="BLOCKED",
    )

    claim = _claim(
        evidence=[
            blocked_support,
            _counterevidence(),
            _alternative(),
        ]
    )

    assert claim["record_status"] == "BLOCKED"
    assert "EVIDENCE_REGISTRATION_BLOCKED" in (
        claim["reason_codes"]
    )


def test_builder_rejects_invalid_nested_premise() -> None:
    premise = _premise()
    premise["source_artifact_ids"] = []

    with pytest.raises(
        CausalSchemaViolation,
        match="source_artifact_ids_empty",
    ):
        _claim(premises=[premise])


def test_validation_detects_counterevidence_status_mismatch() -> None:
    claim = _claim()
    claim["counterevidence_review_status"] = (
        "REVIEWED_NONE_REGISTERED"
    )

    assert (
        "counterevidence_none_status_conflicts_with_reference"
        in validate_registered_causal_claim_record(claim)
    )


def test_validation_detects_nested_correlation_mismatch() -> None:
    claim = _claim()
    claim["premise_records"][0]["correlation_id"] = (
        "different-correlation"
    )

    errors = validate_registered_causal_claim_record(
        claim
    )

    assert any(
        "correlation_id_mismatch" in error
        for error in errors
    )


def test_validation_detects_duplicate_evidence_ids() -> None:
    claim = _claim()
    duplicate = deepcopy(claim["evidence_references"][0])
    claim["evidence_references"].append(duplicate)

    errors = validate_registered_causal_claim_record(
        claim
    )

    assert "evidence_ref_ids_must_be_unique" in errors


def test_validation_rejects_causal_truth_assignment() -> None:
    claim = _claim()
    claim["causal_truth_status"] = "CONFIRMED"

    assert "causal_truth_status_invalid" in (
        validate_registered_causal_claim_record(claim)
    )


def test_source_artifacts_and_conclusions_are_preserved() -> None:
    claim = _claim()

    assert claim["source_artifacts_preserved"] is True
    assert claim["original_conclusions_preserved"] is True


def test_builder_returns_fresh_nested_containers() -> None:
    first = _claim()
    second = _claim()

    first["premise_records"][0]["premise_text"] = "Changed."
    first["evidence_references"][0]["artifact_id"] = (
        "changed-artifact"
    )
    first["safety_flags"]["real_execution_allowed"] = True

    assert second == _claim()
    assert first != second


def test_non_mapping_records_are_rejected() -> None:
    assert validate_registered_causal_premise_record(
        []
    ) == ["premise_record_must_be_mapping"]

    assert validate_registered_causal_evidence_reference(
        []
    ) == ["evidence_reference_must_be_mapping"]

    assert validate_registered_causal_claim_record(
        []
    ) == ["claim_record_must_be_mapping"]
