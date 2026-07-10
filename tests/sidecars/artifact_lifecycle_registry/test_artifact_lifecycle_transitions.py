import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.artifact_lifecycle_registry import (
    ALLOWED_LIFECYCLE_TRANSITIONS,
    build_transition_index,
    validate_lifecycle_transition,
)


def test_transition_policy_is_explicit():
    assert ("REGISTERED", "OBSERVED") in ALLOWED_LIFECYCLE_TRANSITIONS
    assert ("OBSERVED", "STALE") in ALLOWED_LIFECYCLE_TRANSITIONS
    assert ("STALE", "UNRESOLVED") in ALLOWED_LIFECYCLE_TRANSITIONS


def test_valid_transition_is_read_only_and_not_applied():
    result = validate_lifecycle_transition(
        artifact_id="artifact-1",
        from_status="REGISTERED",
        to_status="OBSERVED",
        reason_code="SOURCE_OBSERVED",
    )

    assert result["valid"] is True
    assert result["transition_state"] == "VALID_TRANSITION"
    assert result["transition_applied"] is False
    assert result["read_only"] is True
    assert result["index_only"] is True
    assert result["source_artifact_mutation_allowed"] is False
    assert result["artifact_status_auto_repair_allowed"] is False
    assert result["evidence_backfill_allowed"] is False
    assert result["operator_review_required"] is True
    assert result["auto_pass_allowed"] is False


def test_no_change_transition_does_not_mutate_source():
    result = validate_lifecycle_transition(
        artifact_id="artifact-1",
        from_status="OBSERVED",
        to_status="OBSERVED",
        reason_code="RECHECK_ONLY",
    )

    assert result["valid"] is True
    assert result["transition_state"] == "NO_CHANGE"
    assert result["transition_applied"] is False
    assert result["source_artifact_mutation_allowed"] is False


def test_unsupported_transition_is_unresolved():
    result = validate_lifecycle_transition(
        artifact_id="artifact-1",
        from_status="STALE",
        to_status="REGISTERED",
        reason_code="BAD_REWIND",
    )

    assert result["valid"] is False
    assert result["transition_state"] == "UNRESOLVED"
    assert "TRANSITION_NOT_ALLOWED" in result["issues"]
    assert result["artifact_status_auto_repair_allowed"] is False


def test_missing_reason_code_is_unresolved():
    result = validate_lifecycle_transition(
        artifact_id="artifact-1",
        from_status="REGISTERED",
        to_status="OBSERVED",
        reason_code="",
    )

    assert result["valid"] is False
    assert result["transition_state"] == "UNRESOLVED"
    assert "MISSING_REASON_CODE" in result["issues"]


def test_transition_index_marks_unresolved_without_auto_repair():
    packet = build_transition_index(
        (
            {
                "artifact_id": "artifact-1",
                "from_status": "REGISTERED",
                "to_status": "OBSERVED",
                "reason_code": "SOURCE_OBSERVED",
            },
            {
                "artifact_id": "artifact-2",
                "from_status": "STALE",
                "to_status": "REGISTERED",
                "reason_code": "BAD_REWIND",
            },
        )
    )

    assert packet["stage"] == "D2"
    assert packet["index_status"] == "UNRESOLVED"
    assert packet["transition_count"] == 2
    assert packet["valid_transition_count"] == 1
    assert packet["unresolved_count"] == 1
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["transition_applied"] is False
    assert packet["source_artifact_mutation_allowed"] is False
    assert packet["artifact_status_auto_repair_allowed"] is False
    assert packet["evidence_backfill_allowed"] is False
    assert packet["operator_review_required"] is True
    assert packet["auto_pass_allowed"] is False
