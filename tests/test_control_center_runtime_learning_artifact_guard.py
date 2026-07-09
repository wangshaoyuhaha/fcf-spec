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


def test_parse_git_status_line_detects_known_runtime_dirty_file():
    from scripts.control_center_runtime_learning_artifact_guard import parse_git_status_line

    record = parse_git_status_line(" M runtime/learning_engine/shadow_ledger.json")

    assert record.relative_path == "runtime/learning_engine/shadow_ledger.json"
    assert record.git_status_code == "M"
    assert record.is_known_runtime_learning_artifact is True
    assert record.restorable_runtime_dirt is True


def test_parse_git_status_line_detects_unknown_dirty_file():
    from scripts.control_center_runtime_learning_artifact_guard import parse_git_status_line

    record = parse_git_status_line(" M docs/FCF_PROJECT_CONTROL_CENTER.md")

    assert record.relative_path == "docs/FCF_PROJECT_CONTROL_CENTER.md"
    assert record.git_status_code == "M"
    assert record.is_known_runtime_learning_artifact is False
    assert record.restorable_runtime_dirt is False


def test_parse_git_status_lines_preserves_records():
    from scripts.control_center_runtime_learning_artifact_guard import parse_git_status_lines

    records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M runtime/operator_console/ai_learning_audit_report.json",
        )
    )

    assert len(records) == 2
    assert records[0].restorable_runtime_dirt is True
    assert records[1].restorable_runtime_dirt is True


def test_runtime_dirty_records_only_accepts_known_runtime_dirt():
    from scripts.control_center_runtime_learning_artifact_guard import (
        parse_git_status_lines,
        runtime_dirty_records_only,
    )

    records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M runtime/operator_console/p13_final_closeout_summary.json",
        )
    )

    assert runtime_dirty_records_only(records) is True


def test_runtime_dirty_records_only_blocks_unknown_dirty_file():
    from scripts.control_center_runtime_learning_artifact_guard import (
        parse_git_status_lines,
        runtime_dirty_records_only,
    )

    records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M docs/FCF_PROJECT_CONTROL_CENTER.md",
        )
    )

    assert runtime_dirty_records_only(records) is False


def test_builds_restore_plan_for_known_runtime_dirty_files():
    from scripts.control_center_runtime_learning_artifact_guard import (
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
    )

    records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M runtime/operator_console/ai_learning_memory_ledger.json",
        )
    )

    plan = build_runtime_learning_restore_plan(records)

    assert plan.paths_to_restore == (
        "runtime/learning_engine/shadow_ledger.json",
        "runtime/operator_console/ai_learning_memory_ledger.json",
    )
    assert plan.blocked_dirty_paths == ()
    assert plan.restore_required is True
    assert plan.restore_command == (
        "git",
        "restore",
        "runtime/learning_engine/shadow_ledger.json",
        "runtime/operator_console/ai_learning_memory_ledger.json",
    )


def test_restore_plan_blocks_unknown_dirty_files():
    from scripts.control_center_runtime_learning_artifact_guard import (
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
    )

    records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M docs/FCF_PROJECT_CONTROL_CENTER.md",
        )
    )

    plan = build_runtime_learning_restore_plan(records)

    assert plan.paths_to_restore == ("runtime/learning_engine/shadow_ledger.json",)
    assert plan.blocked_dirty_paths == ("docs/FCF_PROJECT_CONTROL_CENTER.md",)
    assert plan.restore_required is True


def test_restore_plan_deduplicates_paths():
    from scripts.control_center_runtime_learning_artifact_guard import (
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
    )

    records = parse_git_status_lines(
        (
            " M runtime/operator_console/p13_final_closeout_summary.json",
            " M runtime/operator_console/p13_final_closeout_summary.json",
        )
    )

    plan = build_runtime_learning_restore_plan(records)

    assert plan.paths_to_restore == ("runtime/operator_console/p13_final_closeout_summary.json",)


def test_restore_plan_allows_closeout_when_no_unknown_dirty_files():
    from scripts.control_center_runtime_learning_artifact_guard import (
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        restore_plan_allows_closeout,
    )

    records = parse_git_status_lines((" M runtime/learning_engine/shadow_ledger.json",))
    plan = build_runtime_learning_restore_plan(records)

    assert restore_plan_allows_closeout(plan) is True


def test_restore_plan_blocks_closeout_when_unknown_dirty_files_exist():
    from scripts.control_center_runtime_learning_artifact_guard import (
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        restore_plan_allows_closeout,
    )

    records = parse_git_status_lines((" M docs/FCF_PROJECT_CONTROL_CENTER.md",))
    plan = build_runtime_learning_restore_plan(records)

    assert restore_plan_allows_closeout(plan) is False


