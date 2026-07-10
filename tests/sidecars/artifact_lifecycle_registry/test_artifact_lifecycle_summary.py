import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.artifact_lifecycle_registry import (
    build_artifact_state_snapshot_index,
    build_lifecycle_registry_summary,
    build_transition_index,
    classify_lifecycle_registry_summary,
)


def _record(status="REGISTERED", artifact_id="artifact-1"):
    return {
        "artifact_id": artifact_id,
        "artifact_type": "archive_packet",
        "artifact_path": f"runtime/archive/{artifact_id}.json",
        "lifecycle_status": status,
    }


def _transition(
    artifact_id="artifact-1",
    from_status="REGISTERED",
    to_status="OBSERVED",
    reason_code="SOURCE_OBSERVED",
):
    return {
        "artifact_id": artifact_id,
        "from_status": from_status,
        "to_status": to_status,
        "reason_code": reason_code,
    }


def test_registry_summary_observed_requires_operator_review():
    snapshot_index = build_artifact_state_snapshot_index(
        [_record(status="REGISTERED")]
    )
    transition_index = build_transition_index((_transition(),))

    summary = build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )
    classification = classify_lifecycle_registry_summary(summary)

    assert summary["stage"] == "D4"
    assert summary["registry_summary_status"] == "OBSERVED"
    assert summary["registry_action"] == "QUEUE_OPERATOR_REVIEW"
    assert summary["read_only"] is True
    assert summary["index_only"] is True
    assert summary["summary_only"] is True
    assert summary["sidecar_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["auto_pass_allowed"] is False
    assert classification["registry_action"] == "QUEUE_OPERATOR_REVIEW"
    assert classification["auto_pass_allowed"] is False


def test_registry_summary_unresolved_from_bad_transition():
    snapshot_index = build_artifact_state_snapshot_index(
        [_record(status="REGISTERED")]
    )
    transition_index = build_transition_index(
        (
            _transition(
                from_status="STALE",
                to_status="REGISTERED",
                reason_code="BAD_REWIND",
            ),
        )
    )

    summary = build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )
    classification = classify_lifecycle_registry_summary(summary)

    assert summary["registry_summary_status"] == "UNRESOLVED"
    assert summary["registry_action"] == "MARK_UNRESOLVED"
    assert summary["unresolved_count"] == 1
    assert classification["registry_action"] == "MARK_UNRESOLVED"
    assert classification["auto_repair_allowed"] is False


def test_registry_summary_stale_from_snapshot_index():
    snapshot_index = build_artifact_state_snapshot_index(
        [
            _record(status="REGISTERED", artifact_id="artifact-1"),
            _record(status="STALE", artifact_id="artifact-2"),
        ]
    )
    transition_index = build_transition_index((_transition(),))

    summary = build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )

    assert summary["registry_summary_status"] == "STALE"
    assert summary["registry_action"] == "MARK_STALE"
    assert summary["stale_count"] == 1
    assert summary["source_artifact_mutation_allowed"] is False


def test_registry_summary_incomplete_from_snapshot_index():
    snapshot_index = build_artifact_state_snapshot_index(
        [_record(status="INCOMPLETE")]
    )
    transition_index = build_transition_index(
        (
            _transition(
                from_status="OBSERVED",
                to_status="OBSERVED",
                reason_code="RECHECK_ONLY",
            ),
        )
    )

    summary = build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )

    assert summary["registry_summary_status"] == "INCOMPLETE"
    assert summary["registry_action"] == "MARK_INCOMPLETE"
    assert summary["incomplete_count"] == 1
    assert summary["transition_applied"] is False
    assert summary["artifact_status_auto_repair_allowed"] is False


def test_registry_summary_preserves_hard_boundaries():
    snapshot_index = build_artifact_state_snapshot_index(
        [_record(status="REGISTERED")]
    )
    transition_index = build_transition_index((_transition(),))

    summary = build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )

    assert summary["source_artifact_mutation_allowed"] is False
    assert summary["artifact_status_auto_repair_allowed"] is False
    assert summary["transition_applied"] is False
    assert summary["evidence_backfill_allowed"] is False
    assert summary["correlation_id_auto_fill_allowed"] is False
    assert summary["placeholder_review_allowed"] is False
    assert summary["core_mutation_allowed"] is False
    assert summary["p48_core_expansion_allowed"] is False


def test_registry_summary_requires_indexes():
    try:
        build_lifecycle_registry_summary(
            snapshot_index=None,
            transition_index={},
        )
    except ValueError as exc:
        assert "snapshot_index is required" in str(exc)
    else:
        raise AssertionError("missing snapshot_index should fail")
