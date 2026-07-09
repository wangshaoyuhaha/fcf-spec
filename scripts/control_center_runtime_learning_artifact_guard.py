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


@dataclass(frozen=True)
class RuntimeDirtyStatusRecord:
    relative_path: str
    git_status_code: str
    is_known_runtime_learning_artifact: bool
    restorable_runtime_dirt: bool


def parse_git_status_line(line: str) -> RuntimeDirtyStatusRecord:
    status_code = line[:2].strip()
    path = normalize_path(line[3:].strip())
    is_known = is_runtime_learning_artifact_path(path)
    return RuntimeDirtyStatusRecord(
        relative_path=path,
        git_status_code=status_code,
        is_known_runtime_learning_artifact=is_known,
        restorable_runtime_dirt=is_known and status_code in {"M", "MM"},
    )


def parse_git_status_lines(lines: tuple[str, ...]) -> tuple[RuntimeDirtyStatusRecord, ...]:
    return tuple(parse_git_status_line(line) for line in lines if line.strip())


def runtime_dirty_records_only(
    records: tuple[RuntimeDirtyStatusRecord, ...],
) -> bool:
    return all(record.restorable_runtime_dirt for record in records)


@dataclass(frozen=True)
class RuntimeLearningRestorePlan:
    paths_to_restore: tuple[str, ...]
    blocked_dirty_paths: tuple[str, ...]
    restore_required: bool
    restore_command: tuple[str, ...]


def build_runtime_learning_restore_plan(
    records: tuple[RuntimeDirtyStatusRecord, ...],
) -> RuntimeLearningRestorePlan:
    restore_paths: list[str] = []
    blocked_paths: list[str] = []

    for record in records:
        if record.restorable_runtime_dirt:
            restore_paths.append(record.relative_path)
        else:
            blocked_paths.append(record.relative_path)

    unique_restore_paths = tuple(dict.fromkeys(restore_paths))
    unique_blocked_paths = tuple(dict.fromkeys(blocked_paths))

    return RuntimeLearningRestorePlan(
        paths_to_restore=unique_restore_paths,
        blocked_dirty_paths=unique_blocked_paths,
        restore_required=bool(unique_restore_paths),
        restore_command=("git", "restore", *unique_restore_paths),
    )


def restore_plan_allows_closeout(plan: RuntimeLearningRestorePlan) -> bool:
    return not plan.blocked_dirty_paths


@dataclass(frozen=True)
class RuntimeEvidenceCollision:
    runtime_path: str
    evidence_path: str
    reason_code: str


@dataclass(frozen=True)
class RuntimeEvidenceExclusionResult:
    passed: bool
    collisions: tuple[RuntimeEvidenceCollision, ...]
    reason_codes: tuple[str, ...]


def validate_runtime_artifacts_excluded_from_evidence(
    runtime_paths: tuple[str, ...],
    evidence_source_paths: tuple[str, ...],
) -> RuntimeEvidenceExclusionResult:
    normalized_runtime_paths = tuple(normalize_path(path) for path in runtime_paths)
    normalized_evidence_paths = tuple(normalize_path(path) for path in evidence_source_paths)

    collisions: list[RuntimeEvidenceCollision] = []

    for runtime_path in normalized_runtime_paths:
        for evidence_path in normalized_evidence_paths:
            if runtime_path == evidence_path:
                collisions.append(
                    RuntimeEvidenceCollision(
                        runtime_path=runtime_path,
                        evidence_path=evidence_path,
                        reason_code="RUNTIME_ARTIFACT_USED_AS_EVIDENCE_SOURCE",
                    )
                )

    reason_codes = tuple(dict.fromkeys(collision.reason_code for collision in collisions))

    return RuntimeEvidenceExclusionResult(
        passed=not collisions,
        collisions=tuple(collisions),
        reason_codes=reason_codes,
    )


