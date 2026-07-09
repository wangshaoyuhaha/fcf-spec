from pathlib import Path

import pytest

from scripts.control_center_schema_consistency_guard import (
    REQUIRED_SAFETY_FLAGS,
    assert_governance_sources_readable,
    assert_schema_result_pass,
    classify_governance_source,
    discover_governance_sources,
    extract_markdown_key_values,
    load_governance_source,
    load_governance_sources,
    summarize_governance_sources,
    validate_final_state_record,
    validate_safety_boundary,
    validate_stage_record,
)


def _safe_boundary() -> dict[str, bool]:
    return dict(REQUIRED_SAFETY_FLAGS)


def test_validate_stage_record_passes_complete_record() -> None:
    record = {
        "app_id": "CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1",
        "stage_id": "D1",
        "status": "completed",
        "branch": "sidecar-control-center-schema-consistency-guard-app-1",
        "commit": "abc1234",
        "validation": "passed",
        "git_status": "clean",
        "safety_boundary": _safe_boundary(),
    }

    result = validate_stage_record(record)

    assert result.status == "PASS"
    assert result.missing_keys == []
    assert result.invalid_values == []


def test_validate_stage_record_blocks_missing_keys() -> None:
    result = validate_stage_record({"stage_id": "D1", "status": "completed"})

    assert result.status == "BLOCK"
    assert "app_id" in result.missing_keys
    assert "safety_boundary" in result.missing_keys


def test_validate_stage_record_blocks_invalid_status() -> None:
    record = {
        "app_id": "APP",
        "stage_id": "D1",
        "status": "done",
        "branch": "branch",
        "commit": "commit",
        "validation": "passed",
        "git_status": "clean",
        "safety_boundary": _safe_boundary(),
    }

    result = validate_stage_record(record)

    assert result.status == "BLOCK"
    assert "status:INVALID" in result.invalid_values


def test_validate_safety_boundary_blocks_trade_flags() -> None:
    boundary = _safe_boundary()
    boundary["real_trading_allowed"] = True
    boundary["buy_button_allowed"] = True

    invalid = validate_safety_boundary(boundary)

    assert "real_trading_allowed:EXPECTED_FALSE" in invalid
    assert "buy_button_allowed:EXPECTED_FALSE" in invalid


def test_validate_final_state_record_passes_complete_record() -> None:
    record = {
        "app_id": "CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1",
        "latest_main_commit": "abc1234",
        "main_merge_commit": "def5678",
        "final_branch_commit": "fed9876",
        "validation": "passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "none",
        "deploy": "none",
    }

    result = validate_final_state_record(record)

    assert result.status == "PASS"


def test_validate_final_state_record_blocks_release_or_deploy() -> None:
    record = {
        "app_id": "APP",
        "latest_main_commit": "abc1234",
        "main_merge_commit": "def5678",
        "final_branch_commit": "fed9876",
        "validation": "passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "v1",
        "deploy": "none",
    }

    result = validate_final_state_record(record)

    assert result.status == "BLOCK"
    assert "release:MUST_BE_NONE" in result.invalid_values


def test_assert_schema_result_pass_raises_on_block() -> None:
    result = validate_final_state_record({"app_id": "APP"})

    with pytest.raises(ValueError, match="CONTROL_CENTER_SCHEMA_CONSISTENCY_FAILED"):
        assert_schema_result_pass(result)


def test_classify_governance_source() -> None:
    assert classify_governance_source("docs/FCF_PROJECT_CONTROL_CENTER.md") == "CONTROL_CENTER"
    assert classify_governance_source("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md") == "BACKEND_HANDOFF"
    assert classify_governance_source("FCF_NEW_WINDOW_CHAT_PROMPT.md") == "NEW_WINDOW_PROMPT"
    assert classify_governance_source("FCF_CURRENT_STATE_TEST_APP_1_FINAL.md") == "FINAL_CURRENT_STATE"