def test_runtime_artifacts_are_excluded_from_final_evidence_sources_when_absent():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=(
            "FCF_CURRENT_STATE_CONTROL_CENTER_HANDOFF_FRESHNESS_GUARD_APP_1_FINAL.md",
            "docs/FCF_PROJECT_CONTROL_CENTER.md",
        ),
    )

    assert result.passed is True
    assert result.collisions == ()
    assert result.reason_codes == ()


def test_runtime_artifacts_are_blocked_when_used_as_evidence_sources():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=(
            "runtime/learning_engine/shadow_ledger.json",
            "FCF_CURRENT_STATE_ALPHA_FINAL.md",
        ),
    )

    assert result.passed is False
    assert result.reason_codes == ("RUNTIME_ARTIFACT_USED_AS_EVIDENCE_SOURCE",)
    assert result.collisions[0].runtime_path == "runtime/learning_engine/shadow_ledger.json"


def test_runtime_artifact_path_cannot_be_promoted():
    from scripts.control_center_runtime_learning_artifact_guard import (
        validate_runtime_artifact_path_not_promoted,
    )

    result = validate_runtime_artifact_path_not_promoted(
        "runtime/operator_console/ai_learning_audit_report.json"
    )

    assert result.passed is False
    assert "RUNTIME_ARTIFACT_PATH_NOT_PROMOTABLE" in result.reason_codes


def test_reserved_final_current_state_path_is_detected():
    from scripts.control_center_runtime_learning_artifact_guard import (
        validate_runtime_artifact_path_not_promoted,
    )

    result = validate_runtime_artifact_path_not_promoted("FCF_CURRENT_STATE_ALPHA_FINAL.md")

    assert result.passed is False
    assert "FINAL_CURRENT_STATE_PATH_RESERVED" in result.reason_codes


def test_reserved_handoff_paths_are_detected():
    from scripts.control_center_runtime_learning_artifact_guard import (
        validate_runtime_artifact_path_not_promoted,
    )

    backend = validate_runtime_artifact_path_not_promoted(
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"
    )
    prompt = validate_runtime_artifact_path_not_promoted("FCF_NEW_WINDOW_CHAT_PROMPT.md")
    control = validate_runtime_artifact_path_not_promoted("docs/FCF_PROJECT_CONTROL_CENTER.md")

    assert "BACKEND_HANDOFF_PATH_RESERVED" in backend.reason_codes
    assert "NEW_WINDOW_PROMPT_PATH_RESERVED" in prompt.reason_codes
    assert "CONTROL_CENTER_PATH_RESERVED" in control.reason_codes


def test_regular_non_runtime_path_can_pass_promotion_check():
    from scripts.control_center_runtime_learning_artifact_guard import (
        validate_runtime_artifact_path_not_promoted,
    )

    result = validate_runtime_artifact_path_not_promoted("docs/ordinary_note.md")

    assert result.passed is True
    assert result.reason_codes == ()


def test_guard_packet_allows_closeout_when_only_restorable_runtime_dirt_exists():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        build_runtime_learning_artifact_guard_packet,
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    dirty_records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M runtime/operator_console/ai_learning_audit_report.json",
        )
    )
    restore_plan = build_runtime_learning_restore_plan(dirty_records)
    evidence_result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=("FCF_CURRENT_STATE_ALPHA_FINAL.md",),
    )

    packet = build_runtime_learning_artifact_guard_packet(
        dirty_records,
        restore_plan,
        evidence_result,
    )

    assert packet.app_id == "CONTROL-CENTER-RUNTIME-LEARNING-ARTIFACT-GUARD-APP-1"
    assert packet.total_dirty_records == 2
    assert packet.restorable_runtime_records == 2
    assert packet.blocked_dirty_paths == ()
    assert packet.evidence_collision_count == 0
    assert packet.restore_required is True
    assert packet.closeout_allowed is True
    assert packet.reason_codes == ("RUNTIME_RESTORE_REQUIRED_BEFORE_FINAL_CLEAN_STATE",)


