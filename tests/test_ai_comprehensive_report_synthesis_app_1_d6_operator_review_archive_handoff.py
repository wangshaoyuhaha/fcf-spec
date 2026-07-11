from copy import deepcopy
from typing import Any

import pytest

from apps.ai_comprehensive_report_synthesis_app_1 import (
    OPERATOR_REVIEW_DECISIONS,
    REQUIRED_ARTIFACT_TYPES,
    ManualArchiveHandoffViolation,
    OperatorReviewReceiptViolation,
    build_content_item,
    build_d6_closeout_record,
    build_governance_assessment,
    build_governance_review_packet,
    build_manual_archive_handoff,
    build_operator_review_receipt,
    build_report_sections,
    build_source_manifest,
    build_source_payload,
    build_source_record,
    require_valid_d6_closeout_record,
    require_valid_manual_archive_handoff,
    require_valid_operator_review_receipt,
    validate_d6_closeout_record,
    validate_manual_archive_handoff,
    validate_operator_review_receipt,
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
        correlation_id="corr-d6-001",
        research_run_id="research-run-d6-001",
        source_stage_id=f"SOURCE-D{index}",
        source_path=f"artifacts/source_{index:02d}.json",
        locked_sha256=_digest(index),
        source_conclusion_state="PRESERVED",
        validation_state="VALIDATED",
        requirement_level="REQUIRED",
    )


def _content_item(
    artifact_type: str,
    index: int,
) -> dict[str, Any]:
    return build_content_item(
        item_id=f"item-{index:02d}",
        statement_type=f"{artifact_type}_STATEMENT",
        statement_text=f"Preserved statement for {artifact_type}.",
        conclusion_state="PRESERVED",
        uncertainty_state="NOT_APPLICABLE",
        evidence_refs=[f"EVIDENCE_{index:02d}"],
        reason_codes=[f"REASON_{index:02d}"],
    )