def test_extract_markdown_key_values() -> None:
    text = """
# Header

branch: main
Latest main commit: abc1234
- git status: clean
- origin-main: synced
"""

    fields = extract_markdown_key_values(text)

    assert fields["branch"] == "main"
    assert fields["latest_main_commit"] == "abc1234"
    assert fields["git_status"] == "clean"
    assert fields["origin_main"] == "synced"


def test_load_governance_source_reads_utf8(tmp_path: Path) -> None:
    target = tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md"
    target.write_text("app_id: TEST\nbranch: main\n", encoding="utf-8")

    record = load_governance_source(target)

    assert record.exists is True
    assert record.utf8_status == "OK"
    assert record.source_kind == "FINAL_CURRENT_STATE"
    assert record.extracted_fields["app_id"] == "TEST"


def test_load_governance_source_reports_invalid_utf8(tmp_path: Path) -> None:
    target = tmp_path / "FCF_CURRENT_STATE_BAD.md"
    target.write_bytes(b"\xff")

    record = load_governance_source(target)

    assert record.exists is True
    assert record.utf8_status == "UTF8_DECODE_ERROR"
    assert record.extracted_fields == {}


def test_discover_and_load_governance_sources(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md").write_text("branch: main\n", encoding="utf-8")
    (tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md").write_text("branch: main\n", encoding="utf-8")
    (tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md").write_text("branch: main\n", encoding="utf-8")
    (tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md").write_text("app_id: TEST\n", encoding="utf-8")

    sources = discover_governance_sources(tmp_path)
    records = load_governance_sources(tmp_path)
    summary = summarize_governance_sources(records)

    assert "docs/FCF_PROJECT_CONTROL_CENTER.md" in sources
    assert "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md" in sources
    assert len(records) == 4
    assert summary["CONTROL_CENTER:OK"] == 1
    assert summary["FINAL_CURRENT_STATE:OK"] == 1
    assert_governance_sources_readable(records)


def test_assert_governance_sources_readable_blocks_missing(tmp_path: Path) -> None:
    records = load_governance_sources(tmp_path)

    with pytest.raises(ValueError, match="CONTROL_CENTER_SCHEMA_SOURCE_READ_FAILED"):
        assert_governance_sources_readable(records)

def test_normalize_field_name_aliases() -> None:
    from scripts.control_center_schema_consistency_guard import normalize_field_name

    assert normalize_field_name("Latest HEAD") == "latest_main_commit"
    assert normalize_field_name("merge-commit") == "main_merge_commit"
    assert normalize_field_name("D6 commit") == "final_branch_commit"
    assert normalize_field_name("origin/main") == "origin_main"
    assert normalize_field_name("git status") == "git_status"


def test_canonicalize_fields_maps_aliases() -> None:
    from scripts.control_center_schema_consistency_guard import canonicalize_fields

    fields = {
        "Latest HEAD": "abc1234 add final state",
        "merge commit": "def5678 merge app",
        "D6 commit": "9999999 closeout",
        "origin/main": "synced",
    }

    canonical = canonicalize_fields(fields)

    assert canonical["latest_main_commit"] == "abc1234 add final state"
    assert canonical["main_merge_commit"] == "def5678 merge app"
    assert canonical["final_branch_commit"] == "9999999 closeout"
    assert canonical["origin_main"] == "synced"


def test_normalize_commit_value_extracts_hash() -> None:
    from scripts.control_center_schema_consistency_guard import normalize_commit_value

    assert normalize_commit_value("65fba58 add final current state") == "65fba58"
    assert normalize_commit_value("merge commit: 274fec0 merge app") == "274fec0"


def test_normalize_status_text() -> None:
    from scripts.control_center_schema_consistency_guard import normalize_status_text

    assert normalize_status_text("ALL CHECKS PASSED") == "passed"
    assert normalize_status_text("git status clean") == "clean"
    assert normalize_status_text("origin/main synced") == "synced"
    assert normalize_status_text("none") == "none"


def test_build_final_state_record_from_alias_fields() -> None:
    from scripts.control_center_schema_consistency_guard import (
        build_final_state_record_from_fields,
        validate_final_state_record,
    )

    fields = {
        "app id": "APP",
        "Latest HEAD": "65fba58 add final current state",
        "merge commit": "274fec0 merge APP into main",
        "D6 commit": "28b01bf add D6 final closeout",
        "pytest": "1696 passed",
        "git status": "clean",
        "origin/main": "synced",
        "tag": "none",
        "release": "none",
        "deploy": "none",
    }

    record = build_final_state_record_from_fields(fields)
    result = validate_final_state_record(record)

    assert record["latest_main_commit"] == "65fba58"
    assert record["main_merge_commit"] == "274fec0"
    assert record["final_branch_commit"] == "28b01bf"
    assert result.status == "PASS"


def test_build_stage_record_from_alias_fields() -> None:
    from scripts.control_center_schema_consistency_guard import (
        build_stage_record_from_fields,
        validate_stage_record,
    )

    fields = {
        "app id": "APP",
        "stage id": "D3",
        "status": "completed",
        "branch": "sidecar-x",
        "commit": "abc1234 add D3",
        "validation": "passed",
        "git status": "clean",
        "paper only": "true",
        "local only": "true",
        "read only": "true",
        "sidecar only": "true",
        "operator review required": "true",
        "real trading allowed": "false",
        "broker api allowed": "false",
        "exchange api allowed": "false",
        "api key allowed": "false",
        "buy button allowed": "false",
        "sell button allowed": "false",
        "order button allowed": "false",
        "tag allowed": "false",
        "release allowed": "false",
        "deploy allowed": "false",
    }

    record = build_stage_record_from_fields(fields)
    result = validate_stage_record(record)

    assert record["commit"] == "abc1234"
    assert record["safety_boundary"]["paper_only"] is True
    assert record["safety_boundary"]["real_trading_allowed"] is False
    assert result.status == "PASS"


def test_validate_normalized_final_state_fields_blocks_release() -> None:
    from scripts.control_center_schema_consistency_guard import validate_normalized_final_state_fields

    fields = {
        "app id": "APP",
        "Latest HEAD": "65fba58 add final current state",
        "merge commit": "274fec0 merge APP into main",
        "D6 commit": "28b01bf add D6 final closeout",
        "pytest": "1696 passed",
        "git status": "clean",
        "origin/main": "synced",
        "tag": "none",
        "release": "v1",
        "deploy": "none",
    }

    result = validate_normalized_final_state_fields(fields)

    assert result.status == "BLOCK"
    assert "release:MUST_BE_NONE" in result.invalid_values


def test_build_field_value_matrix_normalizes_aliases() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_field_value_matrix,
    )

    records = [
        GovernanceSourceRecord(
            path="a.md",
            source_kind="FINAL_CURRENT_STATE",
            exists=True,
            utf8_status="OK",
            extracted_fields={"origin/main": "synced", "git status": "clean"},
        )
    ]

    matrix = build_field_value_matrix(records, ["origin_main", "git_status"])

    assert matrix["origin_main"]["a.md"] == "synced"
    assert matrix["git_status"]["a.md"] == "clean"


def test_cross_source_consistency_passes_matching_values() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        assert_cross_source_consistency_pass,
        build_cross_source_consistency_report,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"branch": "main", "release": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"branch": "main", "release": "none"}),
    ]

    report = build_cross_source_consistency_report(records, ["branch", "release"])

    assert report.status == "PASS"
    assert report.issue_count == 0
    assert_cross_source_consistency_pass(report)


