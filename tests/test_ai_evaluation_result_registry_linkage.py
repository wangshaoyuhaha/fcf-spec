import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_result_registry.linkage_checks import (
    LINKAGE_SCHEMA_VERSION,
    LINKAGE_STAGE_ID,
    build_sample_result_linkage_report,
    validate_sample_result_linkage_report,
)
from fcf.sidecars.ai_evaluation_result_registry.registry_index import (
    build_evaluation_result_registry,
)
from fcf.sidecars.ai_evaluation_result_registry.result_schema import (
    build_evaluation_result_record,
)
from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    build_evaluation_sample_registry,
)
from fcf.sidecars.ai_evaluation_sample_library.sample_schema import (
    build_evaluation_sample_record,
)


def make_sample(
    sample_id: str,
    dimension: str,
) -> dict:
    return build_evaluation_sample_record(
        sample_id=sample_id,
        sample_version="1.0.0",
        title=f"Sample {sample_id}",
        evaluation_dimension=dimension,
        input_payload_ref=f"local://samples/{sample_id}.json",
        expected_outcome="PASS",
        expected_summary="Expected governance result.",
        expected_reason_codes=("REASON_PRESENT",),
        expected_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{sample_id}",),
        registry_entry_ids=(f"registry-{sample_id}",),
        created_at_utc="2026-07-11T01:00:00Z",
        review_status="APPROVED",
    )


def make_sample_registry() -> dict:
    return build_evaluation_sample_registry(
        registry_id="sample-registry-linkage",
        records=(
            make_sample(
                "sample-001",
                "risk_preservation",
            ),
            make_sample(
                "sample-002",
                "evidence_grounding",
            ),
        ),
        created_at_utc="2026-07-11T02:00:00Z",
    )


def make_result(
    result_id: str,
    sample_id: str,
    dimension: str,
    checksum_character: str,
    *,
    result_status: str = "ARCHIVED",
) -> dict:
    return build_evaluation_result_record(
        result_id=result_id,
        result_version="1.0.0",
        sample_id=sample_id,
        sample_version="1.0.0",
        evaluation_dimension=dimension,
        imported_output_ref=(
            f"local://evaluation-results/{result_id}.json"
        ),
        imported_output_sha256=checksum_character * 64,
        observed_outcome="PASS",
        result_summary="Imported evaluation result.",
        observed_reason_codes=("REASON_PRESENT",),
        observed_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{result_id}",),
        prompt_model_registry_entry_ids=(
            f"prompt-model-{result_id}",
        ),
        context_evidence_entry_ids=(
            f"context-evidence-{result_id}",
        ),
        imported_at_utc="2026-07-11T03:00:00Z",
        result_status=result_status,
    )


def make_result_registry(
    *,
    second_sample_id: str = "sample-002",
    second_dimension: str = "evidence_grounding",
    second_checksum: str = "b",
    second_status: str = "ARCHIVED",
) -> dict:
    return build_evaluation_result_registry(
        registry_id="result-registry-linkage",
        records=(
            make_result(
                "result-001",
                "sample-001",
                "risk_preservation",
                "a",
            ),
            make_result(
                "result-002",
                second_sample_id,
                second_dimension,
                second_checksum,
                result_status=second_status,
            ),
        ),
        created_at_utc="2026-07-11T04:00:00Z",
    )


def make_report() -> dict:
    return build_sample_result_linkage_report(
        report_id="linkage-report-001",
        sample_registry=make_sample_registry(),
        result_registry=make_result_registry(),
        created_at_utc="2026-07-11T05:00:00Z",
    )


def test_linkage_report_identity() -> None:
    report = make_report()

    assert report["stage_id"] == LINKAGE_STAGE_ID
    assert report["schema_version"] == LINKAGE_SCHEMA_VERSION
    assert report["report_id"] == "linkage-report-001"


def test_complete_valid_linkage_passes() -> None:
    report = make_report()

    assert report["linkage_status"] == "PASS"
    assert report["sample_count"] == 2
    assert report["result_count"] == 2
    assert report["linked_result_count"] == 2