def _packet(
    *,
    with_counterevidence: bool = False,
) -> dict[str, Any]:
    sources = [
        _source(artifact_type, index)
        for index, artifact_type in enumerate(
            REQUIRED_ARTIFACT_TYPES,
            start=1,
        )
    ]

    manifest = build_source_manifest(
        manifest_id="manifest-d6-001",
        sources=sources,
    )

    payloads = []

    for index, source in enumerate(
        manifest["sources"],
        start=1,
    ):
        artifact_type = source["artifact_type"]

        item = _content_item(artifact_type, index)

        if (
            with_counterevidence
            and artifact_type == "CONTRARIAN_CHALLENGE"
        ):
            item = build_content_item(
                item_id=f"item-{index:02d}",
                statement_type=f"{artifact_type}_STATEMENT",
                statement_text=(
                    f"Preserved statement for {artifact_type}."
                ),
                conclusion_state="PRESERVED",
                uncertainty_state="NOT_APPLICABLE",
                evidence_refs=[f"EVIDENCE_{index:02d}"],
                reason_codes=[f"REASON_{index:02d}"],
                counterevidence_refs=["COUNTEREVIDENCE_01"],
            )

        items = [item]

        if artifact_type == "SCENARIO_SIMULATION":
            items.append(
                build_content_item(
                    item_id="scenario-item-02",
                    statement_type=(
                        "SCENARIO_SIMULATION_STATEMENT"
                    ),
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

    return build_governance_review_packet(
        manifest=manifest,
        report=report,
        assessment=assessment,
    )


def _confirmed_checks(
    packet: dict[str, Any],
) -> dict[str, str]:
    return {
        check["check_code"]: "CONFIRMED"
        for check in packet["review_checklist"]
    }


def _reviewed_actions(
    packet: dict[str, Any],
) -> dict[str, str]:
    return {
        action["action_id"]: "REVIEWED"
        for action in packet["operator_action_queue"]
    }


def _approved_receipt(
    packet: dict[str, Any],
) -> dict[str, Any]:
    return build_operator_review_receipt(
        packet=packet,
        operator_id="operator-001",
        operator_decision=(
            "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        ),
        review_note=(
            "Registered source evidence and governance fields reviewed."
        ),
        checklist_results=_confirmed_checks(packet),
        action_results=_reviewed_actions(packet),
    )


def test_d6_registered_operator_decisions_are_explicit() -> None:
    assert OPERATOR_REVIEW_DECISIONS == (
        "PENDING",
        "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF",
        "RETURN_FOR_REVISION",
        "REJECTED",
    )


def test_d6_default_receipt_remains_pending() -> None:
    packet = _packet()

    receipt = build_operator_review_receipt(packet=packet)

    assert receipt["status"] == "OPERATOR_REVIEW_PENDING"
    assert receipt["operator_id"] == "UNASSIGNED"
    assert receipt["operator_decision"] == "PENDING"
    assert receipt["manual_archive_handoff_allowed"] is False
    assert receipt["automatic_approval"] is False
    assert all(
        check["status"] == "PENDING"
        for check in receipt["checklist_results"]
    )


def test_d6_pending_receipt_is_valid() -> None:
    packet = _packet()
    receipt = build_operator_review_receipt(packet=packet)

    assert validate_operator_review_receipt(
        receipt,
        packet,
    ) == ()

    assert (
        require_valid_operator_review_receipt(
            receipt,
            packet,
        )
        is receipt
    )


def test_d6_approval_requires_identified_operator() -> None:
    packet = _packet()

    with pytest.raises(OperatorReviewReceiptViolation):
        build_operator_review_receipt(
            packet=packet,
            operator_decision=(
                "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
            ),
            review_note="Reviewed.",
            checklist_results=_confirmed_checks(packet),
            action_results=_reviewed_actions(packet),
        )


def test_d6_approval_requires_review_note() -> None:
    packet = _packet()

    with pytest.raises(OperatorReviewReceiptViolation):
        build_operator_review_receipt(
            packet=packet,
            operator_id="operator-001",
            operator_decision=(
                "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
            ),
            checklist_results=_confirmed_checks(packet),
            action_results=_reviewed_actions(packet),
        )


def test_d6_approval_requires_all_checklist_confirmations() -> None:
    packet = _packet()
    checks = _confirmed_checks(packet)
    first_code = next(iter(checks))
    checks[first_code] = "PENDING"

    with pytest.raises(OperatorReviewReceiptViolation):
        build_operator_review_receipt(
            packet=packet,
            operator_id="operator-001",
            operator_decision=(
                "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
            ),
            review_note="Reviewed.",
            checklist_results=checks,
            action_results=_reviewed_actions(packet),
        )


def test_d6_approval_requires_all_actions_reviewed() -> None:
    packet = _packet(with_counterevidence=True)

    assert packet["operator_action_queue"]

    actions = _reviewed_actions(packet)
    first_action = next(iter(actions))
    actions[first_action] = "PENDING"

    with pytest.raises(OperatorReviewReceiptViolation):
        build_operator_review_receipt(
            packet=packet,
            operator_id="operator-001",
            operator_decision=(
                "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
            ),
            review_note="Reviewed.",
            checklist_results=_confirmed_checks(packet),
            action_results=actions,
        )


def test_d6_explicit_approval_receipt_is_valid() -> None:
    packet = _packet(with_counterevidence=True)
    receipt = _approved_receipt(packet)

    assert receipt["status"] == "OPERATOR_REVIEW_APPROVED"
    assert receipt["all_checklist_items_confirmed"] is True
    assert receipt["all_operator_actions_reviewed"] is True
    assert receipt["manual_archive_handoff_allowed"] is True
    assert validate_operator_review_receipt(
        receipt,
        packet,
    ) == ()


def test_d6_return_for_revision_never_allows_handoff() -> None:
    packet = _packet()

    receipt = build_operator_review_receipt(
        packet=packet,
        operator_id="operator-001",
        operator_decision="RETURN_FOR_REVISION",
        review_note="Additional source review required.",
    )

    assert receipt["status"] == (
        "OPERATOR_REVIEW_RETURNED_FOR_REVISION"
    )
    assert receipt["manual_archive_handoff_allowed"] is False


def test_d6_manual_handoff_requires_explicit_approval() -> None:
    packet = _packet()
    pending = build_operator_review_receipt(packet=packet)

    with pytest.raises(ManualArchiveHandoffViolation):
        build_manual_archive_handoff(
            packet=packet,
            receipt=pending,
        )


def test_d6_manual_handoff_does_not_execute_archive() -> None:
    packet = _packet()
    receipt = _approved_receipt(packet)

    handoff = build_manual_archive_handoff(
        packet=packet,
        receipt=receipt,
    )

    assert handoff["archive_mode"] == "MANUAL_ONLY"
    assert handoff["archive_target"] == "UNASSIGNED"
    assert handoff["archive_operation"] == "NOT_PERFORMED"
    assert handoff["archive_execution_status"] == (
        "PENDING_MANUAL_OPERATOR_ACTION"
    )
    assert handoff["manual_operator_action_required"] is True
    assert handoff["automatic_archive_allowed"] is False
    assert handoff["automatic_archive_executed"] is False
    assert handoff["real_execution"] is False


def test_d6_manual_handoff_is_valid_and_deterministic() -> None:
    packet = _packet(with_counterevidence=True)
    receipt = _approved_receipt(packet)

    first = build_manual_archive_handoff(
        packet=packet,
        receipt=receipt,
    )
    second = build_manual_archive_handoff(
        packet=packet,
        receipt=receipt,
    )

    assert first == second
    assert first is not second
    assert validate_manual_archive_handoff(
        first,
        packet,
        receipt,
    ) == ()

    assert (
        require_valid_manual_archive_handoff(
            first,
            packet,
            receipt,
        )
        is first
    )


def test_d6_handoff_rejects_automatic_archive_mutation() -> None:
    packet = _packet()
    receipt = _approved_receipt(packet)

    handoff = build_manual_archive_handoff(
        packet=packet,
        receipt=receipt,
    )
    handoff["automatic_archive_executed"] = True

    errors = validate_manual_archive_handoff(
        handoff,
        packet,
        receipt,
    )

    assert any(
        "automatic_archive_executed must be False" in error
        for error in errors
    )


def test_d6_receipt_and_handoff_do_not_mutate_packet() -> None:
    packet = _packet(with_counterevidence=True)
    original = deepcopy(packet)

    receipt = _approved_receipt(packet)

    build_manual_archive_handoff(
        packet=packet,
        receipt=receipt,
    )

    assert packet == original


def test_d6_closeout_record_is_valid_and_safe() -> None:
    record = build_d6_closeout_record()

    assert record["status"] == "D1_D6_IMPLEMENTATION_COMPLETE"
    assert record["operator_review_required"] is True
    assert record["operator_decision"] == "PENDING"
    assert record["manual_archive_only"] is True
    assert record["automatic_approval"] is False
    assert record["automatic_archive_executed"] is False
    assert record["tag_created"] is False
    assert record["release_created"] is False
    assert record["deployment_performed"] is False
    assert validate_d6_closeout_record(record) == ()
    assert require_valid_d6_closeout_record(record) is record