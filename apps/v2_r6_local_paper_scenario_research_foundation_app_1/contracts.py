from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    decimal_value,
    identifier,
    instant,
    utc,
)


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class PaperScenarioPolicy:
    scenario_id: str
    scenario_version: str
    research_direction: str
    horizon_seconds: int
    cost_assumption_bps: Decimal
    minimum_points: int
    target_label: str = "REGISTERED_PATH_RETURN"
    operator_registered: bool = True
    market_calibrated: bool = False
    virtual_account_allowed: bool = False
    paper_order_allowed: bool = False
    leverage_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "scenario_id", identifier(self.scenario_id, "scenario_id")
        )
        object.__setattr__(
            self,
            "scenario_version",
            identifier(self.scenario_version, "scenario_version"),
        )
        direction = str(self.research_direction).strip().upper()
        if direction not in {"UP", "DOWN"}:
            raise ValueError("research_direction must be UP or DOWN")
        object.__setattr__(self, "research_direction", direction)
        if isinstance(self.horizon_seconds, bool) or not 1 <= self.horizon_seconds <= 86400:
            raise ValueError("horizon_seconds must be between 1 and 86400")
        cost = decimal_value(self.cost_assumption_bps, "cost_assumption_bps")
        object.__setattr__(self, "cost_assumption_bps", cost)
        if cost < 0 or cost > 1000:
            raise ValueError("cost assumption must be between zero and 1000 bps")
        if isinstance(self.minimum_points, bool) or not 2 <= self.minimum_points <= 1000:
            raise ValueError("minimum_points must be between 2 and 1000")
        if self.target_label != "REGISTERED_PATH_RETURN":
            raise ValueError("V2-R6 target label is fixed")
        if self.operator_registered is not True or self.market_calibrated is not False:
            raise ValueError("scenario policy must be Operator-registered and uncalibrated")
        if self.virtual_account_allowed or self.paper_order_allowed or self.leverage_allowed:
            raise ValueError("scenario policy exceeds research-only scope")


@dataclass(frozen=True)
class RegisteredObservationPoint:
    point_id: str
    sequence: int
    observed_at_utc: str
    available_at_utc: str
    price: Decimal
    source_artifact_hash: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "point_id", identifier(self.point_id, "point_id"))
        if isinstance(self.sequence, bool) or self.sequence <= 0:
            raise ValueError("observation sequence must be positive")
        object.__setattr__(
            self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc")
        )
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("observation availability precedes observation time")
        price = decimal_value(self.price, "price")
        object.__setattr__(self, "price", price)
        if price <= 0:
            raise ValueError("observation price must be positive")
        object.__setattr__(
            self,
            "source_artifact_hash",
            _sha256(self.source_artifact_hash, "source_artifact_hash"),
        )
        if self.registered_local_only is not True:
            raise ValueError("observation point must remain registered and local")
