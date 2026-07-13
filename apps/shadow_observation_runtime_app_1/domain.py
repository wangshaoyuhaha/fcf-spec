from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Tuple


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def parse_utc_timestamp(value: str, field_name: str) -> datetime:
    normalized = _require_text(value, field_name)
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _normalize_evidence(
    values: Tuple[str, ...],
    field_name: str,
) -> Tuple[str, ...]:
    normalized = tuple(
        _require_text(value, field_name)
        for value in values
    )
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} values must be unique")
    return normalized


def _validate_score(
    value: Optional[float],
    field_name: str,
) -> Optional[float]:
    if value is None:
        return None
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")
    return normalized


@dataclass(frozen=True)
class ShadowRuntimeBoundary:
    mode: str = "shadow_observation"
    local_only: bool = True
    read_only_inputs: bool = True
    passive_observation_only: bool = True
    operator_trigger_required: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    background_scheduler_allowed: bool = False
    queue_allowed: bool = False
    daemon_allowed: bool = False
    listener_allowed: bool = False
    server_allowed: bool = False
    network_access_allowed: bool = False
    external_data_fetch_allowed: bool = False
    broker_or_exchange_connection_allowed: bool = False
    credential_access_allowed: bool = False
    account_balance_position_wallet_access_allowed: bool = False
    order_creation_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False

    def __post_init__(self) -> None:
        if self.mode != "shadow_observation":
            raise ValueError("mode must be shadow_observation")
        required = (
            self.local_only,
            self.read_only_inputs,
            self.passive_observation_only,
            self.operator_trigger_required,
            self.operator_review_required,
            self.deterministic_authority,
            self.ai_advisory_only,
        )
        if not all(required):
            raise ValueError("shadow observation authority flags must remain enabled")
        prohibited = (
            self.background_scheduler_allowed,
            self.queue_allowed,
            self.daemon_allowed,
            self.listener_allowed,
            self.server_allowed,
            self.network_access_allowed,
            self.external_data_fetch_allowed,
            self.broker_or_exchange_connection_allowed,
            self.credential_access_allowed,
            self.account_balance_position_wallet_access_allowed,
            self.order_creation_allowed,
            self.real_execution_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited runtime capability cannot be enabled")


SHADOW_OBSERVATION_RUNTIME_BOUNDARY = ShadowRuntimeBoundary()


@dataclass(frozen=True)
class ObservationWindow:
    window_id: str
    decision_time_utc: str
    observation_start_utc: str
    observation_cutoff_utc: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "window_id",
            _require_text(self.window_id, "window_id"),
        )
        decision = self.decision_time
        start = self.observation_start
        cutoff = self.observation_cutoff
        if not decision < start <= cutoff:
            raise ValueError(
                "observation window must satisfy "
                "decision < observation_start <= observation_cutoff"
            )

    @property
    def decision_time(self) -> datetime:
        return parse_utc_timestamp(
            self.decision_time_utc,
            "decision_time_utc",
        )

    @property
    def observation_start(self) -> datetime:
        return parse_utc_timestamp(
            self.observation_start_utc,
            "observation_start_utc",
        )

    @property
    def observation_cutoff(self) -> datetime:
        return parse_utc_timestamp(
            self.observation_cutoff_utc,
            "observation_cutoff_utc",
        )


@dataclass(frozen=True)
class RegisteredObservationArtifact:
    artifact_id: str
    artifact_version: str
    correlation_id: str
    content_sha256: str
    relative_path: str

    def __post_init__(self) -> None:
        for field_name in (
            "artifact_id",
            "artifact_version",
            "correlation_id",
            "relative_path",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        digest = self.content_sha256.strip().lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError("content_sha256 must be a lowercase SHA-256 digest")
        object.__setattr__(self, "content_sha256", digest)


@dataclass(frozen=True)
class ObservationRecord:
    record_id: str
    correlation_id: str
    segment: str
    decision_time_utc: str
    observation_time_utc: str
    baseline_score: float
    candidate_score: Optional[float]
    actual_outcome: Optional[float]
    risk_flags: Tuple[str, ...] = field(default_factory=tuple)
    contradiction_evidence: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in (
            "record_id",
            "correlation_id",
            "segment",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        if self.observation_time <= self.decision_time:
            raise ValueError("observation_time_utc must be after decision_time_utc")
        object.__setattr__(
            self,
            "baseline_score",
            _validate_score(self.baseline_score, "baseline_score"),
        )
        object.__setattr__(
            self,
            "candidate_score",
            _validate_score(self.candidate_score, "candidate_score"),
        )
        object.__setattr__(
            self,
            "actual_outcome",
            _validate_score(self.actual_outcome, "actual_outcome"),
        )
        object.__setattr__(
            self,
            "risk_flags",
            _normalize_evidence(self.risk_flags, "risk_flag"),
        )
        object.__setattr__(
            self,
            "contradiction_evidence",
            _normalize_evidence(
                self.contradiction_evidence,
                "contradiction_evidence",
            ),
        )

    @property
    def decision_time(self) -> datetime:
        return parse_utc_timestamp(
            self.decision_time_utc,
            "decision_time_utc",
        )

    @property
    def observation_time(self) -> datetime:
        return parse_utc_timestamp(
            self.observation_time_utc,
            "observation_time_utc",
        )


@dataclass(frozen=True)
class ObservationPolicy:
    policy_id: str
    minimum_observed_outcomes: int
    minimum_candidate_coverage: float
    maximum_candidate_mae_regression: float
    required_segments: Tuple[str, ...] = field(default_factory=tuple)
    minimum_segment_outcomes: int = 1
    maximum_segment_mae_regression: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "policy_id",
            _require_text(self.policy_id, "policy_id"),
        )
        if self.minimum_observed_outcomes < 1:
            raise ValueError("minimum_observed_outcomes must be positive")
        if not 0.0 <= self.minimum_candidate_coverage <= 1.0:
            raise ValueError(
                "minimum_candidate_coverage must be between 0 and 1"
            )
        if self.maximum_candidate_mae_regression < 0.0:
            raise ValueError(
                "maximum_candidate_mae_regression cannot be negative"
            )
        if self.minimum_segment_outcomes < 1:
            raise ValueError("minimum_segment_outcomes must be positive")
        if self.maximum_segment_mae_regression < 0.0:
            raise ValueError(
                "maximum_segment_mae_regression cannot be negative"
            )
        segments = _normalize_evidence(
            self.required_segments,
            "required_segment",
        )
        object.__setattr__(self, "required_segments", segments)


@dataclass(frozen=True)
class ShadowObservationRequest:
    run_id: str
    correlation_id: str
    operator_trigger_id: str
    artifact: RegisteredObservationArtifact
    window: ObservationWindow
    policy: ObservationPolicy

    def __post_init__(self) -> None:
        for field_name in (
            "run_id",
            "correlation_id",
            "operator_trigger_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        if self.artifact.correlation_id != self.correlation_id:
            raise ValueError(
                "artifact correlation_id must match request correlation_id"
            )
