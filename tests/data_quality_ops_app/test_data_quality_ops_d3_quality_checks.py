import json

from data_quality_ops_app import (
    CHECK_STATUS_FAIL,
    CHECK_STATUS_PASS,
    CHECK_STATUS_REVIEW_REQUIRED,
    build_data_quality_ops_check,
    build_data_quality_ops_checks,
    load_data_quality_ops_source,
    summarize_data_quality_ops_checks,
    validate_data_quality_ops_check,
)


def test_data_quality_ops_d3_builds_pass_check(tmp_path):
    source_file = tmp_path / "health_check_report.json"
    source_file.write_text(
        json.dumps({"data_quality_state": "PASS_STRICT", "issue_count": 0}),
        encoding="utf-8",
    )
    source = load_data_quality_ops_source(
        source_file,
        source_app_id="DATA-APP-1",
        source_type="health_check_report",
    )

    check = build_data_quality_ops_check(source, check_id="DQ-CHECK-001")

    assert check.check_status == CHECK_STATUS_PASS
    assert check.finding_code == "NO_IMMEDIATE_ISSUE"
    assert check.paper_only is True
    assert check.local_only is True
    assert check.read_only is True
    assert check.sidecar_only is True
    assert check.source_content_mutation_allowed is False
    assert check.trade_action_enabled is False
    assert check.real_execution_allowed is False
    assert validate_data_quality_ops_check(check) == []


def test_data_quality_ops_d3_builds_review_required_check_for_limited_health(tmp_path):
    source_file = tmp_path / "health_check_report.json"
    source_file.write_text(
        json.dumps({"data_quality_state": "PASS_LIMITED", "issue_count": 0}),
        encoding="utf-8",
    )
    source = load_data_quality_ops_source(
        source_file,
        source_app_id="DATA-APP-1",
        source_type="health_check_report",
    )

    check = build_data_quality_ops_check(source, check_id="DQ-CHECK-002")

    assert check.check_status == CHECK_STATUS_REVIEW_REQUIRED
    assert check.finding_code == "HEALTH_CHECK_LIMITED"
    assert check.ops_check_is_trade_instruction is False
    assert check.real_execution_allowed is False
    assert validate_data_quality_ops_check(check) == []


def test_data_quality_ops_d3_builds_fail_check_for_quarantine(tmp_path):
    source_file = tmp_path / "quarantine_report.json"
    source_file.write_text(
        json.dumps({"data_quality_state": "FAIL_QUARANTINE", "issue_count": 3}),
        encoding="utf-8",
    )
    source = load_data_quality_ops_source(
        source_file,
        source_app_id="DATA-APP-1",
        source_type="health_check_report",
    )

    check = build_data_quality_ops_check(source, check_id="DQ-CHECK-003")

    assert check.check_status == CHECK_STATUS_FAIL
    assert check.finding_code == "HEALTH_CHECK_FAIL"
    assert check.source_deletion_allowed is False
    assert check.source_overwrite_allowed is False
    assert validate_data_quality_ops_check(check) == []


def test_data_quality_ops_d3_builds_check_set_and_summary(tmp_path):
    first = tmp_path / "health_check_report.json"
    second = tmp_path / "archive_manifest.json"
    first.write_text(json.dumps({"data_quality_state": "PASS_STRICT"}), encoding="utf-8")
    second.write_text(json.dumps({"issue_count": 2}), encoding="utf-8")

    sources = [
        load_data_quality_ops_source(
            first,
            source_app_id="DATA-APP-1",
            source_type="health_check_report",
        ),
        load_data_quality_ops_source(
            second,
            source_app_id="REPORT-ARCHIVE-APP-1",
            source_type="archive_manifest",
        ),
    ]

    checks = build_data_quality_ops_checks(sources, check_set_id="DQ-CHECKSET")
    summary = summarize_data_quality_ops_checks(checks)

    assert len(checks) == 2
    assert checks[0].check_id == "DQ-CHECKSET-CHECK-0001"
    assert checks[1].check_id == "DQ-CHECKSET-CHECK-0002"
    assert summary["check_count"] == 2
    assert summary["by_status"][CHECK_STATUS_PASS] == 1
    assert summary["by_status"][CHECK_STATUS_REVIEW_REQUIRED] == 1
    assert summary["by_finding_code"]["ISSUES_PRESENT"] == 1
    assert summary["operator_review_required"] is True
    assert summary["trade_action_enabled"] is False
    assert summary["real_execution_allowed"] is False
