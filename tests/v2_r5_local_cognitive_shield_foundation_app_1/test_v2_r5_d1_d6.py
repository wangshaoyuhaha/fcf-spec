from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r4_local_anomaly_radar_foundation_app_1 import AnomalyEvidence
from apps.v2_r5_local_cognitive_shield_foundation_app_1 import (
    V2_R5_LOCAL_COGNITIVE_SHIELD_BOUNDARY,
    CognitiveShieldLedger,
    CognitiveTask,
    CognitiveTaskPolicy,
    RegisteredAdvisoryArtifact,
    V2R5LocalCognitiveShieldBoundary,
    build_operator_acceptance,
    build_read_model,
    evaluate_cognitive_shield,
)


def _anomaly(
    *, state: str = "CONFIRMED", expires_at: str = "2026-01-01T00:10:00Z"
) -> AnomalyEvidence:
    return AnomalyEvidence(
        rule_id="registered-anomaly-rule",
        rule_version="v1",
        context_id="registered-local-context",
        stream_id="registered-stream",
        event_id="registered-event",
        state=state,
        value=Decimal("8"),
        z_score=Decimal("3"),
        velocity_per_second=Decimal("0.1"),
        persistence_count=2,
        negative_evidence=(),
        reason_codes=("REGISTERED_TEST",),
        observed_at_utc="2026-01-01T00:00:00Z",
        expires_at_utc=expires_at,
        baseline_replay_hash="b" * 64,
        evidence_hash="a" * 64,
    )


def _policy() -> CognitiveTaskPolicy:
    return CognitiveTaskPolicy(
        policy_id="registered-cognitive-policy",
        policy_version="v1",
        minimum_advisory_confidence=Decimal("0.70"),
        max_task_seconds=60,
    )


def _task(*, evidence_hash: str = "a" * 64, deadline: str = "2026-01-01T00:01:00Z") -> CognitiveTask:
    return CognitiveTask(
        task_id="registered-cognitive-task",
        correlation_id="registered-correlation",
        anomaly_evidence_hash=evidence_hash,
        requested_at_utc="2026-01-01T00:00:00Z",
        deadline_at_utc=deadline,
        task_kind="EXPLAIN_AND_CHALLENGE",
        policy_id="registered-cognitive-policy",
        policy_version="v1",
    )


def _advisory(
    *,
    stance: str = "SUPPORT",
    confidence: Decimal = Decimal("0.80"),
    task_id: str = "registered-cognitive-task",
    evidence_hash: str = "a" * 64,
    produced_at: str = "2026-01-01T00:00:30Z",
) -> RegisteredAdvisoryArtifact:
    return RegisteredAdvisoryArtifact(
        artifact_id="registered-advisory-artifact",
        artifact_version="v1",
        task_id=task_id,
        anomaly_evidence_hash=evidence_hash,
        produced_at_utc=produced_at,
        stance=stance,
        confidence=confidence,
        content_sha256="c" * 64,
        reason_codes=("REGISTERED_LOCAL_REASON",),
    )


