"""Tests for governed AI version review packets."""

from copy import deepcopy
import hashlib

import pytest

from fcf.sidecars.ai_prompt_model_version_registry import (
    build_version_governance_review_packet,
    build_version_record,
    evaluate_version_compatibility,
    validate_version_governance_review_packet,
)


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _record(
    *,
    kind: str,
    version: str,
    status: str = "APPROVED_FOR_PAPER_RESEARCH",
) -> dict[str, object]:
    versions = {
        "prompt_version": "prompt-v1",
        "model_version": "model-v1",
        "contract_version": "contract-v1",
        "registry_version": "registry-v1",
    }

    if kind == "PROMPT":
        versions["prompt_version"] = version
    elif kind == "MODEL":
        versions["model_version"] = version
    elif kind == "CONTRACT":
        versions["contract_version"] = version
    elif kind == "REGISTRY":
        versions["registry_version"] = version

    return build_version_record(
        record_kind=kind,
        record_status=status,
        prompt_version=versions["prompt_version"],
        model_version=versions["model_version"],
        contract_version=versions["contract_version"],
        registry_version=versions["registry_version"],
        correlation_id="corr-001",
        research_run_id=f"run-{kind.lower()}",
        source_artifact_ids=[f"artifact-{kind.lower()}"],
        validation_baseline_id="baseline-001",
        content_hash=_hash(version),
    )


def _bundle(
    *,
    blocked_prompt: bool = False,
) -> list[dict[str, object]]:
    return [
        _record(
            kind="PROMPT",
            version="prompt-v1",
            status=(
                "BLOCKED"
                if blocked_prompt
                else "APPROVED_FOR_PAPER_RESEARCH"
            ),
        ),
        _record(kind="MODEL", version="model-v1"),
        _record(kind="CONTRACT", version="contract-v1"),
        _record(kind="REGISTRY", version="registry-v1"),
    ]


def _report(
    *,
    blocked_prompt: bool = False,
) -> dict[str, object]:
    return evaluate_version_compatibility(
        _bundle(blocked_prompt=blocked_prompt)
    )


def test_review_packet_is_valid() -> None:
    packet = build_version_governance_review_packet(
        _report()
    )

    assert validate_version_governance_review_packet(
        packet
    ) == []
    assert packet["review_packet_id"].startswith(
        "version-review-"
    )
    assert packet["review_packet_status"] == (
        "REVIEW_REQUIRED"
    )
    assert len(str(packet["review_packet_hash"])) == 64


def test_compatible_bundle_still_requires_review() -> None:
    packet = build_version_governance_review_packet(
        _report()
    )

    assert packet["compatible_for_paper_review"] is True
    assert packet["finding_count"] == 0
    assert packet["human_review_required"] is True
    assert packet["automatic_approval_allowed"] is False


def test_blocked_version_findings_are_preserved() -> None:
    report = _report(blocked_prompt=True)
    packet = build_version_governance_review_packet(report)

    assert packet["compatible_for_paper_review"] is False
    assert packet["finding_count"] >= 1
    assert packet["highest_severity"] == "CRITICAL"
    assert packet["finding_class_summary"][
        "BLOCKED_VERSION_SELECTED"
    ] == 1
    assert len(packet["open_finding_ids"]) >= 1


def test_packet_preserves_report_snapshot() -> None:
    report = _report(blocked_prompt=True)
    packet = build_version_governance_review_packet(report)

    assert packet["compatibility_report_snapshot"] == report
    assert packet["source_compatibility_report_id"] == report[
        "compatibility_report_id"
    ]
    assert packet["source_compatibility_report_hash"] == report[
        "compatibility_report_hash"
    ]


def test_packet_does_not_mutate_report() -> None:
    report = _report(blocked_prompt=True)
    before = deepcopy(report)

    build_version_governance_review_packet(report)

    assert report == before


def test_packet_identifier_is_deterministic() -> None:
    first = build_version_governance_review_packet(
        _report()
    )
    second = build_version_governance_review_packet(
        _report()
    )

    assert first["review_packet_id"] == second[
        "review_packet_id"
    ]
    assert first["review_packet_hash"] == second[
        "review_packet_hash"
    ]


def test_packet_is_safety_locked() -> None:
    packet = build_version_governance_review_packet(
        _report()
    )

    assert packet["human_review_required"] is True
    assert packet["operator_review_bypass_allowed"] is False
    assert packet["automatic_approval_allowed"] is False
    assert packet["automatic_activation_allowed"] is False
    assert packet["automatic_promotion_allowed"] is False
    assert packet["automatic_rollback_allowed"] is False
    assert packet["model_execution_allowed"] is False
    assert packet["archive_required"] is True
    assert packet["source_mutation_allowed"] is False
    assert packet["real_trading_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_invalid_packet_status_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported_review_packet_status",
    ):
        build_version_governance_review_packet(
            _report(),
            review_packet_status="AUTO_APPROVED",
        )


def test_invalid_report_is_rejected() -> None:
    report = _report()
    report["automatic_activation_allowed"] = True

    with pytest.raises(
        ValueError,
        match="invalid_compatibility_report",
    ):
        build_version_governance_review_packet(report)


def test_review_bypass_is_detected() -> None:
    packet = build_version_governance_review_packet(
        _report()
    )
    packet["operator_review_bypass_allowed"] = True

    assert "operator_review_bypass_not_blocked" in (
        validate_version_governance_review_packet(packet)
    )


def test_forbidden_activation_instruction_is_detected() -> None:
    packet = build_version_governance_review_packet(
        _report()
    )
    packet["activation_instruction"] = "activate"

    assert "forbidden_action_field:activation_instruction" in (
        validate_version_governance_review_packet(packet)
    )
