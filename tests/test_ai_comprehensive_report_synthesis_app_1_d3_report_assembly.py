from copy import deepcopy
from typing import Any

import pytest

from apps.ai_comprehensive_report_synthesis_app_1 import (
    REPORT_SCHEMA_VERSION,
    REQUIRED_ARTIFACT_TYPES,
    SECTION_ORDER,
    ContentItemViolation,
    ReportAssemblyViolation,
    SourcePayloadViolation,
    build_content_item,
    build_report_sections,
    build_source_manifest,
    build_source_payload,
    build_source_record,
    require_valid_report_sections,
    validate_content_item,
    validate_report_sections,
    validate_source_payload,
)


def _digest(index: int) -> str:
    return f"{index:064x}"


def _source(
    artifact_type: str,
    index: int,
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
        validation_state="VALIDATED",
        requirement_level="REQUIRED",
    )


def _sources() -> list[dict[str, Any]]:
    return [
        _source(artifact_type, index)
        for index, artifact_type in enumerate(
            REQUIRED_ARTIFACT_TYPES,
            start=1,
        )
    ]


def _item(index: int) -> dict[str, Any]:
    return build_content_item(
        item_id=f"item-{index:02d}",
        statement_type="REGISTERED_SOURCE_STATEMENT",
        statement_text=f"Preserved source statement {index}.",
        conclusion_state="PRESERVED",
        uncertainty_state="UNDETERMINED",
        risk_flags=[f"RISK_{index:02d}"],
        reason_codes=[f"REASON_{index:02d}"],
        evidence_refs=[f"EVIDENCE_{index:02d}"],
        counterevidence_refs=[f"COUNTER_{index:02d}"],
        alternative_explanation_refs=[f"ALT_{index:02d}"],
    )


def _manifest_and_payloads() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
]:
    sources = _sources()
    manifest = build_source_manifest(
        manifest_id="manifest-001",
        sources=sources,
    )

    payloads = [
        build_source_payload(
            source_record=source,
            items=[_item(index)],
        )
        for index, source in enumerate(
            manifest["sources"],
            start=1,
        )
    ]

    return manifest, payloads


def test_d3_content_item_preserves_registered_fields() -> None:
    item = _item(1)

    assert item["statement_text"] == "Preserved source statement 1."
    assert item["conclusion_state"] == "PRESERVED"
    assert item["uncertainty_state"] == "UNDETERMINED"
    assert item["risk_flags"] == ["RISK_01"]
    assert item["counterevidence_refs"] == ["COUNTER_01"]
    assert item["alternative_explanation_refs"] == ["ALT_01"]
    assert item["source_statement_preserved"] is True


def test_d3_content_item_rejects_unsorted_duplicate_flags() -> None:
    item = _item(1)
    item["risk_flags"] = ["RISK_B", "RISK_A", "RISK_A"]

    errors = validate_content_item(item)

    assert any(
        "risk_flags must be sorted and duplicate-free" in error
        for error in errors
    )

    with pytest.raises(ContentItemViolation):
        build_source_payload(
            source_record=_sources()[0],
            items=[item],
        )


def test_d3_source_payload_is_locked_to_source_record() -> None:
    source = _sources()[0]
    payload = build_source_payload(
        source_record=source,
        items=[_item(1)],
    )

    assert payload["artifact_id"] == source["artifact_id"]
    assert payload["artifact_type"] == source["artifact_type"]
    assert payload["artifact_version"] == source["artifact_version"]
    assert payload["locked_sha256"] == source["locked_sha256"]
    assert validate_source_payload(payload, source) == ()


def test_d3_source_payload_rejects_silent_version_change() -> None:
    source = _sources()[0]
    payload = build_source_payload(
        source_record=source,
        items=[_item(1)],
    )
    payload["artifact_version"] = "9.9.9"

    errors = validate_source_payload(payload, source)

    assert any("artifact_version" in error for error in errors)

    with pytest.raises(SourcePayloadViolation):
        build_source_payload(
            source_record=source,
            items=[],
        )