def _evaluate(advisory: RegisteredAdvisoryArtifact | None):
    return evaluate_cognitive_shield(
        _anomaly(),
        _task(),
        _policy(),
        advisory,
        as_of_utc="2026-01-01T00:00:45Z",
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R5_LOCAL_COGNITIVE_SHIELD_BOUNDARY

    assert boundary.local_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.model_invocation_allowed is False
    assert boundary.prompt_execution_allowed is False
    assert boundary.automatic_learning_allowed is False
    assert boundary.order_path_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R5LocalCognitiveShieldBoundary(model_invocation_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.model_invocation_allowed = True  # type: ignore[misc]


def test_d2_contract_rejects_model_prompt_and_unregistered_artifact() -> None:
    with pytest.raises(ValueError, match="cannot invoke"):
        replace(_policy(), model_invocation_allowed=True)
    with pytest.raises(ValueError, match="Operator registration"):
        replace(_advisory(), operator_registered=False)


def test_d3_support_is_deterministic_and_preserves_anomaly() -> None:
    evidence = _evaluate(_advisory())
    repeated = _evaluate(_advisory())

    assert evidence.shield_state == "SUPPORTED_REVIEW"
    assert evidence.uncertainty_state == "NONE"
    assert evidence.explanation_used is True
    assert evidence.deterministic_evidence_preserved is True
    assert evidence.shield_evidence_hash == repeated.shield_evidence_hash


def test_d3_contradiction_requires_review_without_state_mutation() -> None:
    evidence = _evaluate(_advisory(stance="CONTRADICT"))

    assert evidence.shield_state == "CONTRADICTION_REVIEW"
    assert evidence.uncertainty_state == "DATA_CONFLICT"
    assert evidence.anomaly_state == "CONFIRMED"
    assert evidence.operator_review_required is True


def test_d4_missing_and_timeout_use_registered_fallback() -> None:
    missing = _evaluate(None)
    timeout = evaluate_cognitive_shield(
        _anomaly(),
        _task(),
        _policy(),
        _advisory(produced_at="2026-01-01T00:01:01Z"),
        as_of_utc="2026-01-01T00:01:01Z",
    )

    assert missing.shield_state == "DEGRADED"
    assert "SKIP_EXPLANATION" in missing.reason_codes
    assert timeout.shield_state == "DEGRADED"
    assert "COGNITIVE_TIMEOUT" in timeout.reason_codes
    assert timeout.explanation_used is False


def test_d4_low_confidence_and_abstention_are_explicit() -> None:
    low = _evaluate(_advisory(confidence=Decimal("0.69")))
    abstain = _evaluate(_advisory(stance="ABSTAIN"))

    assert low.shield_state == "ABSTAIN_REVIEW_REQUIRED"
    assert low.uncertainty_state == "LOW_CONFIDENCE"
    assert abstain.shield_state == "ABSTAIN_REVIEW_REQUIRED"
    assert abstain.uncertainty_state == "ABSTAIN_REVIEW_REQUIRED"


def test_d4_hard_gates_block_degraded_expired_and_mismatched_evidence() -> None:
    degraded = evaluate_cognitive_shield(
        _anomaly(state="DEGRADED"),
        _task(),
        _policy(),
        _advisory(),
        as_of_utc="2026-01-01T00:00:45Z",
    )
    expired = evaluate_cognitive_shield(
        _anomaly(expires_at="2026-01-01T00:00:20Z"),
        _task(),
        _policy(),
        _advisory(),
        as_of_utc="2026-01-01T00:00:45Z",
    )
    mismatch = _evaluate(_advisory(evidence_hash="d" * 64))

    assert degraded.shield_state == "BLOCKED"
    assert expired.uncertainty_state == "STATE_EXPIRED"
    assert mismatch.shield_state == "BLOCKED"
    assert mismatch.uncertainty_state == "DATA_CONFLICT"


def test_d4_task_policy_identity_and_deadline_fail_closed() -> None:
    with pytest.raises(ValueError, match="identity mismatch"):
        evaluate_cognitive_shield(
            _anomaly(), _task(evidence_hash="d" * 64), _policy(), None,
            as_of_utc="2026-01-01T00:00:45Z",
        )
    with pytest.raises(ValueError, match="policy maximum"):
        evaluate_cognitive_shield(
            _anomaly(), _task(deadline="2026-01-01T00:02:00Z"), _policy(), None,
            as_of_utc="2026-01-01T00:00:45Z",
        )


def test_d5_ledger_rejects_duplicate_task_and_evidence() -> None:
    task = _task()
    evidence = _evaluate(_advisory())
    ledger = CognitiveShieldLedger().register_task(task).append_evidence(evidence)

    with pytest.raises(ValueError, match="duplicate cognitive task"):
        ledger.register_task(task)
    with pytest.raises(ValueError, match="duplicate shield evidence"):
        ledger.append_evidence(evidence)


def test_d6_read_model_and_acceptance_remain_read_only() -> None:
    evidence = _evaluate(_advisory())
    ledger = CognitiveShieldLedger().register_task(_task()).append_evidence(evidence)
    model = build_read_model(ledger)
    acceptance = build_operator_acceptance(evidence)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["model_invocation"] is False
    assert model.payload["order_path"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.automatic_approval is False
    with pytest.raises(TypeError):
        model.payload["model_invocation"] = True  # type: ignore[index]
