"""Tests for the AI version registry final handoff."""

from copy import deepcopy
import hashlib

import pytest

from fcf.sidecars.ai_prompt_model_version_registry import (
    build_final_handoff,
    build_version_governance_review_packet,
    build_version_record,
    evaluate_version_compatibility,
    validate_final_handoff,
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


def _packet(
    *,
    blocked_prompt: bool = False,
) -> dict[str, object]:
    records = [
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

    report = evaluate_version_compatibility(records)

    return build_version_governance_review_packet(report)


def test_final_handoff_is_valid() -> None:
    handoff = build_final_handoff(_packet())

    assert validate_final_handoff(handoff) == []
    assert handoff["handoff_id"].startswith(
        "version-registry-handoff-"
    )
    assert handoff["handoff_status"] == (
        "WAITING_FOR_OPERATOR_REVIEW"
    )
    assert len(str(handoff["handoff_hash"])) == 64


def test_handoff_preserves_review_packet() -> None:
    packet = _packet()
    handoff = build_final_handoff(packet)

    assert handoff["review_packet_snapshot"] == packet
    assert handoff["source_review_packet_id"] == packet[
        "review_packet_id"
    ]
    assert handoff["source_review_packet_hash"] == packet[
        "review_packet_hash"
    ]


def test_handoff_does_not_mutate_packet() -> None:
    packet = _packet()
    before = deepcopy(packet)

    build_final_handoff(packet)

    assert packet == before


def test_handoff_identifier_is_deterministic() -> None:
    first = build_final_handoff(_packet())
    second = build_final_handoff(_packet())

    assert first["handoff_id"] == second["handoff_id"]
    assert first["handoff_hash"] == second["handoff_hash"]


def test_compatible_bundle_still_waits_for_review() -> None:
    handoff = build_final_handoff(_packet())

    assert handoff["compatible_for_paper_review"] is True
    assert handoff["finding_count"] == 0
    assert handoff["human_review_required"] is True
    assert handoff["handoff_status"] == (
        "WAITING_FOR_OPERATOR_REVIEW"
    )


def test_blocked_bundle_preserves_findings() -> None:
    handoff = build_final_handoff(
        _packet(blocked_prompt=True)
    )

    assert handoff["compatible_for_paper_review"] is False
    assert handoff["finding_count"] >= 1
    assert handoff["highest_severity"] == "CRITICAL"
    assert len(handoff["open_finding_ids"]) >= 1


def test_handoff_is_safety_locked() -> None:
    handoff = build_final_handoff(_packet())

    assert handoff["human_review_required"] is True
    assert handoff["operator_review_bypass_allowed"] is False
    assert handoff["automatic_approval_allowed"] is False
    assert handoff["automatic_activation_allowed"] is False
    assert handoff["automatic_promotion_allowed"] is False
    assert handoff["automatic_rollback_allowed"] is False
    assert handoff["model_execution_allowed"] is False
    assert handoff["archive_required"] is True
    assert handoff["source_mutation_allowed"] is False
    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False
    assert handoff["real_trading_allowed"] is False
    assert handoff["real_execution_allowed"] is False


def test_invalid_review_packet_is_rejected() -> None:
    packet = _packet()
    packet["automatic_activation_allowed"] = True

    with pytest.raises(
        ValueError,
        match="invalid_review_packet",
    ):
        build_final_handoff(packet)


def test_review_bypass_is_detected() -> None:
    handoff = build_final_handoff(_packet())
    handoff["operator_review_bypass_allowed"] = True

    assert "operator_review_bypass_not_blocked" in (
        validate_final_handoff(handoff)
    )


def test_forbidden_deployment_field_is_detected() -> None:
    handoff = build_final_handoff(_packet())
    handoff["deployment_instruction"] = "deploy"

    assert "forbidden_action_field:deployment_instruction" in (
        validate_final_handoff(handoff)
    )
