"""Tests for governed version registry records."""

import hashlib

import pytest

from fcf.sidecars.ai_prompt_model_version_registry import (
    build_version_record,
    validate_version_record,
)


def _content_hash() -> str:
    return hashlib.sha256(b"paper-only-prompt").hexdigest()


def _record() -> dict[str, object]:
    return build_version_record(
        record_kind="PROMPT",
        record_status="REVIEW_REQUIRED",
        prompt_version="prompt-v1.0.0",
        model_version="local-model-v1",
        contract_version="contract-v1.0.0",
        registry_version="registry-v1.0.0",
        correlation_id="corr-001",
        research_run_id="run-001",
        source_artifact_ids=[
            "artifact-002",
            "artifact-001",
        ],
        validation_baseline_id="baseline-001",
        content_hash=_content_hash(),
    )


def test_version_record_is_valid() -> None:
    record = _record()

    assert validate_version_record(record) == []
    assert record["registry_entry_id"].startswith(
        "version-entry-"
    )
    assert len(str(record["registry_entry_hash"])) == 64


def test_version_record_preserves_versions() -> None:
    record = _record()

    assert record["prompt_version"] == "prompt-v1.0.0"
    assert record["model_version"] == "local-model-v1"
    assert record["contract_version"] == "contract-v1.0.0"
    assert record["registry_version"] == "registry-v1.0.0"


def test_version_record_preserves_traceability() -> None:
    record = _record()

    assert record["correlation_id"] == "corr-001"
    assert record["research_run_id"] == "run-001"
    assert record["validation_baseline_id"] == "baseline-001"
    assert record["source_artifact_ids"] == [
        "artifact-001",
        "artifact-002",
    ]


def test_registry_entry_is_deterministic() -> None:
    first = _record()
    second = _record()

    assert first["registry_entry_id"] == second["registry_entry_id"]
    assert first["registry_entry_hash"] == second[
        "registry_entry_hash"
    ]


def test_version_record_is_safety_locked() -> None:
    record = _record()

    assert record["human_review_required"] is True
    assert record["archive_required"] is True
    assert record["model_execution_allowed"] is False
    assert record["automatic_activation_allowed"] is False
    assert record["automatic_promotion_allowed"] is False
    assert record["automatic_rollback_allowed"] is False
    assert record["real_trading_allowed"] is False
    assert record["real_execution_allowed"] is False


def test_unsupported_record_kind_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported_record_kind",
    ):
        build_version_record(
            record_kind="DEPLOYMENT",
            record_status="REVIEW_REQUIRED",
            prompt_version="prompt-v1",
            model_version="model-v1",
            contract_version="contract-v1",
            registry_version="registry-v1",
            correlation_id="corr-001",
            research_run_id="run-001",
            source_artifact_ids=["artifact-001"],
            validation_baseline_id="baseline-001",
            content_hash=_content_hash(),
        )


def test_automatic_status_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported_record_status",
    ):
        build_version_record(
            record_kind="MODEL",
            record_status="AUTO_ACTIVE",
            prompt_version="prompt-v1",
            model_version="model-v1",
            contract_version="contract-v1",
            registry_version="registry-v1",
            correlation_id="corr-001",
            research_run_id="run-001",
            source_artifact_ids=["artifact-001"],
            validation_baseline_id="baseline-001",
            content_hash=_content_hash(),
        )


def test_invalid_content_hash_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="invalid_sha256:content_hash",
    ):
        build_version_record(
            record_kind="MODEL",
            record_status="DRAFT",
            prompt_version="prompt-v1",
            model_version="model-v1",
            contract_version="contract-v1",
            registry_version="registry-v1",
            correlation_id="corr-001",
            research_run_id="run-001",
            source_artifact_ids=["artifact-001"],
            validation_baseline_id="baseline-001",
            content_hash="not-a-sha256",
        )


def test_model_execution_enablement_is_detected() -> None:
    record = _record()
    record["model_execution_allowed"] = True

    assert "model_execution_not_blocked" in (
        validate_version_record(record)
    )


def test_forbidden_action_field_is_detected() -> None:
    record = _record()
    record["order"] = True

    assert "forbidden_action_field:order" in (
        validate_version_record(record)
    )
