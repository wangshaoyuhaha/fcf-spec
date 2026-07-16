from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping

from .contracts import (
    AIReplayMode,
    PointInTimeEvidence,
    decimal_value,
    freeze,
    identifier,
    utc_time,
)


@dataclass(frozen=True)
class RegisteredAIReplay:
    replay_id: str
    mode: AIReplayMode
    as_of_time_utc: str
    model_role: str
    model_id: str
    model_version: str
    model_training_cutoff_status: str
    prompt_id: str
    prompt_version: str
    output_artifact_id: str
    registered_ai_score: Decimal
    deterministic_baseline_score: Decimal
    fact_alignment_score: Decimal
    evidence: tuple[PointInTimeEvidence, ...]
    model_invocation_performed: bool = False
    prompt_execution_performed: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "replay_id",
            "model_role",
            "model_id",
            "model_version",
            "prompt_id",
            "prompt_version",
            "output_artifact_id",
        ):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        mode = self.mode if isinstance(self.mode, AIReplayMode) else AIReplayMode(self.mode)
        object.__setattr__(self, "mode", mode)
        as_of = utc_time(self.as_of_time_utc, "as_of_time_utc")
        if self.model_training_cutoff_status not in {"KNOWN", "UNKNOWN"}:
            raise ValueError("model_training_cutoff_status must be KNOWN or UNKNOWN")
        for field_name in (
            "registered_ai_score",
            "deterministic_baseline_score",
            "fact_alignment_score",
        ):
            value = decimal_value(getattr(self, field_name), field_name)
            if not Decimal("0") <= value <= Decimal("1"):
                raise ValueError(f"{field_name} must be between 0 and 1")
            object.__setattr__(self, field_name, value)
        evidence = tuple(self.evidence)
        if not evidence:
            raise ValueError("registered AI replay evidence is required")
        if mode is AIReplayMode.HISTORICAL_REPRODUCTION:
            for item in evidence:
                if utc_time(item.available_at_utc, "available_at_utc") > as_of:
                    raise ValueError("historical AI replay contains future evidence")
        object.__setattr__(self, "evidence", evidence)
        if self.model_invocation_performed or self.prompt_execution_performed:
            raise ValueError("Stage 11 evaluates registered output only")


@dataclass(frozen=True)
class AIHistoricalEvaluation:
    replay_id: str
    status: str
    incremental_value: Decimal
    fact_alignment_score: Decimal
    leakage_detected: bool
    role_performance: Mapping[str, object]
    reason_codes: tuple[str, ...]
    advisory_only: bool = True
    model_invocation_performed: bool = False

    def __post_init__(self) -> None:
        if self.status not in {
            "PASS_REVIEW_REQUIRED",
            "DEGRADED_REVIEW_REQUIRED",
            "BLOCKED_REVIEW_REQUIRED",
        }:
            raise ValueError("unsupported AI evaluation status")
        object.__setattr__(self, "role_performance", freeze(self.role_performance))
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))
        if not self.advisory_only or self.model_invocation_performed:
            raise ValueError("AI historical evaluation must remain advisory")


class RegisteredAIHistoricalEvaluationService:
    def evaluate(self, replay: RegisteredAIReplay) -> AIHistoricalEvaluation:
        reasons = []
        leakage = False
        as_of = utc_time(replay.as_of_time_utc, "as_of_time_utc")
        for item in replay.evidence:
            if utc_time(item.available_at_utc, "available_at_utc") > as_of:
                leakage = True
                reasons.append("knowledge-leakage-detected")
        if replay.model_training_cutoff_status == "UNKNOWN":
            reasons.append("model-training-cutoff-unknown")
        if replay.fact_alignment_score < Decimal("0.80"):
            reasons.append("fact-alignment-below-policy")
        incremental = (
            replay.registered_ai_score - replay.deterministic_baseline_score
        )
        if incremental <= 0:
            reasons.append("no-positive-ai-incremental-value")
        status = (
            "BLOCKED_REVIEW_REQUIRED"
            if leakage
            else (
                "DEGRADED_REVIEW_REQUIRED"
                if reasons
                else "PASS_REVIEW_REQUIRED"
            )
        )
        return AIHistoricalEvaluation(
            replay_id=replay.replay_id,
            status=status,
            incremental_value=incremental,
            fact_alignment_score=replay.fact_alignment_score,
            leakage_detected=leakage,
            role_performance=MappingProxyType(
                {
                    "model_id": replay.model_id,
                    "model_role": replay.model_role,
                    "mode": replay.mode.value,
                    "output_artifact_id": replay.output_artifact_id,
                    "prompt_version": replay.prompt_version,
                }
            ),
            reason_codes=tuple(reasons),
        )
