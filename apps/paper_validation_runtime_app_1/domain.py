from __future__ import annotations

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


@dataclass(frozen=True)
class RuntimeBoundary:
    mode: str = "paper_validation"
    local_only: bool = True
    read_only_inputs: bool = True
    operator_trigger_required: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    background_scheduler_allowed: bool = False
    listener_allowed: bool = False
    network_access_allowed: bool = False
    external_data_fetch_allowed: bool = False
    broker_or_exchange_connection_allowed: bool = False
    credential_access_allowed: bool = False
    account_or_wallet_access_allowed: bool = False
    real_order_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False
    shadow_runtime_allowed: bool = False

    def __post_init__(self) -> None:
        if self.mode != "paper_validation":
            raise ValueError("mode must be paper_validation")
        required_true = (
            self.local_only,
            self.read_only_inputs,
            self.operator_trigger_required,
            self.operator_review_required,
            self.deterministic_authority,
            self.ai_advisory_only,
        )
        if not all(required_true):
            raise ValueError("paper validation authority flags must remain enabled")
        prohibited = (
            self.background_scheduler_allowed,
            self.listener_allowed,
            self.network_access_allowed,
            self.external_data_fetch_allowed,
            self.broker_or_exchange_connection_allowed,
            self.credential_access_allowed,
            self.account_or_wallet_access_allowed,
            self.real_order_allowed,
            self.real_execution_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
            self.shadow_runtime_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited runtime capability cannot be enabled")


PAPER_VALIDATION_RUNTIME_BOUNDARY = RuntimeBoundary()


@dataclass(frozen=True)
class EvaluationWindow:
    window_id: str
    start_time_utc: str
    decision_cutoff_utc: str
    observation_cutoff_utc: str
    end_time_utc: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "window_id", _require_text(self.window_id, "window_id"))
        start = parse_utc_timestamp(self.start_time_utc, "start_time_utc")
        decision = parse_utc_timestamp(
            self.decision_cutoff_utc,
            "decision_cutoff_utc",
        )
        observation = parse_utc_timestamp(
            self.observation_cutoff_utc,
            "observation_cutoff_utc",
        )
        end = parse_utc_timestamp(self.end_time_utc, "end_time_utc")
        if not start < decision < observation <= end:
            raise ValueError(
                "evaluation window must satisfy "
                "start < decision < observation <= end"
            )

    @property
    def start(self) -> datetime:
        return parse_utc_timestamp(self.start_time_utc, "start_time_utc")

    @property
    def decision_cutoff(self) -> datetime:
        return parse_utc_timestamp(
            self.decision_cutoff_utc,
            "decision_cutoff_utc",
        )

    @property
    def observation_cutoff(self) -> datetime:
        return parse_utc_timestamp(
            self.observation_cutoff_utc,
            "observation_cutoff_utc",
        )

    @property
    def end(self) -> datetime:
        return parse_utc_timestamp(self.end_time_utc, "end_time_utc")


@dataclass(frozen=True)
class RegisteredArtifact:
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
            character not in "0123456789abcdef" for character in digest
        ):
            raise ValueError("content_sha256 must be a lowercase SHA-256 digest")
        object.__setattr__(self, "content_sha256", digest)


@dataclass(frozen=True)
class ValidationSample:
    sample_id: str
    segment: str
    decision_time_utc: str
    outcome_time_utc: str
    baseline_score: float
    candidate_score: Optional[float]
    actual_outcome: float
    eligible: bool = True
    exclusion_reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "sample_id", _require_text(self.sample_id, "sample_id"))
        object.__setattr__(self, "segment", _require_text(self.segment, "segment"))
        decision = parse_utc_timestamp(
            self.decision_time_utc,
            "decision_time_utc",
        )
        outcome = parse_utc_timestamp(
            self.outcome_time_utc,
            "outcome_time_utc",
        )
        if outcome <= decision:
            raise ValueError("outcome_time_utc must be after decision_time_utc")
        for field_name in ("baseline_score", "actual_outcome"):
            value = float(getattr(self, field_name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        if self.candidate_score is not None:
            candidate = float(self.candidate_score)
            if not 0.0 <= candidate <= 1.0:
                raise ValueError("candidate_score must be between 0 and 1")
            object.__setattr__(self, "candidate_score", candidate)
        if self.eligible and self.exclusion_reason.strip():
            raise ValueError("eligible sample cannot have exclusion_reason")
        if not self.eligible and not self.exclusion_reason.strip():
            raise ValueError("ineligible sample requires exclusion_reason")

    @property
    def decision_time(self) -> datetime:
        return parse_utc_timestamp(
            self.decision_time_utc,
            "decision_time_utc",
        )

    @property
    def outcome_time(self) -> datetime:
        return parse_utc_timestamp(
            self.outcome_time_utc,
            "outcome_time_utc",
        )


@dataclass(frozen=True)
class ComparisonPolicy:
    policy_id: str
    minimum_eligible_samples: int
    minimum_candidate_coverage: float
    maximum_mae_regression: float
    minimum_accuracy_delta: float
    required_segments: Tuple[str, ...] = field(default_factory=tuple)
    minimum_segment_samples: int = 1
    maximum_segment_mae_regression: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", _require_text(self.policy_id, "policy_id"))
        if self.minimum_eligible_samples < 1:
            raise ValueError("minimum_eligible_samples must be positive")
        if not 0.0 <= self.minimum_candidate_coverage <= 1.0:
            raise ValueError("minimum_candidate_coverage must be between 0 and 1")
        if self.minimum_segment_samples < 1:
            raise ValueError("minimum_segment_samples must be positive")
        normalized_segments = tuple(
            _require_text(segment, "required_segment")
            for segment in self.required_segments
        )
        if len(set(normalized_segments)) != len(normalized_segments):
            raise ValueError("required_segments must be unique")
        object.__setattr__(self, "required_segments", normalized_segments)


@dataclass(frozen=True)
class ValidationRunRequest:
    run_id: str
    correlation_id: str
    artifact_id: str
    artifact_version: str
    window: EvaluationWindow
    policy: ComparisonPolicy
    operator_trigger_id: str

    def __post_init__(self) -> None:
        for field_name in (
            "run_id",
            "correlation_id",
            "artifact_id",
            "artifact_version",
            "operator_trigger_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