def test_cross_source_consistency_blocks_conflicting_values() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_cross_source_consistency_report,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"release": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"release": "v1"}),
    ]

    report = build_cross_source_consistency_report(records, ["release"])

    assert report.status == "BLOCK"
    assert report.issues[0].severity == "BLOCK"
    assert report.issues[0].field_name == "release"


def test_cross_source_consistency_warns_partial_missing() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_cross_source_consistency_report,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"deploy": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {}),
    ]

    report = build_cross_source_consistency_report(records, ["deploy"])

    assert report.status == "WARN"
    assert report.issues[0].message == "PARTIAL_MISSING_FIELD"


def test_assert_cross_source_consistency_pass_raises_on_block() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        assert_cross_source_consistency_pass,
        build_cross_source_consistency_report,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"tag": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"tag": "v1"}),
    ]

    report = build_cross_source_consistency_report(records, ["tag"])

    with pytest.raises(ValueError, match="CONTROL_CENTER_CROSS_SOURCE_CONSISTENCY_FAILED"):
        assert_cross_source_consistency_pass(report)


def test_render_cross_source_consistency_report_md() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_cross_source_consistency_report,
        render_cross_source_consistency_report_md,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"branch": "main"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"branch": "main"}),
    ]

    report = build_cross_source_consistency_report(records, ["branch"])
    text = render_cross_source_consistency_report_md(report)

    assert "# CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 D4 Consistency Report" in text
    assert "- status: PASS" in text
    assert "- branch" in text