def test_guard_packet_blocks_unknown_dirty_files():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        build_runtime_learning_artifact_guard_packet,
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    dirty_records = parse_git_status_lines(
        (
            " M runtime/learning_engine/shadow_ledger.json",
            " M docs/FCF_PROJECT_CONTROL_CENTER.md",
        )
    )
    restore_plan = build_runtime_learning_restore_plan(dirty_records)
    evidence_result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=("FCF_CURRENT_STATE_ALPHA_FINAL.md",),
    )

    packet = build_runtime_learning_artifact_guard_packet(
        dirty_records,
        restore_plan,
        evidence_result,
    )

    assert packet.closeout_allowed is False
    assert packet.blocked_dirty_paths == ("docs/FCF_PROJECT_CONTROL_CENTER.md",)
    assert "UNKNOWN_DIRTY_FILES_BLOCK_CLOSEOUT" in packet.reason_codes


def test_guard_packet_blocks_runtime_evidence_collision():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        build_runtime_learning_artifact_guard_packet,
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    dirty_records = parse_git_status_lines((" M runtime/learning_engine/shadow_ledger.json",))
    restore_plan = build_runtime_learning_restore_plan(dirty_records)
    evidence_result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=("runtime/learning_engine/shadow_ledger.json",),
    )

    packet = build_runtime_learning_artifact_guard_packet(
        dirty_records,
        restore_plan,
        evidence_result,
    )

    assert packet.closeout_allowed is False
    assert packet.evidence_collision_count == 1
    assert "RUNTIME_ARTIFACT_USED_AS_EVIDENCE_SOURCE" in packet.reason_codes


def test_guard_packet_handles_empty_clean_state():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        build_runtime_learning_artifact_guard_packet,
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    dirty_records = parse_git_status_lines(())
    restore_plan = build_runtime_learning_restore_plan(dirty_records)
    evidence_result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=("FCF_CURRENT_STATE_ALPHA_FINAL.md",),
    )

    packet = build_runtime_learning_artifact_guard_packet(
        dirty_records,
        restore_plan,
        evidence_result,
    )

    assert packet.total_dirty_records == 0
    assert packet.restorable_runtime_records == 0
    assert packet.restore_required is False
    assert packet.closeout_allowed is True
    assert packet.reason_codes == ()


def test_builds_runtime_learning_artifact_closeout_pass():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        build_runtime_learning_artifact_closeout,
        build_runtime_learning_artifact_guard_packet,
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    dirty_records = parse_git_status_lines(
        (" M runtime/learning_engine/shadow_ledger.json",)
    )
    restore_plan = build_runtime_learning_restore_plan(dirty_records)
    evidence_result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=("FCF_CURRENT_STATE_ALPHA_FINAL.md",),
    )
    packet = build_runtime_learning_artifact_guard_packet(
        dirty_records,
        restore_plan,
        evidence_result,
    )

    closeout = build_runtime_learning_artifact_closeout(packet)

    assert closeout.app_id == "CONTROL-CENTER-RUNTIME-LEARNING-ARTIFACT-GUARD-APP-1"
    assert closeout.final_status == "PASS"
    assert closeout.closeout_allowed is True
    assert closeout.restore_required is True
    assert closeout.blocked_dirty_paths == ()
    assert "D6 final workflow handoff and closeout" in closeout.completed_stages
    assert "no deploy" in closeout.safety_boundary


def test_builds_runtime_learning_artifact_closeout_blocked():
    from scripts.control_center_runtime_learning_artifact_guard import (
        RUNTIME_LEARNING_ARTIFACT_PATHS,
        build_runtime_learning_artifact_closeout,
        build_runtime_learning_artifact_guard_packet,
        build_runtime_learning_restore_plan,
        parse_git_status_lines,
        validate_runtime_artifacts_excluded_from_evidence,
    )

    dirty_records = parse_git_status_lines(
        (" M docs/FCF_PROJECT_CONTROL_CENTER.md",)
    )
    restore_plan = build_runtime_learning_restore_plan(dirty_records)
    evidence_result = validate_runtime_artifacts_excluded_from_evidence(
        runtime_paths=RUNTIME_LEARNING_ARTIFACT_PATHS,
        evidence_source_paths=("FCF_CURRENT_STATE_ALPHA_FINAL.md",),
    )
    packet = build_runtime_learning_artifact_guard_packet(
        dirty_records,
        restore_plan,
        evidence_result,
    )

    closeout = build_runtime_learning_artifact_closeout(packet)

    assert closeout.final_status == "BLOCKED"
    assert closeout.closeout_allowed is False
    assert closeout.blocked_dirty_paths == ("docs/FCF_PROJECT_CONTROL_CENTER.md",)
    assert "UNKNOWN_DIRTY_FILES_BLOCK_CLOSEOUT" in closeout.reason_codes
