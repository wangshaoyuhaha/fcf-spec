import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_drift_review import (
    APP_ID,
    WINDOW_VERSION,
    build_drift_comparison_window,
    build_drift_evidence_record,
)


def make_record(
    *,
    evidence_id: str,
    sample_id: str = "sample-001",
    baseline_time: str = "2026-07-01T00:00:00+00:00",
    candidate_time: str = "2026-07-10T00:00:00+00:00",
    baseline_status: str = "MATCHED",
    candidate_status: str = "MATCHED",
    baseline_model_version: str = "1.0.0",
    candidate_model_version: str = "1.0.0",
    baseline_prompt_version: str = "2.0.0",
    candidate_prompt_version: str = "2.0.0",
) -> dict:
    return build_drift_evidence_record(
        drift_evidence_id=evidence_id,
        evaluation_sample_id=sample_id,
        baseline_reference=f"baseline/{evidence_id}.json",
        candidate_reference=f"candidate/{evidence_id}.json",
        baseline_created_at_utc=baseline_time,
        candidate_created_at_utc=candidate_time,
        model_id="model-alpha",
        baseline_model_version=baseline_model_version,
        candidate_model_version=candidate_model_version,
        prompt_id="prompt-alpha",
        baseline_prompt_version=baseline_prompt_version,
        candidate_prompt_version=candidate_prompt_version,
        baseline_comparison_status=baseline_status,
        candidate_comparison_status=candidate_status,
        drift_status="REVIEW_REQUIRED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T00:00:00+00:00",
    )


def test_window_builds_valid_no_drift_window() -> None:
    report = build_drift_comparison_window(
        [make_record(evidence_id="evidence-001")]
    )

    assert report["app_id"] == APP_ID
    assert report["window_version"] == WINDOW_VERSION
    assert report["window_status"] == "NO_DRIFT"
    assert report["record_count"] == 1
    assert report["sample_count"] == 1
    assert report["errors"] == []


def test_window_orders_items_chronologically() -> None:
    records = [
        make_record(
            evidence_id="evidence-002",
            candidate_time="2026-07-10T00:00:00+00:00",
        ),
        make_record(
            evidence_id="evidence-001",
            candidate_time="2026-07-05T00:00:00+00:00",
        ),
    ]

    report = build_drift_comparison_window(records)

    assert [
        item["drift_evidence_id"]
        for item in report["items"]
    ] == ["evidence-001", "evidence-002"]


def test_window_calculates_time_bounds() -> None:
    records = [
        make_record(
            evidence_id="evidence-001",
            baseline_time="2026-07-01T00:00:00+00:00",
            candidate_time="2026-07-05T00:00:00+00:00",
        ),
        make_record(
            evidence_id="evidence-002",
            baseline_time="2026-07-03T00:00:00+00:00",
            candidate_time="2026-07-10T00:00:00+00:00",
        ),
    ]

    report = build_drift_comparison_window(records)

    assert report["window_start_utc"] == (
        "2026-07-01T00:00:00+00:00"
    )
    assert report["window_end_utc"] == (
        "2026-07-10T00:00:00+00:00"
    )
    assert report["window_span_seconds"] == 777600


def test_potential_drift_requires_review() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_model_version="1.1.0",
            )
        ]
    )

    assert report["window_status"] == "REVIEW_REQUIRED"
    assert report["review_required_count"] == 1
    assert report["drift_status_counts"] == {
        "POTENTIAL_DRIFT": 1
    }


def test_confirmed_drift_requires_review() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_status="MISMATCH",
            )
        ]
    )

    assert report["window_status"] == "REVIEW_REQUIRED"
    assert report["drift_status_counts"] == {
        "CONFIRMED_DRIFT": 1
    }
    assert report["drift_severity_counts"] == {
        "HIGH": 1
    }


def test_window_counts_multiple_drift_states() -> None:
    records = [
        make_record(evidence_id="evidence-001"),
        make_record(
            evidence_id="evidence-002",
            candidate_model_version="1.1.0",
        ),
        make_record(
            evidence_id="evidence-003",
            candidate_status="MISMATCH",
        ),
    ]

    report = build_drift_comparison_window(records)

    assert report["drift_status_counts"] == {
        "CONFIRMED_DRIFT": 1,
        "NO_DRIFT": 1,
        "POTENTIAL_DRIFT": 1,
    }


