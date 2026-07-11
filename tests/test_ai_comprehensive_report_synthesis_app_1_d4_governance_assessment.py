from copy import deepcopy
from typing import Any

import pytest

from apps.ai_comprehensive_report_synthesis_app_1 import (
    REQUIRED_ARTIFACT_TYPES,
    GovernanceAssessmentViolation,
    build_content_item,
    build_governance_assessment,
    build_report_sections,
    build_source_manifest,
    build_source_payload,
    build_source_record,
    require_valid_governance_assessment,
    validate_governance_assessment,
)


def _digest(index: int) -> str:
    return f"{index:064x}"


def _source(
    artifact_type: str,
    index: int,
    *,
    validation_state: str = "VALIDATED",
) -> dict[str, Any]:
    return build_source_record(
        artifact_id=f"artifact-{index:02d}",
        artifact_type=artifact_type,
        artifact_version=f"1.0.{index}",
        correlation_id="corr-report-001",
        research_run_id="research-run-001",
        source_stage_id=f"SOURCE-D{index}",
        source_path=f"artifacts/source_{index:02d}.json",
        locked_sha256=_digest(index),
        source_conclusion_state="PRESERVED",
        validation_state=validation_state,
        requirement_level="REQUIRED",
    )


def _item(
    artifact_type: str,
    index: int,
    *,
    statement_text: str | None = None,
    conclusion_state: str = "PRESERVED",
    evidence_refs: list[str] | None = None,
    risk_flags: list[str] | None = None,
    reason_codes: list[str] | None = None,
    counterevidence_refs: list[str] | None = None,
    alternative_explanation_refs: list[str] | None = None,
) -> dict[str, Any]:
    if evidence_refs is None:
        evidence_refs = [f"EVIDENCE_{index:02d}"]

    if risk_flags is None:
        risk_flags = []

    if reason_codes is None:
        reason_codes = [f"REASON_{index:02d}"]

    if counterevidence_refs is None:
        counterevidence_refs = []

    if alternative_explanation_refs is None:
        alternative_explanation_refs = []

    return build_content_item(
        item_id=f"item-{index:02d}",
        statement_type=f"{artifact_type}_STATEMENT",
        statement_text=(
            statement_text
            if statement_text is not None
            else f"Preserved statement for {artifact_type}."
        ),
        conclusion_state=conclusion_state,
        uncertainty_state="UNDETERMINED",
        risk_flags=risk_flags,
        reason_codes=reason_codes,
        evidence_refs=evidence_refs,
        counterevidence_refs=counterevidence_refs,
        alternative_explanation_refs=alternative_explanation_refs,
    )


def _manifest_report(
    *,
    validation_overrides: dict[str, str] | None = None,
    item_overrides: dict[str, dict[str, Any]] | None = None,
    add_second_scenario: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validation_overrides = validation_overrides or {}
    item_overrides = item_overrides or {}

    sources = [
        _source(
            artifact_type,
            index,
            validation_state=validation_overrides.get(
                artifact_type,
                "VALIDATED",
            ),
        )
        for index, artifact_type in enumerate(
            REQUIRED_ARTIFACT_TYPES,
            start=1,
        )
    ]

    manifest = build_source_manifest(
        manifest_id="manifest-001",
        sources=sources,
    )

    payloads = []

    for index, source in enumerate(
        manifest["sources"],
        start=1,
    ):
        artifact_type = source["artifact_type"]
        override = item_overrides.get(artifact_type, {})

        items = [
            _item(
                artifact_type,
                index,
                **override,
            )
        ]

        if (
            artifact_type == "SCENARIO_SIMULATION"
            and add_second_scenario
        ):
            items.append(
                build_content_item(
                    item_id="item-scenario-02",
                    statement_type="SCENARIO_SIMULATION_STATEMENT",
                    statement_text="Preserved alternative scenario.",
                    conclusion_state="PRESERVED",
                    uncertainty_state="UNDETERMINED",
                    evidence_refs=["EVIDENCE_SCENARIO_02"],
                    reason_codes=["REASON_SCENARIO_02"],
                )
            )

        payloads.append(
            build_source_payload(
                source_record=source,
                items=items,
            )
        )

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )

    return manifest, report


def _codes(
    assessment: dict[str, Any],
) -> set[str]:
    return {
        issue["issue_code"]
        for issue in assessment["issues"]
    }


def test_d4_assessment_is_valid_and_preserves_sources() -> None:
    manifest, report = _manifest_report()
    original_manifest = deepcopy(manifest)
    original_report = deepcopy(report)

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert validate_governance_assessment(assessment) == ()
    assert (
        require_valid_governance_assessment(assessment)
        is assessment
    )
    assert assessment["source_artifacts_preserved"] is True
    assert assessment["original_conclusions_preserved"] is True
    assert assessment["operator_review_required"] is True
    assert assessment["operator_decision"] == "PENDING"
    assert assessment["report_mutated"] is False
    assert manifest == original_manifest
    assert report == original_report


def test_d4_assessment_preserves_safe_governance_states() -> None:
    manifest, report = _manifest_report()

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert assessment["causal_truth"] == "UNDETERMINED"
    assert assessment["probability"] == "NOT_ASSIGNED"
    assert assessment["winner"] == "NOT_SELECTED"
    assert assessment["live_model_invoked"] is False
    assert assessment["prompt_executed"] is False
    assert assessment["runtime_orchestrator_executed"] is False
    assert assessment["automatic_archive_executed"] is False
    assert assessment["trade_action_generated"] is False
    assert assessment["real_execution"] is False