def test_default_consistency_fields_include_release_deploy() -> None:
    from scripts.control_center_schema_consistency_guard import default_consistency_fields

    fields = default_consistency_fields()

    assert "release" in fields
    assert "deploy" in fields
    assert "tag" in fields
    assert "validation" in fields


def test_classify_governance_source_handles_absolute_control_center_path(tmp_path: Path) -> None:
    from scripts.control_center_schema_consistency_guard import classify_governance_source

    target = tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md"

    assert classify_governance_source(target) == "CONTROL_CENTER"


def test_build_schema_consistency_packet_pass() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        assert_schema_consistency_packet_safe,
        build_schema_consistency_packet,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"branch": "main", "release": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"branch": "main", "release": "none"}),
    ]

    packet = build_schema_consistency_packet(records, ["branch", "release"])

    assert packet.stage_id == "CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1-D5"
    assert packet.status == "PASS"
    assert packet.source_count == 2
    assert packet.issue_count == 0
    assert packet.block_count == 0
    assert packet.warn_count == 0
    assert packet.operator_review_required is True
    assert packet.real_execution_allowed is False
    assert packet.trade_action_enabled is False
    assert_schema_consistency_packet_safe(packet)


def test_build_schema_consistency_packet_warn() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_schema_consistency_packet,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"deploy": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {}),
    ]

    packet = build_schema_consistency_packet(records, ["deploy"])

    assert packet.status == "WARN"
    assert packet.block_count == 0
    assert packet.warn_count == 1


def test_build_schema_consistency_packet_blocks_conflict() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        assert_schema_consistency_packet_safe,
        build_schema_consistency_packet,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"tag": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"tag": "v1"}),
    ]

    packet = build_schema_consistency_packet(records, ["tag"])

    assert packet.status == "BLOCK"
    assert packet.block_count == 1

    with pytest.raises(ValueError, match="CONTROL_CENTER_SCHEMA_CONSISTENCY_PACKET_BLOCKED"):
        assert_schema_consistency_packet_safe(packet)


def test_render_schema_consistency_packet_md_contains_safety_flags() -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_schema_consistency_packet,
        render_schema_consistency_packet_md,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"branch": "main"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"branch": "main"}),
    ]

    packet = build_schema_consistency_packet(records, ["branch"])
    text = render_schema_consistency_packet_md(packet)

    assert "# CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 D5 Packet" in text
    assert "- operator_review_required: true" in text
    assert "- real_execution_allowed: false" in text
    assert "- trade_action_enabled: false" in text


def test_write_schema_consistency_packet_md(tmp_path: Path) -> None:
    from scripts.control_center_schema_consistency_guard import (
        GovernanceSourceRecord,
        build_schema_consistency_packet,
        write_schema_consistency_packet_md,
    )

    records = [
        GovernanceSourceRecord("a.md", "FINAL_CURRENT_STATE", True, "OK", {"release": "none"}),
        GovernanceSourceRecord("b.md", "CONTROL_CENTER", True, "OK", {"release": "none"}),
    ]

    packet = build_schema_consistency_packet(records, ["release"])
    output = tmp_path / "packet.md"
    write_schema_consistency_packet_md(packet, output)

    text = output.read_text(encoding="utf-8")
    assert text.startswith("# CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1 D5 Packet")
    assert "- release" in text
