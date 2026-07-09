from scripts.control_center_runtime_learning_artifact_guard import (
    RUNTIME_LEARNING_ARTIFACT_PATHS,
    RuntimeLearningArtifactRecord,
    build_runtime_learning_artifact_record,
    is_runtime_learning_artifact_path,
    validate_runtime_learning_artifact_record,
)


def test_known_runtime_learning_artifacts_are_classified():
    for path in RUNTIME_LEARNING_ARTIFACT_PATHS:
        record = build_runtime_learning_artifact_record(path)
        assert record.relative_path == path
        assert record.is_runtime_learning_artifact is True
        assert record.generated_by_validation is True
        assert record.final_evidence_allowed is False
        assert record.handoff_source_allowed is False
        assert record.control_center_truth_allowed is False
        assert record.must_restore_before_closeout is True


def test_known_runtime_learning_artifacts_pass_validation():
    for path in RUNTIME_LEARNING_ARTIFACT_PATHS:
        result = validate_runtime_learning_artifact_record(
            build_runtime_learning_artifact_record(path)
        )
        assert result.passed is True
        assert result.reason_codes == ()


def test_unknown_runtime_learning_artifact_is_blocked():
    result = validate_runtime_learning_artifact_record(
        build_runtime_learning_artifact_record("runtime/unknown.json")
    )
    assert result.passed is False
    assert "UNKNOWN_RUNTIME_LEARNING_ARTIFACT" in result.reason_codes


def test_runtime_artifact_cannot_be_final_evidence():
    record = RuntimeLearningArtifactRecord(
        relative_path="runtime/learning_engine/shadow_ledger.json",
        is_runtime_learning_artifact=True,
        generated_by_validation=True,
        final_evidence_allowed=True,
        handoff_source_allowed=False,
        control_center_truth_allowed=False,
        must_restore_before_closeout=True,
    )
    result = validate_runtime_learning_artifact_record(record)
    assert result.passed is False
    assert "RUNTIME_FINAL_EVIDENCE_NOT_ALLOWED" in result.reason_codes


def test_runtime_artifact_cannot_be_handoff_source():
    record = RuntimeLearningArtifactRecord(
        relative_path="runtime/operator_console/ai_learning_memory_ledger.json",
        is_runtime_learning_artifact=True,
        generated_by_validation=True,
        final_evidence_allowed=False,
        handoff_source_allowed=True,
        control_center_truth_allowed=False,
        must_restore_before_closeout=True,
    )
    result = validate_runtime_learning_artifact_record(record)
    assert result.passed is False
    assert "RUNTIME_HANDOFF_SOURCE_NOT_ALLOWED" in result.reason_codes


def test_runtime_artifact_cannot_be_control_center_truth():
    record = RuntimeLearningArtifactRecord(
        relative_path="runtime/operator_console/ai_learning_audit_report.json",
        is_runtime_learning_artifact=True,
        generated_by_validation=True,
        final_evidence_allowed=False,
        handoff_source_allowed=False,
        control_center_truth_allowed=True,
        must_restore_before_closeout=True,
    )
    result = validate_runtime_learning_artifact_record(record)
    assert result.passed is False
    assert "RUNTIME_CONTROL_CENTER_TRUTH_NOT_ALLOWED" in result.reason_codes


def test_runtime_artifact_must_restore_before_closeout():
    record = RuntimeLearningArtifactRecord(
        relative_path="runtime/operator_console/p13_final_closeout_summary.json",
        is_runtime_learning_artifact=True,
        generated_by_validation=True,
        final_evidence_allowed=False,
        handoff_source_allowed=False,
        control_center_truth_allowed=False,
        must_restore_before_closeout=False,
    )
    result = validate_runtime_learning_artifact_record(record)
    assert result.passed is False
    assert "RUNTIME_RESTORE_REQUIRED" in result.reason_codes


def test_runtime_learning_path_detection_accepts_slashes():
    assert is_runtime_learning_artifact_path("runtime/learning_engine/shadow_ledger.json") is True
    assert is_runtime_learning_artifact_path("runtime\\learning_engine\\shadow_ledger.json") is True
    assert is_runtime_learning_artifact_path("FCF_CURRENT_STATE_ALPHA_FINAL.md") is False
