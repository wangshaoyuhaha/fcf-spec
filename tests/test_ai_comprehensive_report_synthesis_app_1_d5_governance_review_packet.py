from copy import deepcopy
from typing import Any

import pytest

from apps.ai_comprehensive_report_synthesis_app_1 import (
    REQUIRED_ARTIFACT_TYPES,
    REVIEW_CHECKLIST_ITEMS,
    GovernanceReviewPacketViolation,
    build_content_item,
    build_governance_assessment,
    build_governance_review_packet,
    build_report_sections,
    build_source_manifest,
    build_source_payload,
    build_source_record,
    require_valid_governance_review_packet,
    validate_governance_review_packet,
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
        correlation_id="corr-review-001",
        research_run_id="research-run-001",
        source_stage_id=f"SOURCE-D{index}",
        source_path=f"artifacts/source_{index:02d}.json",
        locked_sha256=_digest(index),
        source_conclusion_state="PRESERVED",
        validation_state="VALIDATED",
        requirement_level="REQUIRED",
    )


def _item(
    artifact_type: str,
    index: int,
    *,
    counterevidence_refs: list[str] | None = None,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    return build_content_item(
        item_id=f"item-{index:02d}",
        statement_type=f"{artifact_type}_STATEMENT",
        statement_text=f"Preserved statement for {artifact_type}.",
        conclusion_state="PRESERVED",
        uncertainty_state="NOT_APPLICABLE",
        evidence_refs=[f"EVIDENCE_{index:02d}"],
        reason_codes=[f"REASON_{index:02d}"],
        counterevidence_refs=counterevidence_refs or [],
        risk_flags=risk_flags or [],
    )


def _artifacts(
    *,
    counterevidence: bool = False,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    sources = [
        _source(artifact_type, index)
        for index, artifact_type in enumerate(
            REQUIRED_ARTIFACT_TYPES,
            start=1,
        )
    ]

    manifest = build_source_manifest(
        manifest_id="manifest-review-001",
        sources=sources,
    )

    payloads = []

    for index, source in enumerate(
        manifest["sources"],
        start=1,
    ):
        artifact_type = source["artifact_type"]

        items = [
            _item(
                artifact_type,
                index,
                counterevidence_refs=(
                    ["COUNTEREVIDENCE_01"]
                    if (
                        counterevidence
                        and artifact_type
                        == "CONTRARIAN_CHALLENGE"
                    )
                    else []
                ),
            )
        ]

        if artifact_type == "SCENARIO_SIMULATION":
            items.append(
                build_content_item(
                    item_id="scenario-item-02",
                    statement_type="SCENARIO_SIMULATION_STATEMENT",
                    statement_text="Preserved alternative scenario.",
                    conclusion_state="PRESERVED",
                    uncertainty_state="NOT_APPLICABLE",
                    evidence_refs=["SCENARIO_EVIDENCE_02"],
                    reason_codes=["SCENARIO_REASON_02"],
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

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    return manifest, report, assessment


def _blocked_artifacts() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    manifest, report, _ = _artifacts()

    report["source_reference_index"][0][
        "artifact_version"
    ] = "9.9.9"

    source_section = next(
        section
        for section in report["sections"]
        if section["section_id"] == "SOURCE_REFERENCE_INDEX"
    )
    source_section["items"][0][
        "artifact_version"
    ] = "9.9.9"

    assessment = build_governance_assessment(
        manifest=manifest,
        report=report,
    )

    return manifest, report, assessment


def test_d5_packet_preserves_all_upstream_artifacts() -> None:
    manifest, report, assessment = _artifacts()
    original_manifest = deepcopy(manifest)
    original_report = deepcopy(report)
    original_assessment = deepcopy(assessment)

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert packet["source_manifest"] == manifest
    assert packet["report"] == report
    assert packet["governance_assessment"] == assessment
    assert packet["source_manifest"] is not manifest
    assert packet["report"] is not report
    assert packet["governance_assessment"] is not assessment
    assert manifest == original_manifest
    assert report == original_report
    assert assessment == original_assessment


def test_d5_ready_packet_requires_operator_review() -> None:
    manifest, report, assessment = _artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert packet["status"] == (
        "REVIEW_PACKET_READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["operator_review_required"] is True
    assert packet["operator_decision"] == "PENDING"
    assert packet["archive_handoff_allowed"] is False
    assert packet["manual_archive_only"] is True


def test_d5_blocked_packet_preserves_blocking_state() -> None:
    manifest, report, assessment = _blocked_artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert packet["status"] == "REVIEW_PACKET_BLOCKED"
    assert packet["issue_summary"]["blocking_issue_count"] >= 1
    assert packet["archive_handoff_allowed"] is False


def test_d5_issue_summary_matches_assessment() -> None:
    manifest, report, assessment = _artifacts(
        counterevidence=True,
    )

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    summary = packet["issue_summary"]

    assert summary["issue_count"] == assessment["issue_count"]
    assert summary["blocking_issue_count"] == assessment[
        "blocking_issue_count"
    ]
    assert summary["unresolved_issue_count"] == assessment[
        "unresolved_issue_count"
    ]
    assert summary["issue_code_counts"] == assessment[
        "issue_code_counts"
    ]


def test_d5_operator_queue_maps_every_issue() -> None:
    manifest, report, assessment = _artifacts(
        counterevidence=True,
    )

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    queue = packet["operator_action_queue"]

    assert len(queue) == assessment["issue_count"]
    assert [action["issue_id"] for action in queue] == [
        issue["issue_id"]
        for issue in assessment["issues"]
    ]
    assert all(action["status"] == "PENDING" for action in queue)
    assert all(
        action["operator_decision"] == "PENDING"
        for action in queue
    )
    assert all(
        action["automatic_resolution_allowed"] is False
        for action in queue
    )


def test_d5_empty_issue_register_creates_empty_queue() -> None:
    manifest, report, assessment = _artifacts()

    assert assessment["issue_count"] == 0

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert packet["operator_action_queue"] == []


def test_d5_review_checklist_uses_registered_order() -> None:
    manifest, report, assessment = _artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert [
        check["check_code"]
        for check in packet["review_checklist"]
    ] == list(REVIEW_CHECKLIST_ITEMS)

    assert all(
        check["status"] == "PENDING"
        for check in packet["review_checklist"]
    )

    assert all(
        check["automatic_confirmation_allowed"] is False
        for check in packet["review_checklist"]
    )


def test_d5_source_and_section_inventories_are_preserved() -> None:
    manifest, report, assessment = _artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert packet["source_inventory"] == manifest["sources"]

    assert [
        item["section_id"]
        for item in packet["section_inventory"]
    ] == [
        section["section_id"]
        for section in report["sections"]
    ]

    assert [
        item["item_count"]
        for item in packet["section_inventory"]
    ] == [
        len(section["items"])
        for section in report["sections"]
    ]


def test_d5_packet_preserves_safe_interpretation_states() -> None:
    manifest, report, assessment = _artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert packet["causal_truth"] == "UNDETERMINED"
    assert packet["probability"] == "NOT_ASSIGNED"
    assert packet["winner"] == "NOT_SELECTED"
    assert packet["live_model_invoked"] is False
    assert packet["prompt_executed"] is False
    assert packet["runtime_orchestrator_executed"] is False
    assert packet["automatic_archive_executed"] is False
    assert packet["trade_action_generated"] is False
    assert packet["real_execution"] is False


def test_d5_packet_is_deterministic() -> None:
    manifest, report, assessment = _artifacts(
        counterevidence=True,
    )

    first = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )
    second = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert first == second
    assert first is not second
    assert first["operator_action_queue"] is not second[
        "operator_action_queue"
    ]


def test_d5_validator_rejects_automatic_resolution() -> None:
    manifest, report, assessment = _artifacts(
        counterevidence=True,
    )

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    packet["operator_action_queue"][0][
        "automatic_resolution_allowed"
    ] = True

    errors = validate_governance_review_packet(packet)

    assert any(
        "automatic_resolution_allowed must be False" in error
        for error in errors
    )

    with pytest.raises(GovernanceReviewPacketViolation):
        require_valid_governance_review_packet(packet)


def test_d5_validator_rejects_source_conclusion_replacement() -> None:
    manifest, report, assessment = _artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    packet["report"]["winner"] = "SCENARIO_A"

    errors = validate_governance_review_packet(packet)

    assert any(
        "report.winner must be 'NOT_SELECTED'" in error
        for error in errors
    )


def test_d5_validator_rejects_identity_mismatch() -> None:
    manifest, report, assessment = _artifacts()

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    packet["correlation_id"] = "corr-other"

    errors = validate_governance_review_packet(packet)

    assert any(
        "correlation_id is not aligned" in error
        for error in errors
    )


def test_d5_registered_packet_is_valid() -> None:
    manifest, report, assessment = _artifacts(
        counterevidence=True,
    )

    packet = build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )

    assert validate_governance_review_packet(packet) == ()
    assert (
        require_valid_governance_review_packet(packet)
        is packet
    )