def test_d3_report_uses_registered_section_order() -> None:
    manifest, payloads = _manifest_and_payloads()

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )

    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["section_order"] == list(SECTION_ORDER)
    assert [
        section["section_id"]
        for section in report["sections"]
    ] == list(SECTION_ORDER)


def test_d3_report_preserves_source_statement_exactly() -> None:
    manifest, payloads = _manifest_and_payloads()

    expected_texts = {
        item["statement_text"]
        for payload in payloads
        for item in payload["items"]
    }

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )

    actual_texts = {
        entry["item"]["statement_text"]
        for section in report["sections"]
        if section["section_type"] == "PRESERVED_SOURCE_CONTENT"
        for entry in section["items"]
    }

    assert actual_texts == expected_texts


def test_d3_report_preserves_risk_and_uncertainty() -> None:
    manifest, payloads = _manifest_and_payloads()

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )

    risk_section = next(
        section
        for section in report["sections"]
        if section["section_id"] == "RISK_AND_UNCERTAINTY"
    )

    assert len(risk_section["items"]) == len(payloads)
    assert all(
        item["uncertainty_state"] == "UNDETERMINED"
        for item in risk_section["items"]
    )
    assert all(item["risk_flags"] for item in risk_section["items"])
    assert all(
        item["counterevidence_refs"]
        for item in risk_section["items"]
    )


def test_d3_report_preserves_safe_governance_states() -> None:
    manifest, payloads = _manifest_and_payloads()

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )

    assert report["causal_truth"] == "UNDETERMINED"
    assert report["probability"] == "NOT_ASSIGNED"
    assert report["winner"] == "NOT_SELECTED"
    assert report["operator_review_required"] is True
    assert report["live_model_invoked"] is False
    assert report["prompt_executed"] is False
    assert report["runtime_orchestrator_executed"] is False
    assert report["trade_action_generated"] is False
    assert report["real_execution"] is False


def test_d3_report_rejects_missing_required_payload() -> None:
    manifest, payloads = _manifest_and_payloads()
    payloads.pop()

    with pytest.raises(ReportAssemblyViolation) as exc_info:
        build_report_sections(
            manifest=manifest,
            payloads=payloads,
        )

    assert "required source payloads are missing" in str(exc_info.value)


def test_d3_report_rejects_unregistered_payload_source() -> None:
    manifest, payloads = _manifest_and_payloads()
    payload = deepcopy(payloads[0])
    payload["artifact_id"] = "unregistered-artifact"

    with pytest.raises(ReportAssemblyViolation) as exc_info:
        build_report_sections(
            manifest=manifest,
            payloads=[payload, *payloads[1:]],
        )

    assert "payload source is not registered" in str(exc_info.value)


def test_d3_report_is_deterministic_and_independent() -> None:
    manifest, payloads = _manifest_and_payloads()

    first = build_report_sections(
        manifest=manifest,
        payloads=reversed(payloads),
    )
    second = build_report_sections(
        manifest=manifest,
        payloads=reversed(payloads),
    )

    assert first == second
    assert first is not second
    assert first["sections"] is not second["sections"]


def test_d3_report_validator_rejects_winner_selection() -> None:
    manifest, payloads = _manifest_and_payloads()

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )
    report["winner"] = "SCENARIO_A"

    errors = validate_report_sections(report)

    assert any("winner must be 'NOT_SELECTED'" in error for error in errors)

    with pytest.raises(ReportAssemblyViolation):
        require_valid_report_sections(report)


def test_d3_registered_report_is_valid() -> None:
    manifest, payloads = _manifest_and_payloads()

    report = build_report_sections(
        manifest=manifest,
        payloads=payloads,
    )

    assert validate_report_sections(report) == ()
    assert require_valid_report_sections(report) is report