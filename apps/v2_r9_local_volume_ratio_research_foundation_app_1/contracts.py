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


VOLUME_BASES = ("INTERVAL", "CUMULATIVE")
BASELINE_STATISTICS = ("MEAN", "MEDIAN")
MAX_VOLUME = Decimal("1E30")


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class VolumeRatioPolicy:
    ratio_id: str
    ratio_version: str
    baseline_id: str
    baseline_version: str
    feature_id: str
    phase: str
    interval_id: str
    slot_index: int
    regime_id: str
    volume_basis: str
    baseline_statistic: str
    decimal_places: int = 6
    operator_registered: bool = True
    factor_activation_allowed: bool = False
    scoring_allowed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "ratio_id",
            "ratio_version",
            "baseline_id",
            "baseline_version",
            "feature_id",
            "interval_id",
            "regime_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        phase = str(self.phase).strip().upper()
        if phase not in SESSION_PHASES:
            raise ValueError("volume-ratio phase is not registered")
        object.__setattr__(self, "phase", phase)
        basis = str(self.volume_basis).strip().upper()
        if basis not in VOLUME_BASES:
            raise ValueError("volume basis must be INTERVAL or CUMULATIVE")
        object.__setattr__(self, "volume_basis", basis)
        statistic = str(self.baseline_statistic).strip().upper()
        if statistic not in BASELINE_STATISTICS:
            raise ValueError("baseline statistic must be MEAN or MEDIAN")
        object.__setattr__(self, "baseline_statistic", statistic)
        if isinstance(self.slot_index, bool) or self.slot_index < 0:
            raise ValueError("slot_index must be nonnegative")
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("volume-ratio policy must be Operator-registered")
        if self.factor_activation_allowed or self.scoring_allowed:
            raise ValueError("volume-ratio policy exceeds research-only scope")


@dataclass(frozen=True)
class RegisteredCurrentVolumeObservation:
    observation_id: str
    session_evidence_hash: str
    feature_id: str
    phase: str
    interval_id: str
    slot_index: int
    regime_id: str
    volume_basis: str
    observed_at_utc: str
    available_at_utc: str
    volume: Decimal
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
            raise ValueError("current-volume phase is not registered")
        object.__setattr__(self, "phase", phase)
        basis = str(self.volume_basis).strip().upper()
        if basis not in VOLUME_BASES:
            raise ValueError("volume basis must be INTERVAL or CUMULATIVE")
        object.__setattr__(self, "volume_basis", basis)
        if isinstance(self.slot_index, bool) or self.slot_index < 0:
            raise ValueError("slot_index must be nonnegative")
        object.__setattr__(
            self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc")
        )
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("current-volume availability precedes observation time")
        volume = decimal_value(self.volume, "volume")
        if volume < 0 or volume > MAX_VOLUME:
            raise ValueError("current volume must be between zero and 1E30")
        object.__setattr__(self, "volume", volume)
        object.__setattr__(
            self,
            "source_artifact_hash",
            _sha256(self.source_artifact_hash, "source_artifact_hash"),
        )
        if self.registered_local_only is not True:
            raise ValueError("current-volume observation must remain registered and local")