def test_d4_detects_manifest_identity_mismatch() -> None:
    manifest, report = _manifest_report()
    report["manifest_id"] = "manifest-other"

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "REPORT_MANIFEST_ID_MISMATCH" in _codes(assessment)
    assert assessment["status"] == "ASSESSMENT_BLOCKED"


def test_d4_detects_source_version_drift() -> None:
    manifest, report = _manifest_report()
    artifact_id = manifest["sources"][0]["artifact_id"]

    report["source_reference_index"][0][
        "artifact_version"
    ] = "9.9.9"

    source_section = next(
        section
        for section in report["sections"]
        if section["section_id"] == "SOURCE_REFERENCE_INDEX"
    )
    source_section["items"][0]["artifact_version"] = "9.9.9"

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "SOURCE_VERSION_DRIFT" in _codes(assessment)
    assert assessment["blocking_issue_count"] >= 1
    assert artifact_id in {
        artifact_id
        for issue in assessment["issues"]
        for artifact_id in issue["artifact_ids"]
    }


def test_d4_detects_cross_artifact_conclusion_conflict() -> None:
    shared_text = "The same preserved market statement."

    manifest, report = _manifest_report(
        item_overrides={
            "MARKET_NARRATIVE_CONTEXT": {
                "statement_text": shared_text,
                "conclusion_state": "PRESERVED",
            },
            "CAUSAL_REASONING_CHAIN": {
                "statement_text": shared_text,
                "conclusion_state": "REVIEW_REQUIRED",
            },
        }
    )

    for section in report["sections"]:
        if section["section_id"] == "CAUSAL_REASONING":
            section["items"][0]["item"][
                "statement_type"
            ] = "SHARED_STATEMENT"

        if section["section_id"] == "MARKET_NARRATIVE":
            section["items"][0]["item"][
                "statement_type"
            ] = "SHARED_STATEMENT"

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert (
        "CROSS_ARTIFACT_CONCLUSION_CONFLICT"
        in _codes(assessment)
    )


def test_d4_detects_causal_evidence_gap() -> None:
    manifest, report = _manifest_report(
        item_overrides={
            "CAUSAL_REASONING_CHAIN": {
                "evidence_refs": [],
            }
        }
    )

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "CAUSAL_EVIDENCE_GAP" in _codes(assessment)


def test_d4_detects_scenario_coverage_gap() -> None:
    manifest, report = _manifest_report(
        add_second_scenario=False,
    )

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "SCENARIO_COVERAGE_GAP" in _codes(assessment)


def test_d4_detects_evaluation_drift_marker() -> None:
    manifest, report = _manifest_report(
        item_overrides={
            "AI_EVALUATION_EVIDENCE": {
                "risk_flags": ["MODEL_DRIFT"],
            }
        }
    )

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "EVALUATION_DRIFT_OPEN" in _codes(assessment)


def test_d4_detects_validation_baseline_review_state() -> None:
    manifest, report = _manifest_report(
        validation_overrides={
            "VALIDATION_BASELINE": "REVIEW_REQUIRED",
        }
    )

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "VALIDATION_BASELINE_GAP" in _codes(assessment)
    assert (
        "SOURCE_VALIDATION_REVIEW_REQUIRED"
        in _codes(assessment)
    )
    assert assessment["status"] == "ASSESSMENT_BLOCKED"


def test_d4_detects_counterevidence_and_alternative_explanation() -> None:
    manifest, report = _manifest_report(
        item_overrides={
            "CONTRARIAN_CHALLENGE": {
                "counterevidence_refs": ["COUNTER_01"],
                "alternative_explanation_refs": ["ALT_01"],
            }
        }
    )

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert "UNRESOLVED_COUNTEREVIDENCE" in _codes(assessment)
    assert "ALTERNATIVE_EXPLANATION_OPEN" in _codes(assessment)


def test_d4_detects_risk_visibility_gap() -> None:
    manifest, report = _manifest_report(
        item_overrides={
            "MARKET_NARRATIVE_CONTEXT": {
                "risk_flags": ["RISK_VISIBLE"],
            }
        }
    )

    risk_section = next(
        section
        for section in report["sections"]
        if section["section_id"] == "RISK_AND_UNCERTAINTY"
    )

    target = next(
        item
        for item in risk_section["items"]
        if item["artifact_type"] == "MARKET_NARRATIVE_CONTEXT"
    )
    target["risk_flags"] = []

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert (
        "RISK_AND_UNCERTAINTY_VISIBILITY_GAP"
        in _codes(assessment)
    )
    assert assessment["status"] == "ASSESSMENT_BLOCKED"


def test_d4_assessment_is_deterministic() -> None:
    manifest, report = _manifest_report(
        item_overrides={
            "CONTRARIAN_CHALLENGE": {
                "counterevidence_refs": ["COUNTER_02"],
                "risk_flags": ["RISK_02"],
            }
        }
    )

    first = build_governance_assessment(
        manifest=manifest,
        report=report,
    )
    second = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    assert first == second
    assert first is not second
    assert first["issues"] is not second["issues"]
    assert [
        issue["issue_id"]
        for issue in first["issues"]
    ] == [
        f"GOV-{index:04d}"
        for index in range(1, first["issue_count"] + 1)
    ]


def test_d4_validator_rejects_automatic_resolution() -> None:
    manifest, report = _manifest_report(
        item_overrides={
            "CONTRARIAN_CHALLENGE": {
                "counterevidence_refs": ["COUNTER_03"],
            }
        }
    )

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )
    assessment["issues"][0][
        "automatic_resolution_allowed"
    ] = True

    errors = validate_governance_assessment(assessment)

    assert any(
        "automatic_resolution_allowed must be False" in error
        for error in errors
    )

    with pytest.raises(GovernanceAssessmentViolation):
        require_valid_governance_assessment(assessment)