from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    decimal_value,
    identifier,
)


_DIRECTIONS = {"UP", "DOWN", "BOTH"}


@dataclass(frozen=True)
class AnomalyRule:
    rule_id: str
    rule_version: str
    context_id: str
    field_key: str
    direction: str
    minimum_abs_z: Decimal
    minimum_abs_velocity: Decimal
    minimum_persistence: int
    max_event_age_seconds: int
    cooldown_seconds: int
    evidence_ttl_seconds: int
    baseline_replay_hash: str
    negative_evidence_keys: tuple[str, ...] = ()
    target_label: str = "NONE"
    operator_registered: bool = True
    permanent_global_threshold: bool = False
    automatic_tuning_allowed: bool = False

    def __post_init__(self) -> None:
        for name in ("rule_id", "rule_version", "context_id", "field_key"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        if self.direction not in _DIRECTIONS:
            raise ValueError("direction is not allowed")
        minimum_abs_z = decimal_value(self.minimum_abs_z, "minimum_abs_z")
        minimum_abs_velocity = decimal_value(
            self.minimum_abs_velocity, "minimum_abs_velocity"
        )
        if minimum_abs_z <= 0 or minimum_abs_velocity < 0:
            raise ValueError("anomaly thresholds are outside the allowed range")
        object.__setattr__(self, "minimum_abs_z", minimum_abs_z)
        object.__setattr__(self, "minimum_abs_velocity", minimum_abs_velocity)
        for name, minimum in (
            ("minimum_persistence", 1),
            ("max_event_age_seconds", 1),
            ("evidence_ttl_seconds", 1),
            ("cooldown_seconds", 0),
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise ValueError(f"{name} is outside the allowed range")
        if self.minimum_persistence > 20:
            raise ValueError("minimum_persistence exceeds the bounded window")
        if len(self.baseline_replay_hash) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.baseline_replay_hash
        ):
            raise ValueError("baseline_replay_hash must be lowercase SHA-256")
        negative_keys = tuple(
            sorted(
                {
                    identifier(value, "negative_evidence_key")
                    for value in self.negative_evidence_keys
                }
            )
        )
        object.__setattr__(self, "negative_evidence_keys", negative_keys)
        if self.target_label != "NONE":
            raise ValueError("V2-R4 has no prediction target")
        if self.operator_registered is not True:
            raise ValueError("anomaly rules require Operator registration")
        if self.permanent_global_threshold or self.automatic_tuning_allowed:
            raise ValueError("global thresholds and automatic tuning are prohibited")
