import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.validation_baseline_registry import (
    build_validation_baseline_snapshot_index,
    build_validation_baseline_summary,
    build_validation_run_index,
    build_validation_run_record,
    classify_validation_baseline_summary,
)


def _record(result="PASS", pass_count=2062, baseline_status="REGISTERED"):
    return build_validation_run_record(
        validation_id="validation-1",
        command="python -m pytest -q",
        result=result,
        pass_count=pass_count,
        git_branch="main",
        git_head="48970eb",
        git_status="clean",
        origin_status="synced",
        output_summary="2062 passed",
        baseline_status=baseline_status,
    )


def test_summary_verified_requires_operator_review():
    snapshot_index = build_validation_baseline_snapshot_index([_record()])
    run_index = build_validation_run_index([_record()])

    summary = build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )
    result = classify_validation_baseline_summary(summary)

    assert summary["stage"] == "D4"
    assert summary["summary_status"] == "VERIFIED"
    assert summary["summary_action"] == "QUEUE_OPERATOR_REVIEW"
    assert summary["verified_count"] == 2
    assert summary["read_only"] is True
    assert summary["index_only"] is True
    assert summary["summary_only"] is True
    assert summary["sidecar_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["auto_pass_allowed"] is False
    assert result["summary_action"] == "QUEUE_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_summary_unresolved_has_highest_priority():
    bad = _record()
    bad["pass_count_fabrication_allowed"] = True

    snapshot_index = build_validation_baseline_snapshot_index([bad])
    run_index = build_validation_run_index([_record()])

    summary = build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )
    result = classify_validation_baseline_summary(summary)

    assert summary["summary_status"] == "UNRESOLVED"
    assert summary["summary_action"] == "MARK_UNRESOLVED"
    assert summary["unresolved_count"] == 1
    assert result["summary_action"] == "MARK_UNRESOLVED"
    assert result["auto_repair_allowed"] is False


def test_summary_stale_from_run_index():
    snapshot_index = build_validation_baseline_snapshot_index([_record()])
    run_index = build_validation_run_index(
        [_record(result="FAIL", pass_count=0, baseline_status="STALE")]
    )

    summary = build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )

    assert summary["summary_status"] == "STALE"
    assert summary["summary_action"] == "MARK_STALE"
    assert summary["stale_count"] == 1
    assert summary["validation_result_fabrication_allowed"] is False


def test_summary_incomplete_from_snapshot_index():
    snapshot_index = build_validation_baseline_snapshot_index(
        [_record(result="INCOMPLETE", pass_count=0, baseline_status="INCOMPLETE")]
    )
    run_index = build_validation_run_index([_record()])

    summary = build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )

    assert summary["summary_status"] == "INCOMPLETE"
    assert summary["summary_action"] == "MARK_INCOMPLETE"
    assert summary["incomplete_count"] == 1
    assert summary["pass_count_fabrication_allowed"] is False


def test_summary_preserves_hard_boundaries():
    snapshot_index = build_validation_baseline_snapshot_index([_record()])
    run_index = build_validation_run_index([_record()])

    summary = build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )

    assert summary["validation_result_fabrication_allowed"] is False
    assert summary["pass_count_fabrication_allowed"] is False
    assert summary["source_artifact_mutation_allowed"] is False
    assert summary["evidence_backfill_allowed"] is False
    assert summary["correlation_id_auto_fill_allowed"] is False
    assert summary["placeholder_review_allowed"] is False
    assert summary["ui_dashboard_panel_allowed"] is False
    assert summary["core_mutation_allowed"] is False
    assert summary["p48_core_expansion_allowed"] is False


def test_summary_requires_indexes():
    try:
        build_validation_baseline_summary(
            snapshot_index=None,
            run_index={},
        )
    except ValueError as exc:
        assert "snapshot_index is required" in str(exc)
    else:
        raise AssertionError("missing snapshot_index should fail")
