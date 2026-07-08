from sidecars.archive_correlation_rollup_app_1 import (
    CorrelationRollupItem,
    build_rollup_index,
    validate_rollup_item,
)


def test_d1_rollup_item_accepts_valid_read_only_item():
    item = CorrelationRollupItem(
        correlation_id="CORR-ARCHIVE-ROLLUP-D1-001",
        artifact_path="FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        artifact_type="final_current_state",
        source_app="UI-RISK-FLAG-VISIBILITY-APP-1",
        source_phase="FINAL",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
    )

    valid, issues = validate_rollup_item(item)

    assert valid is True
    assert issues == ()


def test_d1_rollup_item_rejects_missing_correlation_id():
    item = CorrelationRollupItem(
        correlation_id="",
        artifact_path="FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        artifact_type="final_current_state",
        source_app="UI-RISK-FLAG-VISIBILITY-APP-1",
        source_phase="FINAL",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
    )

    valid, issues = validate_rollup_item(item)

    assert valid is False
    assert "missing_or_empty:correlation_id" in issues


def test_d1_rollup_index_groups_by_correlation_id():
    first = CorrelationRollupItem(
        correlation_id="CORR-ARCHIVE-ROLLUP-D1-001",
        artifact_path="FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        artifact_type="final_current_state",
        source_app="UI-RISK-FLAG-VISIBILITY-APP-1",
        source_phase="FINAL",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
    )
    second = CorrelationRollupItem(
        correlation_id="CORR-ARCHIVE-ROLLUP-D1-001",
        artifact_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        artifact_type="control_center",
        source_app="CONTROL-CENTER-MAINTENANCE-APP-2",
        source_phase="FINAL",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
    )

    index = build_rollup_index([first, second])

    assert tuple(index.keys()) == ("CORR-ARCHIVE-ROLLUP-D1-001",)
    assert index["CORR-ARCHIVE-ROLLUP-D1-001"] == (first, second)
