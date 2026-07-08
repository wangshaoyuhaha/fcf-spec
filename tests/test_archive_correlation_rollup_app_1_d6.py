import pytest

from sidecars.archive_correlation_rollup_app_1 import (
    CorrelationRollupCloseout,
    REQUIRED_COMPLETED_STAGES,
    build_final_closeout,
    validate_final_closeout,
)


def test_d6_builds_final_closeout():
    closeout = build_final_closeout(REQUIRED_COMPLETED_STAGES)

    assert closeout.source_app == "ARCHIVE-CORRELATION-ROLLUP-APP-1"
    assert closeout.completed_stages == ("D1", "D2", "D3", "D4", "D5", "D6")
    assert closeout.final_status == "completed_pending_operator_merge_review"
    assert closeout.operator_review_required is True
    assert closeout.core_mutation_allowed is False
    assert closeout.source_mutation_allowed is False
    assert closeout.real_execution_allowed is False
    assert closeout.tag_allowed is False
    assert closeout.release_allowed is False
    assert closeout.deploy_allowed is False


def test_d6_validates_final_closeout():
    closeout = build_final_closeout(REQUIRED_COMPLETED_STAGES)

    valid, issues = validate_final_closeout(closeout)

    assert valid is True
    assert issues == ()


def test_d6_rejects_missing_stage():
    with pytest.raises(ValueError, match="completed_stages_mismatch"):
        build_final_closeout(("D1", "D2", "D3", "D4", "D5"))


def test_d6_rejects_release_enabled_closeout():
    valid_closeout = build_final_closeout(REQUIRED_COMPLETED_STAGES)
    invalid_closeout = CorrelationRollupCloseout(
        source_app=valid_closeout.source_app,
        completed_stages=valid_closeout.completed_stages,
        final_status=valid_closeout.final_status,
        operator_review_required=valid_closeout.operator_review_required,
        core_mutation_allowed=valid_closeout.core_mutation_allowed,
        source_mutation_allowed=valid_closeout.source_mutation_allowed,
        real_execution_allowed=valid_closeout.real_execution_allowed,
        tag_allowed=valid_closeout.tag_allowed,
        release_allowed=True,
        deploy_allowed=valid_closeout.deploy_allowed,
        handoff_summary=valid_closeout.handoff_summary,
    )

    valid, issues = validate_final_closeout(invalid_closeout)

    assert valid is False
    assert "release_allowed_must_be_false" in issues


def test_d6_rejects_operator_review_bypass():
    valid_closeout = build_final_closeout(REQUIRED_COMPLETED_STAGES)
    invalid_closeout = CorrelationRollupCloseout(
        source_app=valid_closeout.source_app,
        completed_stages=valid_closeout.completed_stages,
        final_status=valid_closeout.final_status,
        operator_review_required=False,
        core_mutation_allowed=valid_closeout.core_mutation_allowed,
        source_mutation_allowed=valid_closeout.source_mutation_allowed,
        real_execution_allowed=valid_closeout.real_execution_allowed,
        tag_allowed=valid_closeout.tag_allowed,
        release_allowed=valid_closeout.release_allowed,
        deploy_allowed=valid_closeout.deploy_allowed,
        handoff_summary=valid_closeout.handoff_summary,
    )

    valid, issues = validate_final_closeout(invalid_closeout)

    assert valid is False
    assert "operator_review_not_required" in issues
