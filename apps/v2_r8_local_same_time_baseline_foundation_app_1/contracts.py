from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    decimal_value,
    identifier,
    instant,
    utc,
)
from apps.v2_r7_local_market_session_registry_foundation_app_1 import SESSION_PHASES


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class SameTimeBaselinePolicy:
    baseline_id: str
    baseline_version: str
    feature_id: str
    phase: str
    interval_id: str
    slot_index: int
    regime_id: str
    minimum_samples: int
    missing_policy: str = "REJECT"
    outlier_policy: str = "NONE"
    operator_registered: bool = True
    factor_activation_allowed: bool = False
    scoring_allowed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "baseline_id",
            "baseline_version",
            "feature_id",
            "interval_id",
            "regime_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        phase = str(self.phase).strip().upper()
        if phase not in SESSION_PHASES:
            raise ValueError("baseline phase is not registered")
        object.__setattr__(self, "phase", phase)
        if isinstance(self.slot_index, bool) or self.slot_index < 0:
            raise ValueError("slot_index must be nonnegative")
        if isinstance(self.minimum_samples, bool) or not 2 <= self.minimum_samples <= 1000:
            raise ValueError("minimum_samples must be between 2 and 1000")
        if self.missing_policy != "REJECT" or self.outlier_policy != "NONE":
            raise ValueError("V2-R8 policies are fixed to REJECT and NONE")
        if self.operator_registered is not True:
            raise ValueError("baseline policy must be Operator-registered")
        if self.factor_activation_allowed or self.scoring_allowed:
            raise ValueError("baseline policy exceeds research-only scope")


@dataclass(frozen=True)
class RegisteredBaselineObservation:
    observation_id: str
    session_evidence_hash: str
    feature_id: str
    phase: str
    interval_id: str
    slot_index: int
    regime_id: str
    observed_at_utc: str
    available_at_utc: str
    value: Decimal
    source_artifact_hash: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        for name in ("observation_id", "feature_id", "interval_id", "regime_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(
            self,
            "session_evidence_hash",
            _sha256(self.session_evidence_hash, "session_evidence_hash"),
        )
        phase = str(self.phase).strip().upper()
        if phase not in SESSION_PHASES:
            raise ValueError("observation phase is not registered")
        object.__setattr__(self, "phase", phase)
        if isinstance(self.slot_index, bool) or self.slot_index < 0:
            raise ValueError("slot_index must be nonnegative")
        object.__setattr__(
            self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc")
        )
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("observation availability precedes observation time")
        object.__setattr__(self, "value", decimal_value(self.value, "value"))
        object.__setattr__(
            self,
            "source_artifact_hash",
            _sha256(self.source_artifact_hash, "source_artifact_hash"),
        )
        if self.registered_local_only is not True:
            raise ValueError("baseline observation must remain registered and local")
