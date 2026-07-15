import json

import pytest

from apps.browser_product_console_integration_acceptance_app_1 import (
    INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY,
    REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS,
    BrowserConsoleIntegrationOperatorAcceptance,
    IntegrationValidationSummary,
    build_browser_console_integration_operator_acceptance,
)


def _passing_summary() -> IntegrationValidationSummary:
    return IntegrationValidationSummary(
        targeted_passed=446,
        targeted_skipped=3,
        full_passed=4210,
        full_skipped=3,
        run_all_checks_passed=True,
        generated_outputs_restored=True,
        exact_changed_files_verified=True,
        diff_check_passed=True,
    )


def test_d5_operator_acceptance_fixture_is_registered():
    fixture = next(
        item
        for item in INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY
        if item.fixture_id == "OPERATOR_ACCEPTANCE_FIXTURE"
    )

    assert fixture.source_kind == "STATIC_CONTRACT"
    assert fixture.read_only is True
    assert fixture.operator_review_required is True
    assert fixture.required_fields == (
        "acceptance_matrix",
        "validation_summary",
        "unresolved_items",
        "operator_review_required",
    )


def test_d5_passing_package_requires_operator_review():
    package = build_browser_console_integration_operator_acceptance(
        _passing_summary()
    )

    assert isinstance(
        package,
        BrowserConsoleIntegrationOperatorAcceptance,
    )
    assert package.status == "READY_FOR_OPERATOR_REVIEW"
    assert package.ready_for_operator_review is True
    assert package.operator_review_required is True
    assert package.read_only is True
    assert package.automatic_approval_allowed is False
    assert tuple(item[0] for item in package.matrix_results) == (
        REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
    )
    assert all(item[1] == "PASSED" for item in package.matrix_results)


def test_d5_operator_payload_is_deterministic_and_read_only():
    first = build_browser_console_integration_operator_acceptance(
        _passing_summary()
    )
    second = build_browser_console_integration_operator_acceptance(
        _passing_summary()
    )

    first_json = json.dumps(
        dict(first.to_payload()),
        ensure_ascii=True,
        sort_keys=True,
    )
    second_json = json.dumps(
        dict(second.to_payload()),
        ensure_ascii=True,
        sort_keys=True,
    )

    assert first_json == second_json
    assert '"status": "READY_FOR_OPERATOR_REVIEW"' in first_json
    assert '"automatic_approval_allowed": false' in first_json

    with pytest.raises(TypeError):
        first.to_payload()["status"] = "APPROVED"


def test_d5_unresolved_item_blocks_acceptance():
    package = build_browser_console_integration_operator_acceptance(
        _passing_summary(),
        unresolved_items=("manual-evidence-review-required",),
    )

    assert package.status == "BLOCKED"
    assert package.ready_for_operator_review is False
    assert package.unresolved_items == (
        "manual-evidence-review-required",
    )
    assert package.operator_review_required is True


def test_d5_matrix_failure_blocks_acceptance():
    package = build_browser_console_integration_operator_acceptance(
        _passing_summary(),
        blocked_matrix_ids=("RUNTIME_SECURITY",),
    )

    assert package.status == "BLOCKED"
    assert ("RUNTIME_SECURITY", "BLOCKED") in package.matrix_results


def test_d5_validation_failure_blocks_acceptance():
    summary = IntegrationValidationSummary(
        targeted_passed=446,
        targeted_skipped=3,
        full_passed=4210,
        full_skipped=3,
        run_all_checks_passed=False,
        generated_outputs_restored=True,
        exact_changed_files_verified=True,
        diff_check_passed=True,
    )
    package = build_browser_console_integration_operator_acceptance(summary)

    assert summary.ok is False
    assert package.status == "BLOCKED"


def test_d5_unknown_matrix_id_is_rejected():
    with pytest.raises(ValueError, match="unknown blocked matrix id"):
        build_browser_console_integration_operator_acceptance(
            _passing_summary(),
            blocked_matrix_ids=("UNKNOWN_MATRIX",),
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("targeted_passed", True),
        ("targeted_passed", -1),
        ("full_passed", 0),
        ("run_all_checks_passed", "yes"),
    ),
)
def test_d5_validation_summary_rejects_invalid_values(
    field_name,
    value,
):
    values = {
        "targeted_passed": 446,
        "targeted_skipped": 3,
        "full_passed": 4210,
        "full_skipped": 3,
        "run_all_checks_passed": True,
        "generated_outputs_restored": True,
        "exact_changed_files_verified": True,
        "diff_check_passed": True,
        field_name: value,
    }

    with pytest.raises(ValueError):
        IntegrationValidationSummary(**values)


def test_d5_permanent_restrictions_are_explicit():
    package = build_browser_console_integration_operator_acceptance(
        _passing_summary()
    )

    for restriction in (
        "p1-p47-frozen",
        "no-p48",
        "paper-only",
        "loopback-only",
        "registered-artifact-only",
        "operator-review-required",
        "deterministic-engine-authority",
        "registered-evidence-authority",
        "ai-advisory-only",
        "no-order-path",
        "no-real-execution",
        "no-automatic-approval",
        "no-automatic-promotion",
        "no-automatic-learning-activation",
        "no-tag",
        "no-release",
        "no-deployment",
    ):
        assert restriction in package.permanent_restrictions
