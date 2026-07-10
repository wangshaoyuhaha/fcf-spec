"""Tests for AI version compatibility and conflict checks."""

import hashlib

from fcf.sidecars.ai_prompt_model_version_registry import (
    build_version_record,
    evaluate_version_compatibility,
    validate_compatibility_report,
)


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _record(
    *,
    kind: str,
    version: str,
    status: str = "APPROVED_FOR_PAPER_RESEARCH",
    contract_version: str = "contract-v1",
    registry_version: str = "registry-v1",
    baseline_id: str = "baseline-001",
    correlation_id: str = "corr-001",
    content_label: str | None = None,
) -> dict[str, object]:
    versions = {
        "prompt_version": "prompt-v1",
        "model_version": "model-v1",
        "contract_version": contract_version,
        "registry_version": registry_version,
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
        correlation_id=correlation_id,
        research_run_id=f"run-{kind.lower()}",
        source_artifact_ids=[f"artifact-{kind.lower()}"],
        validation_baseline_id=baseline_id,
        content_hash=_hash(content_label or version),
    )


def _compatible_bundle() -> list[dict[str, object]]:
    return [
        _record(kind="PROMPT", version="prompt-v1"),
        _record(kind="MODEL", version="model-v1"),
        _record(kind="CONTRACT", version="contract-v1"),
        _record(kind="REGISTRY", version="registry-v1"),
    ]


def _classes(report: dict[str, object]) -> set[str]:
    findings = report["findings"]
    assert isinstance(findings, list)

    return {
        str(finding["finding_class"])
        for finding in findings
    }


def test_approved_bundle_is_compatible() -> None:
    report = evaluate_version_compatibility(
        _compatible_bundle()
    )

    assert validate_compatibility_report(report) == []
    assert report["compatible"] is True
    assert report["compatibility_status"] == (
        "COMPATIBLE_FOR_PAPER_REVIEW"
    )
    assert report["finding_count"] == 0


def test_missing_required_kind_is_blocking() -> None:
    records = _compatible_bundle()[:-1]

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert "MISSING_REQUIRED_KIND" in _classes(report)


def test_duplicate_kind_selection_is_blocking() -> None:
    records = _compatible_bundle()
    records.append(
        _record(kind="MODEL", version="model-v2")
    )

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert "DUPLICATE_KIND_SELECTION" in _classes(report)


def test_blocked_version_is_critical() -> None:
    records = _compatible_bundle()
    records[0] = _record(
        kind="PROMPT",
        version="prompt-v1",
        status="BLOCKED",
    )

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert report["highest_severity"] == "CRITICAL"
    assert "BLOCKED_VERSION_SELECTED" in _classes(report)


def test_review_required_version_is_recorded() -> None:
    records = _compatible_bundle()
    records[1] = _record(
        kind="MODEL",
        version="model-v1",
        status="REVIEW_REQUIRED",
    )

    report = evaluate_version_compatibility(records)

    assert "REVIEW_REQUIRED_VERSION_SELECTED" in (
        _classes(report)
    )
    assert report["human_review_required"] is True


def test_contract_reference_mismatch_is_detected() -> None:
    records = _compatible_bundle()
    records[0] = _record(
        kind="PROMPT",
        version="prompt-v1",
        contract_version="contract-v2",
    )

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert "CONTRACT_REFERENCE_MISMATCH" in _classes(report)


def test_registry_reference_mismatch_is_detected() -> None:
    records = _compatible_bundle()
    records[1] = _record(
        kind="MODEL",
        version="model-v1",
        registry_version="registry-v2",
    )

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert "REGISTRY_REFERENCE_MISMATCH" in _classes(report)


def test_validation_baseline_mismatch_is_detected() -> None:
    records = _compatible_bundle()
    records[1] = _record(
        kind="MODEL",
        version="model-v1",
        baseline_id="baseline-999",
    )

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert "VALIDATION_BASELINE_MISMATCH" in _classes(report)


def test_correlation_id_mismatch_is_detected() -> None:
    records = _compatible_bundle()
    records[1] = _record(
        kind="MODEL",
        version="model-v1",
        correlation_id="corr-999",
    )

    report = evaluate_version_compatibility(records)

    assert report["compatible"] is False
    assert "CORRELATION_ID_MISMATCH" in _classes(report)


def test_duplicate_content_under_versions_is_recorded() -> None:
    records = _compatible_bundle()
    records[0] = _record(
        kind="PROMPT",
        version="prompt-v1",
        content_label="same-content",
    )
    records[1] = _record(
        kind="MODEL",
        version="model-v1",
        content_label="same-content",
    )

    report = evaluate_version_compatibility(records)

    assert "DUPLICATE_CONTENT_DIFFERENT_VERSION" in (
        _classes(report)
    )


def test_compatibility_report_is_deterministic() -> None:
    first = evaluate_version_compatibility(
        _compatible_bundle()
    )
    second = evaluate_version_compatibility(
        list(reversed(_compatible_bundle()))
    )

    assert first["compatibility_report_id"] == second[
        "compatibility_report_id"
    ]
    assert first["compatibility_report_hash"] == second[
        "compatibility_report_hash"
    ]


def test_compatibility_report_is_safety_locked() -> None:
    report = evaluate_version_compatibility(
        _compatible_bundle()
    )

    assert report["human_review_required"] is True
    assert report["operator_review_bypass_allowed"] is False
    assert report["archive_required"] is True
    assert report["model_execution_allowed"] is False
    assert report["automatic_activation_allowed"] is False
    assert report["automatic_promotion_allowed"] is False
    assert report["automatic_rollback_allowed"] is False
    assert report["source_mutation_allowed"] is False
    assert report["real_trading_allowed"] is False
    assert report["real_execution_allowed"] is False


def test_unsafe_activation_is_detected() -> None:
    report = evaluate_version_compatibility(
        _compatible_bundle()
    )
    report["automatic_activation_allowed"] = True

    assert "automatic_activation_not_blocked" in (
        validate_compatibility_report(report)
    )
