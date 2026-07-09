from __future__ import annotations

from dataclasses import dataclass


RUNTIME_LEARNING_ARTIFACT_PATHS = (
    "runtime/learning_engine/shadow_ledger.json",
    "runtime/operator_console/ai_learning_audit_report.json",
    "runtime/operator_console/ai_learning_memory_ledger.json",
    "runtime/operator_console/p13_final_closeout_summary.json",
)


@dataclass(frozen=True)
class RuntimeLearningArtifactRecord:
    relative_path: str
    is_runtime_learning_artifact: bool
    generated_by_validation: bool
    final_evidence_allowed: bool
    handoff_source_allowed: bool
    control_center_truth_allowed: bool
    must_restore_before_closeout: bool


@dataclass(frozen=True)
class RuntimeLearningArtifactValidation:
    passed: bool
    reason_codes: tuple[str, ...]


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def is_runtime_learning_artifact_path(path: str) -> bool:
    return normalize_path(path) in RUNTIME_LEARNING_ARTIFACT_PATHS


def build_runtime_learning_artifact_record(path: str) -> RuntimeLearningArtifactRecord:
    normalized = normalize_path(path)
    is_known = is_runtime_learning_artifact_path(normalized)
    return RuntimeLearningArtifactRecord(
        relative_path=normalized,
        is_runtime_learning_artifact=is_known,
        generated_by_validation=is_known,
        final_evidence_allowed=False,
        handoff_source_allowed=False,
        control_center_truth_allowed=False,
        must_restore_before_closeout=is_known,
    )


def validate_runtime_learning_artifact_record(
    record: RuntimeLearningArtifactRecord,
) -> RuntimeLearningArtifactValidation:
    reasons: list[str] = []

    if not record.is_runtime_learning_artifact:
        reasons.append("UNKNOWN_RUNTIME_LEARNING_ARTIFACT")

    if record.final_evidence_allowed:
        reasons.append("RUNTIME_FINAL_EVIDENCE_NOT_ALLOWED")

    if record.handoff_source_allowed:
        reasons.append("RUNTIME_HANDOFF_SOURCE_NOT_ALLOWED")

    if record.control_center_truth_allowed:
        reasons.append("RUNTIME_CONTROL_CENTER_TRUTH_NOT_ALLOWED")

    if not record.must_restore_before_closeout:
        reasons.append("RUNTIME_RESTORE_REQUIRED")

    return RuntimeLearningArtifactValidation(
        passed=not reasons,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )
