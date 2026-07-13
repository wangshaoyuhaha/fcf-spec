from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from apps.paper_validation_runtime_app_1 import coordinator
from apps.paper_validation_runtime_app_1.coordinator import (
    run_paper_validation,
    write_validation_runtime_bundle,
)
from apps.paper_validation_runtime_app_1.domain import (
    ComparisonPolicy,
    EvaluationWindow,
    RegisteredArtifact,
    ValidationRunRequest,
)
from apps.paper_validation_runtime_app_1.input_loader import (
    ArtifactRegistryEntry,
    LoadedValidationDataset,
)
from apps.paper_validation_runtime_app_1.metric_engine import (
    ComparisonPacket,
    MetricSummary,
)
from apps.paper_validation_runtime_app_1.packet_builder import (
    ContradictionRecord,
    RiskFlag,
)


def _request(run_id: str = "run-001") -> ValidationRunRequest:
    return ValidationRunRequest(
        run_id=run_id,
        correlation_id="corr-001",
        artifact_id="artifact-001",
        artifact_version="v1",
        window=EvaluationWindow(
            window_id="window-001",
            start_time_utc="2026-01-01T00:00:00Z",
            decision_cutoff_utc="2026-01-02T00:00:00Z",
            observation_cutoff_utc="2026-01-03T00:00:00Z",
            end_time_utc="2026-01-03T00:00:00Z",
        ),
        policy=ComparisonPolicy(
            policy_id="policy-001",
            minimum_eligible_samples=1,
            minimum_candidate_coverage=0.0,
            maximum_mae_regression=1.0,
            minimum_accuracy_delta=-1.0,
        ),
        operator_trigger_id="operator-trigger-001",
    )


def _dataset(request: ValidationRunRequest) -> LoadedValidationDataset:
    return LoadedValidationDataset(
        artifact=RegisteredArtifact(
            artifact_id=request.artifact_id,
            artifact_version=request.artifact_version,
            correlation_id=request.correlation_id,
            content_sha256="1" * 64,
            relative_path="registered.json",
        ),
        window=request.window,
        samples=(object(), object()),
        source_path="registered.json",
        source_sha256="2" * 64,
    )


def _comparison(
    request: ValidationRunRequest,
    *,
    blocked: bool = False,
) -> ComparisonPacket:
    metrics = MetricSummary(
        total_samples=2,
        eligible_samples=2,
        excluded_samples=0,
        candidate_scored_samples=2,
        candidate_abstentions=0,
        candidate_coverage=1.0,
        baseline_mae=0.2,
        candidate_mae=0.1,
        mae_delta=-0.1,
        baseline_accuracy=0.5,
        candidate_accuracy=1.0,
        accuracy_delta=0.5,
    )
    return ComparisonPacket(
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        policy_id=request.policy.policy_id,
        status="BLOCKED" if blocked else "READY_FOR_OPERATOR_REVIEW",
        recommendation=(
            "DO_NOT_ADVANCE"
            if blocked
            else "CANDIDATE_MAY_PROCEED_TO_OPERATOR_REVIEW"
        ),
        overall_metrics=metrics,
        segment_metrics={},
        blocking_reasons=(
            ("INSUFFICIENT_ELIGIBLE_SAMPLES",) if blocked else ()
        ),
        review_reasons=("OPERATOR_DECISION_REQUIRED",),
    )


def _patch_runtime(
    monkeypatch: pytest.MonkeyPatch,
    request: ValidationRunRequest,
    *,
    blocked: bool = False,
) -> None:
    monkeypatch.setattr(
        coordinator,
        "load_registered_validation_dataset",
        lambda **kwargs: _dataset(request),
    )
    monkeypatch.setattr(
        coordinator,
        "evaluate_candidate",
        lambda **kwargs: _comparison(request, blocked=blocked),
    )


def _registry(request: ValidationRunRequest) -> ArtifactRegistryEntry:
    return ArtifactRegistryEntry(
        artifact_id=request.artifact_id,
        artifact_version=request.artifact_version,
        correlation_id=request.correlation_id,
        relative_path="registered.json",
        content_sha256="1" * 64,
    )


def test_run_paper_validation_builds_review_ready_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request)

    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )

    assert outcome.lifecycle.state == "REVIEW_PACKET_READY"
    assert [event.to_state for event in outcome.lifecycle.events] == [
        "INPUT_LOADING",
        "INPUT_VALIDATED",
        "METRICS_EVALUATED",
        "RESULT_PACKET_BUILT",
        "REVIEW_PACKET_READY",
    ]
    assert outcome.operator_triggered is True
    assert outcome.network_access_used is False
    assert outcome.real_execution_used is False
    assert not (tmp_path / request.run_id).exists()


def test_blocked_comparison_remains_operator_review_gated(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request, blocked=True)

    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )

    assert outcome.lifecycle.state == "BLOCKED_REVIEW_REQUIRED"
    assert outcome.result_packet.status == "BLOCKED"
    assert outcome.operator_review_packet.required_action == (
        "OPERATOR_REVIEW_BLOCKING_EVIDENCE"
    )
    assert outcome.operator_review_packet.operator_review_required is True


def test_runtime_preserves_supplied_risk_and_contradiction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request)
    risk = RiskFlag(
        code="OPERATOR_NOTE",
        severity="LOW",
        message="Operator supplied note",
        blocking=False,
        source="operator",
    )
    contradiction = ContradictionRecord(
        contradiction_id="contradiction-001",
        correlation_id=request.correlation_id,
        category="narrative_conflict",
        statement_a="positive",
        statement_b="negative",
        severity="MEDIUM",
    )

    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
        risk_flags=(risk,),
        contradictions=(contradiction,),
    )

    assert risk in outcome.result_packet.risk_flags
    assert outcome.result_packet.contradictions == (contradiction,)
    assert outcome.request.correlation_id == outcome.lifecycle.correlation_id


def test_writer_creates_hash_manifest_and_no_archive(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request)
    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )

    written = write_validation_runtime_bundle(
        outcome=outcome,
        output_root=tmp_path / "output",
    )

    assert Path(written.validation_result_file).is_file()
    assert Path(written.operator_review_file).is_file()
    assert Path(written.lifecycle_file).is_file()
    assert Path(written.manifest_file).is_file()
    manifest = json.loads(Path(written.manifest_file).read_text(encoding="utf-8"))
    assert manifest["validation_result_sha256"] == (
        written.validation_result_sha256
    )
    assert manifest["operator_review_sha256"] == written.operator_review_sha256
    assert manifest["lifecycle_sha256"] == written.lifecycle_sha256
    assert manifest["archive_status"] == "NOT_ARCHIVED"
    assert manifest["automatic_approval_allowed"] is False
    assert manifest["real_execution_allowed"] is False


def test_writer_is_idempotent_for_identical_bundle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request)
    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )

    first = write_validation_runtime_bundle(
        outcome=outcome,
        output_root=tmp_path / "output",
    )
    second = write_validation_runtime_bundle(
        outcome=outcome,
        output_root=tmp_path / "output",
    )

    assert first.reused_existing_bundle is False
    assert second.reused_existing_bundle is True
    assert first.validation_result_sha256 == second.validation_result_sha256


def test_writer_rejects_tampered_existing_bundle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request)
    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )
    written = write_validation_runtime_bundle(
        outcome=outcome,
        output_root=tmp_path / "output",
    )
    Path(written.operator_review_file).write_text(
        "{}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="existing validation bundle content mismatch",
    ):
        write_validation_runtime_bundle(
            outcome=outcome,
            output_root=tmp_path / "output",
        )


def test_writer_rejects_unsafe_run_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request(run_id="../escape")
    _patch_runtime(monkeypatch, request)
    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )

    with pytest.raises(ValueError, match="run_id is unsafe"):
        write_validation_runtime_bundle(
            outcome=outcome,
            output_root=tmp_path / "output",
        )


def test_runtime_outcome_rejects_authority_escalation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    request = _request()
    _patch_runtime(monkeypatch, request)
    outcome = run_paper_validation(
        request=request,
        registry_entry=_registry(request),
        allowed_root=tmp_path,
    )

    with pytest.raises(ValueError, match="prohibited runtime behavior"):
        replace(outcome, automatic_approval_used=True)
