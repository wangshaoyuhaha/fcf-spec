import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_comparison import (
    APP_ID,
    COMPARISON_AXES,
    MATRIX_VERSION,
    build_comparison_record,
    build_registered_comparison_matrix,
)


def make_record(
    *,
    comparison_id: str,
    sample_id: str = "sample-001",
    model_id: str = "model-alpha",
    model_version: str = "1.0.0",
    prompt_id: str = "prompt-alpha",
    prompt_version: str = "1.0.0",
    comparison_status: str = "MATCHED",
) -> dict:
    return build_comparison_record(
        comparison_id=comparison_id,
        comparison_mode="expected_vs_observed",
        evaluation_sample_id=sample_id,
        expected_result_reference=f"expected/{sample_id}.json",
        observed_result_reference=f"observed/{comparison_id}.json",
        model_id=model_id,
        model_version=model_version,
        prompt_id=prompt_id,
        prompt_version=prompt_version,
        context_evidence_reference=f"context/{comparison_id}.json",
        result_status="RECORDED",
        comparison_status=comparison_status,
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T02:40:00+00:00",
    )


def test_matrix_builds_valid_single_sample_group() -> None:
    report = build_registered_comparison_matrix(
        [make_record(comparison_id="comparison-001")]
    )

    assert report["app_id"] == APP_ID
    assert report["matrix_version"] == MATRIX_VERSION
    assert report["comparison_axes"] == list(COMPARISON_AXES)
    assert report["matrix_status"] == "REVIEW_REQUIRED"
    assert report["record_count"] == 1
    assert report["sample_count"] == 1
    assert report["errors"] == []


def test_matrix_detects_cross_model_comparison() -> None:
    records = [
        make_record(
            comparison_id="comparison-001",
            model_id="model-alpha",
        ),
        make_record(
            comparison_id="comparison-002",
            model_id="model-beta",
        ),
    ]

    report = build_registered_comparison_matrix(records)
    group = report["sample_groups"][0]

    assert group["cross_model_available"] is True
    assert group["model_ids"] == [
        "model-alpha",
        "model-beta",
    ]


def test_matrix_detects_cross_model_version() -> None:
    records = [
        make_record(
            comparison_id="comparison-001",
            model_version="1.0.0",
        ),
        make_record(
            comparison_id="comparison-002",
            model_version="2.0.0",
        ),
    ]

    group = build_registered_comparison_matrix(
        records
    )["sample_groups"][0]

    assert group["cross_model_version_available"] is True


def test_matrix_detects_cross_prompt_version() -> None:
    records = [
        make_record(
            comparison_id="comparison-001",
            prompt_version="1.0.0",
        ),
        make_record(
            comparison_id="comparison-002",
            prompt_version="2.0.0",
        ),
    ]

    group = build_registered_comparison_matrix(
        records
    )["sample_groups"][0]

    assert group["cross_prompt_version_available"] is True


def test_matrix_does_not_confuse_different_model_ids() -> None:
    records = [
        make_record(
            comparison_id="comparison-001",
            model_id="model-alpha",
            model_version="1.0.0",
        ),
        make_record(
            comparison_id="comparison-002",
            model_id="model-beta",
            model_version="2.0.0",
        ),
    ]

    group = build_registered_comparison_matrix(
        records
    )["sample_groups"][0]

    assert group["cross_model_available"] is True
    assert group["cross_model_version_available"] is False


def test_matrix_groups_multiple_samples() -> None:
    records = [
        make_record(
            comparison_id="comparison-002",
            sample_id="sample-002",
        ),
        make_record(
            comparison_id="comparison-001",
            sample_id="sample-001",
        ),
    ]

    report = build_registered_comparison_matrix(records)

    assert report["sample_count"] == 2
    assert [
        group["evaluation_sample_id"]
        for group in report["sample_groups"]
    ] == ["sample-001", "sample-002"]


def test_matrix_counts_comparison_statuses() -> None:
    records = [
        make_record(
            comparison_id="comparison-001",
            comparison_status="MATCHED",
        ),
        make_record(
            comparison_id="comparison-002",
            comparison_status="MISMATCH",
        ),
    ]

    group = build_registered_comparison_matrix(
        records
    )["sample_groups"][0]

    assert group["comparison_status_counts"] == {
        "MATCHED": 1,
        "MISMATCH": 1,
    }


def test_matrix_rejects_duplicate_comparison_ids() -> None:
    record = make_record(comparison_id="comparison-001")

    report = build_registered_comparison_matrix(
        [record, deepcopy(record)]
    )

    assert report["matrix_status"] == "INVALID"
    assert (
        "duplicate_comparison_id:comparison-001"
        in report["errors"]
    )


def test_matrix_rejects_invalid_record() -> None:
    record = make_record(comparison_id="comparison-001")
    record["model_id"] = ""

    report = build_registered_comparison_matrix([record])

    assert report["matrix_status"] == "INVALID"
    assert "record[0]:model_id_invalid" in report["errors"]


def test_matrix_rejects_non_mapping_record() -> None:
    report = build_registered_comparison_matrix([[]])

    assert report["matrix_status"] == "INVALID"
    assert "record_not_mapping:0" in report["errors"]


def test_matrix_blocks_empty_record_collection() -> None:
    report = build_registered_comparison_matrix([])

    assert report["matrix_status"] == "BLOCKED"
    assert report["result_status"] == "BLOCKED"
    assert report["errors"] == ["no_comparison_records"]


def test_matrix_rejects_invalid_collection_type() -> None:
    report = build_registered_comparison_matrix(
        "not-a-record-list"
    )

    assert report["matrix_status"] == "INVALID"
    assert report["errors"] == ["records_invalid"]


def test_matrix_is_deterministic() -> None:
    records = [
        make_record(
            comparison_id="comparison-002",
            model_id="model-beta",
        ),
        make_record(
            comparison_id="comparison-001",
            model_id="model-alpha",
        ),
    ]

    first = build_registered_comparison_matrix(records)
    second = build_registered_comparison_matrix(records)

    assert first == second
    assert first["sample_groups"][0]["comparison_ids"] == [
        "comparison-001",
        "comparison-002",
    ]


def test_matrix_does_not_mutate_source_records() -> None:
    records = [
        make_record(comparison_id="comparison-001"),
        make_record(comparison_id="comparison-002"),
    ]
    before = deepcopy(records)

    build_registered_comparison_matrix(records)

    assert records == before


def test_matrix_preserves_safety_boundary() -> None:
    report = build_registered_comparison_matrix(
        [make_record(comparison_id="comparison-001")]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["read_only"] is True
    assert report["sidecar_only"] is True
    assert report["operator_review_required"] is True
    assert report["automatic_acceptance_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False
    assert report["core_mutation_allowed"] is False