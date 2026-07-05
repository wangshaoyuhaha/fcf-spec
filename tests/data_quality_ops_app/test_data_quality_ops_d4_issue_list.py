import json

from data_quality_ops_app import (
    CHECK_STATUS_FAIL,
    CHECK_STATUS_PASS,
    CHECK_STATUS_REVIEW_REQUIRED,
    ISSUE_STATUS_OPEN,
    build_data_quality_issue_from_check,
    build_data_quality_issue_list,
    build_data_quality_ops_check,
    build_data_quality_ops_checks,
    load_data_quality_ops_source,
    summarize_data_quality_issue_list,
    validate_data_quality_issue,
    validate_data_quality_issue_list,
)


def _build_check(tmp_path, payload, *, check_id="DQ-CHECK"):
    source_file = tmp_path / f"{check_id}.json"
    source_file.write_text(json.dumps(payload), encoding="utf-8")
    source = load_data_quality_ops_source(
        source_file,
        source_app_id="DATA-APP-1",
        source_type="health_check_report",
    )
    return build_data_quality_ops_check(source, check_id=check_id)


def test_data_quality_ops_d4_skips_pass_check(tmp_path):
    check = _build_check(
        tmp_path,
        {"data_quality_state": "PASS_STRICT", "issue_count": 0},
        check_id="DQ-PASS",
    )

    assert check.check_status == CHECK_STATUS_PASS
    issue = build_data_quality_issue_from_check(check, issue_id="ISSUE-PASS")
    assert issue is None


def test_data_quality_ops_d4_builds_review_required_issue(tmp_path):
    check = _build_check(
        tmp_path,
        {"data_quality_state": "PASS_LIMITED"},
        check_id="DQ-LIMITED",
    )

    assert check.check_status == CHECK_STATUS_REVIEW_REQUIRED
    issue = build_data_quality_issue_from_check(check, issue_id="ISSUE-LIMITED")

    assert issue is not None
    assert issue.issue_id == "ISSUE-LIMITED"
    assert issue.issue_status == ISSUE_STATUS_OPEN
    assert issue.issue_code == "HEALTH_CHECK_LIMITED"
    assert issue.paper_only is True
    assert issue.local_only is True
    assert issue.read_only is True
    assert issue.sidecar_only is True
    assert issue.source_content_mutation_allowed is False
    assert issue.repair_queue_is_execution_instruction is False
    assert issue.trade_action_enabled is False
    assert issue.real_execution_allowed is False
    assert validate_data_quality_issue(issue) == []


def test_data_quality_ops_d4_builds_error_issue_from_fail_check(tmp_path):
    check = _build_check(
        tmp_path,
        {"data_quality_state": "FAIL_QUARANTINE"},
        check_id="DQ-FAIL",
    )

    assert check.check_status == CHECK_STATUS_FAIL
    issue = build_data_quality_issue_from_check(check, issue_id="ISSUE-FAIL")

    assert issue is not None
    assert issue.severity == "ERROR"
    assert issue.issue_code == "HEALTH_CHECK_FAIL"
    assert issue.source_deletion_allowed is False
    assert issue.source_overwrite_allowed is False
    assert validate_data_quality_issue(issue) == []


def test_data_quality_ops_d4_builds_issue_list_and_summary(tmp_path):
    first = tmp_path / "pass.json"
    second = tmp_path / "limited.json"
    third = tmp_path / "fail.json"
    first.write_text(json.dumps({"data_quality_state": "PASS_STRICT"}), encoding="utf-8")
    second.write_text(json.dumps({"data_quality_state": "PASS_LIMITED"}), encoding="utf-8")
    third.write_text(json.dumps({"data_quality_state": "FAIL_QUARANTINE"}), encoding="utf-8")

    sources = [
        load_data_quality_ops_source(first, source_app_id="DATA-APP-1", source_type="health_check_report"),
        load_data_quality_ops_source(second, source_app_id="DATA-APP-1", source_type="health_check_report"),
        load_data_quality_ops_source(third, source_app_id="DATA-APP-1", source_type="health_check_report"),
    ]
    checks = build_data_quality_ops_checks(sources, check_set_id="DQ-D4")
    issue_list = build_data_quality_issue_list(
        issue_list_id="DQ-D4-ISSUES",
        checks=checks,
    )
    summary = summarize_data_quality_issue_list(issue_list)

    assert len(issue_list.issues) == 2
    assert issue_list.issue_list_id == "DQ-D4-ISSUES"
    assert issue_list.paper_only is True
    assert issue_list.local_only is True
    assert issue_list.read_only is True
    assert issue_list.sidecar_only is True
    assert issue_list.trade_action_enabled is False
    assert issue_list.real_execution_allowed is False
    assert summary["issue_count"] == 2
    assert summary["by_issue_code"]["HEALTH_CHECK_LIMITED"] == 1
    assert summary["by_issue_code"]["HEALTH_CHECK_FAIL"] == 1
    assert summary["operator_review_required"] is True
    assert validate_data_quality_issue_list(issue_list) == []
