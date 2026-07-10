"""D3 tests for deterministic narrative linkage rules."""

from dataclasses import replace

import pytest

from fcf.sidecars.market_narrative_context.linkage import (
    NarrativeLinkageDisposition,
    NarrativeLinkageRequest,
    NarrativeLinkageViolation,
    assert_valid_linkage_request,
    evaluate_narrative_linkage,
    validate_linkage_request,
)


def _request() -> NarrativeLinkageRequest:
    return NarrativeLinkageRequest(
        narrative_artifact_id="artifact:narrative:001",
        target_artifact_id="artifact:research:001",
        narrative_correlation_id="correlation:001",
        target_correlation_id="correlation:001",
        narrative_research_run_id="research-run:001",
        target_research_run_id="research-run:001",
        narrative_asset_type="STOCK",
        target_asset_type="stock",
        narrative_symbol="AAPL",
        target_symbol="aapl",
        narrative_evidence_reference_ids=(
            "evidence:macro:001",
            "evidence:company:001",
        ),
        target_evidence_reference_ids=(
            "evidence:company:001",
            "evidence:price:001",
        ),
    )


def test_valid_linkage_request_passes_validation() -> None:
    request = _request()

    assert validate_linkage_request(request) == ()
    assert_valid_linkage_request(request)


def test_matching_metadata_and_evidence_produce_linked_state() -> None:
    result = evaluate_narrative_linkage(_request())

    assert result.disposition is NarrativeLinkageDisposition.LINKED
    assert result.shared_evidence_reference_ids == (
        "evidence:company:001",
    )
    assert result.risk_flags == ()
    assert result.truth_status == "UNDETERMINED"
    assert result.operator_review_required is True


def test_missing_evidence_overlap_requires_review() -> None:
    request = replace(
        _request(),
        target_evidence_reference_ids=("evidence:price:001",),
    )

    result = evaluate_narrative_linkage(request)

    assert (
        result.disposition
        is NarrativeLinkageDisposition.REVIEW_REQUIRED
    )
    assert result.risk_flags == (
        "NO_SHARED_EVIDENCE_REFERENCE",
    )


def test_correlation_mismatch_blocks_linkage() -> None:
    request = replace(
        _request(),
        target_correlation_id="correlation:002",
    )

    result = evaluate_narrative_linkage(request)

    assert result.disposition is NarrativeLinkageDisposition.BLOCKED
    assert "CORRELATION_ID_MISMATCH" in result.risk_flags


def test_research_run_mismatch_blocks_linkage() -> None:
    request = replace(
        _request(),
        target_research_run_id="research-run:002",
    )

    result = evaluate_narrative_linkage(request)

    assert result.disposition is NarrativeLinkageDisposition.BLOCKED
    assert "RESEARCH_RUN_ID_MISMATCH" in result.risk_flags


def test_asset_or_symbol_mismatch_blocks_linkage() -> None:
    request = replace(
        _request(),
        target_asset_type="FUTURES",
        target_symbol="ES",
    )

    result = evaluate_narrative_linkage(request)

    assert result.disposition is NarrativeLinkageDisposition.BLOCKED
    assert result.risk_flags == (
        "ASSET_TYPE_MISMATCH",
        "SYMBOL_MISMATCH",
    )


def test_empty_required_field_is_rejected() -> None:
    request = replace(
        _request(),
        narrative_symbol="",
    )

    assert validate_linkage_request(request) == (
        "EMPTY_FIELD:narrative_symbol",
    )


def test_duplicate_evidence_reference_is_rejected() -> None:
    request = replace(
        _request(),
        narrative_evidence_reference_ids=(
            "evidence:001",
            "evidence:001",
        ),
    )

    with pytest.raises(
        NarrativeLinkageViolation,
        match="DUPLICATE_NARRATIVE_EVIDENCE_REFERENCE",
    ):
        assert_valid_linkage_request(request)


def test_result_preserves_safety_boundary() -> None:
    result = evaluate_narrative_linkage(_request())

    assert result.original_conclusions_preserved is True
    assert result.automatic_truth_decision_allowed is False
    assert result.automatic_conclusion_replacement_allowed is False
    assert result.trade_action_allowed is False


def test_serialization_is_deterministic() -> None:
    first = evaluate_narrative_linkage(_request()).to_dict()
    second = evaluate_narrative_linkage(_request()).to_dict()

    assert first == second
    assert first["disposition"] == "LINKED"
    assert first["truth_status"] == "UNDETERMINED"
    assert first["operator_review_required"] is True