def test_unknown_sample_reference_fails() -> None:
    report = build_sample_result_linkage_report(
        report_id="unknown-sample-report",
        sample_registry=make_sample_registry(),
        result_registry=make_result_registry(
            second_sample_id="sample-999",
        ),
        created_at_utc="2026-07-11T05:00:00Z",
    )

    assert report["linkage_status"] == "FAIL"
    assert report["unknown_sample_keys"] == [
        "sample-999@1.0.0"
    ]


def test_dimension_mismatch_fails() -> None:
    report = build_sample_result_linkage_report(
        report_id="dimension-mismatch-report",
        sample_registry=make_sample_registry(),
        result_registry=make_result_registry(
            second_dimension="risk_preservation",
        ),
        created_at_utc="2026-07-11T05:00:00Z",
    )

    assert report["linkage_status"] == "FAIL"
    assert report["dimension_mismatch_result_keys"] == [
        "result-002@1.0.0"
    ]


def test_sample_without_result_requires_review() -> None:
    result_registry = build_evaluation_result_registry(
        registry_id="single-result-registry",
        records=(
            make_result(
                "result-001",
                "sample-001",
                "risk_preservation",
                "a",
            ),
        ),
        created_at_utc="2026-07-11T04:00:00Z",
    )

    report = build_sample_result_linkage_report(
        report_id="missing-result-report",
        sample_registry=make_sample_registry(),
        result_registry=result_registry,
        created_at_utc="2026-07-11T05:00:00Z",
    )

    assert report["linkage_status"] == "REVIEW_REQUIRED"
    assert report["samples_without_results"] == [
        "sample-002@1.0.0"
    ]


def test_duplicate_output_checksum_requires_review() -> None:
    report = build_sample_result_linkage_report(
        report_id="duplicate-output-report",
        sample_registry=make_sample_registry(),
        result_registry=make_result_registry(
            second_checksum="a",
        ),
        created_at_utc="2026-07-11T05:00:00Z",
    )

    assert report["linkage_status"] == "REVIEW_REQUIRED"
    assert report["duplicate_output_sha256"] == [
        "a" * 64
    ]


def test_pending_result_requires_review() -> None:
    report = build_sample_result_linkage_report(
        report_id="pending-result-report",
        sample_registry=make_sample_registry(),
        result_registry=make_result_registry(
            second_status="REVIEW_REQUIRED",
        ),
        created_at_utc="2026-07-11T05:00:00Z",
    )

    assert report["linkage_status"] == "REVIEW_REQUIRED"


def test_invalid_source_registry_fails() -> None:
    result_registry = make_result_registry()
    result_registry["result_count"] = 999

    report = build_sample_result_linkage_report(
        report_id="invalid-source-report",
        sample_registry=make_sample_registry(),
        result_registry=result_registry,
        created_at_utc="2026-07-11T05:00:00Z",
    )

    assert report["linkage_status"] == "FAIL"
    assert (
        "result_registry:result_count_mismatch"
        in report["source_validation_errors"]
    )


def test_linkage_report_blocks_automatic_capabilities() -> None:
    report = make_report()

    assert report["operator_review_required"] is True
    assert report["imported_artifacts_only"] is True
    assert report["operator_review_bypass_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False


def test_linkage_report_validation_passes() -> None:
    assert validate_sample_result_linkage_report(
        make_report()
    ) == []


def test_validation_detects_status_mismatch() -> None:
    report = make_report()
    report["linkage_status"] = "FAIL"

    errors = validate_sample_result_linkage_report(report)

    assert "linkage_status_mismatch" in errors


def test_validation_detects_count_mismatches() -> None:
    report = make_report()
    report["sample_count"] = 999
    report["linked_result_count"] = 999

    errors = validate_sample_result_linkage_report(report)

    assert "sample_count_mismatch" in errors
    assert "linked_result_count_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    report = make_report()
    report["operator_review_bypass_allowed"] = True
    report["model_invocation_allowed"] = True

    errors = validate_sample_result_linkage_report(report)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_builder_returns_fresh_lists() -> None:
    first = make_report()
    second = make_report()
    changed = deepcopy(first)

    changed["linked_result_keys"].append(
        "unexpected-result"
    )
    changed["known_sample_keys"].clear()

    assert (
        "unexpected-result"
        not in second["linked_result_keys"]
    )
    assert second["known_sample_keys"]


def test_validation_rejects_non_mapping() -> None:
    assert validate_sample_result_linkage_report([]) == [
        "report_not_mapping"
    ]