def test_window_counts_reason_codes() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_model_version="1.1.0",
            )
        ]
    )

    assert report["reason_code_counts"] == {
        "MODEL_VERSION_CHANGED": 1
    }


def test_window_counts_changed_dimensions() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_model_version="1.1.0",
                candidate_prompt_version="2.1.0",
            )
        ]
    )

    assert report["changed_dimension_counts"] == {
        "model_version": 1,
        "prompt_version": 1,
    }


def test_window_detects_cross_model_version() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_model_version="2.0.0",
            )
        ]
    )

    assert report[
        "cross_model_version_available"
    ] is True


def test_window_detects_cross_prompt_version() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_prompt_version="3.0.0",
            )
        ]
    )

    assert report[
        "cross_prompt_version_available"
    ] is True


def test_window_groups_samples_deterministically() -> None:
    records = [
        make_record(
            evidence_id="evidence-002",
            sample_id="sample-002",
        ),
        make_record(
            evidence_id="evidence-001",
            sample_id="sample-001",
        ),
    ]

    report = build_drift_comparison_window(records)

    assert [
        item["evaluation_sample_id"]
        for item in report["sample_windows"]
    ] == ["sample-001", "sample-002"]


def test_sample_window_marks_review_required() -> None:
    report = build_drift_comparison_window(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_status="PARTIAL_MATCH",
            )
        ]
    )

    assert report["sample_windows"][0][
        "review_required"
    ] is True


def test_window_rejects_duplicate_evidence_ids() -> None:
    record = make_record(evidence_id="evidence-001")

    report = build_drift_comparison_window(
        [record, deepcopy(record)]
    )

    assert report["window_status"] == "INVALID"
    assert (
        "duplicate_drift_evidence_id:evidence-001"
        in report["errors"]
    )


def test_window_rejects_invalid_record() -> None:
    record = make_record(evidence_id="evidence-001")
    record["model_id"] = ""

    report = build_drift_comparison_window([record])

    assert report["window_status"] == "INVALID"
    assert "record[0]:model_id_invalid" in report["errors"]


def test_window_rejects_non_mapping_record() -> None:
    report = build_drift_comparison_window([[]])

    assert report["window_status"] == "INVALID"
    assert report["errors"] == ["record_not_mapping:0"]


def test_window_blocks_empty_collection() -> None:
    report = build_drift_comparison_window([])

    assert report["window_status"] == "BLOCKED"
    assert report["result_status"] == "BLOCKED"
    assert report["errors"] == [
        "no_drift_evidence_records"
    ]


def test_window_rejects_invalid_collection_type() -> None:
    report = build_drift_comparison_window(
        "not-a-record-list"
    )

    assert report["window_status"] == "INVALID"
    assert report["errors"] == ["records_invalid"]


def test_window_does_not_mutate_records() -> None:
    records = [
        make_record(evidence_id="evidence-001"),
        make_record(
            evidence_id="evidence-002",
            candidate_model_version="1.1.0",
        ),
    ]
    before = deepcopy(records)

    build_drift_comparison_window(records)

    assert records == before


def test_window_is_deterministic() -> None:
    records = [
        make_record(
            evidence_id="evidence-002",
            sample_id="sample-002",
        ),
        make_record(
            evidence_id="evidence-001",
            sample_id="sample-001",
        ),
    ]

    first = build_drift_comparison_window(records)
    second = build_drift_comparison_window(records)

    assert first == second


def test_window_preserves_safety_boundary() -> None:
    report = build_drift_comparison_window(
        [make_record(evidence_id="evidence-001")]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["read_only"] is True
    assert report["sidecar_only"] is True
    assert report["operator_review_required"] is True
    assert report["deterministic_only"] is True
    assert report["registered_artifacts_only"] is True
    assert report["core_mutation_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["orchestrator_execution_allowed"] is False
    assert report["automatic_approval_allowed"] is False
    assert report["automatic_rejection_allowed"] is False
    assert report["automatic_rollback_allowed"] is False
    assert report["automatic_model_switch_allowed"] is False
    assert report["automatic_prompt_switch_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False