def validate_runtime_artifact_path_not_promoted(path: str) -> RuntimeLearningArtifactValidation:
    normalized = normalize_path(path)
    reasons: list[str] = []

    if is_runtime_learning_artifact_path(normalized):
        reasons.append("RUNTIME_ARTIFACT_PATH_NOT_PROMOTABLE")

    if normalized.startswith("FCF_CURRENT_STATE_"):
        reasons.append("FINAL_CURRENT_STATE_PATH_RESERVED")

    if normalized.startswith("FCF_PROJECT_BACKEND_HANDOFF"):
        reasons.append("BACKEND_HANDOFF_PATH_RESERVED")

    if normalized.startswith("FCF_NEW_WINDOW_CHAT_PROMPT"):
        reasons.append("NEW_WINDOW_PROMPT_PATH_RESERVED")

    if normalized == "docs/FCF_PROJECT_CONTROL_CENTER.md":
        reasons.append("CONTROL_CENTER_PATH_RESERVED")

    return RuntimeLearningArtifactValidation(
        passed=not reasons,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


@dataclass(frozen=True)
class RuntimeLearningArtifactGuardPacket:
    app_id: str
    total_dirty_records: int
    restorable_runtime_records: int
    blocked_dirty_paths: tuple[str, ...]
    evidence_collision_count: int
    restore_required: bool
    closeout_allowed: bool
    reason_codes: tuple[str, ...]


def build_runtime_learning_artifact_guard_packet(
    dirty_records: tuple[RuntimeDirtyStatusRecord, ...],
    restore_plan: RuntimeLearningRestorePlan,
    evidence_result: RuntimeEvidenceExclusionResult,
    app_id: str = "CONTROL-CENTER-RUNTIME-LEARNING-ARTIFACT-GUARD-APP-1",
) -> RuntimeLearningArtifactGuardPacket:
    reasons: list[str] = []

    restorable_count = sum(1 for record in dirty_records if record.restorable_runtime_dirt)

    if restore_plan.blocked_dirty_paths:
        reasons.append("UNKNOWN_DIRTY_FILES_BLOCK_CLOSEOUT")

    if evidence_result.collisions:
        reasons.extend(evidence_result.reason_codes)

    if restore_plan.restore_required:
        reasons.append("RUNTIME_RESTORE_REQUIRED_BEFORE_FINAL_CLEAN_STATE")

    closeout_allowed = (
        not restore_plan.blocked_dirty_paths
        and not evidence_result.collisions
    )

    return RuntimeLearningArtifactGuardPacket(
        app_id=app_id,
        total_dirty_records=len(dirty_records),
        restorable_runtime_records=restorable_count,
        blocked_dirty_paths=restore_plan.blocked_dirty_paths,
        evidence_collision_count=len(evidence_result.collisions),
        restore_required=restore_plan.restore_required,
        closeout_allowed=closeout_allowed,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


@dataclass(frozen=True)
class RuntimeLearningArtifactCloseout:
    app_id: str
    completed_stages: tuple[str, ...]
    final_status: str
    closeout_allowed: bool
    restore_required: bool
    blocked_dirty_paths: tuple[str, ...]
    reason_codes: tuple[str, ...]
    safety_boundary: tuple[str, ...]


def build_runtime_learning_artifact_closeout(
    packet: RuntimeLearningArtifactGuardPacket,
) -> RuntimeLearningArtifactCloseout:
    return RuntimeLearningArtifactCloseout(
        app_id=packet.app_id,
        completed_stages=(
            "D1 runtime learning artifact contract",
            "D2 runtime artifact dirty-state detector",
            "D3 runtime restore plan",
            "D4 final evidence exclusion guard",
            "D5 runtime learning artifact guard packet",
            "D5 repair syntax regression",
            "D6 final workflow handoff and closeout",
        ),
        final_status="PASS" if packet.closeout_allowed else "BLOCKED",
        closeout_allowed=packet.closeout_allowed,
        restore_required=packet.restore_required,
        blocked_dirty_paths=packet.blocked_dirty_paths,
        reason_codes=packet.reason_codes,
        safety_boundary=(
            "paper-only",
            "local-only",
            "read-only governance validation",
            "sidecar-only",
            "operator review required",
            "no P48",
            "no core mutation",
            "no real trading",
            "no broker API",
            "no exchange API",
            "no API key",
            "no buy button",
            "no sell button",
            "no order button",
            "no tag",
            "no release",
            "no deploy",
        ),
    )
