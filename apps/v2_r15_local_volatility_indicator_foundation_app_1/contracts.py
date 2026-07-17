from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    decimal_value,
    identifier,
    instant,
    utc,
)
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import (
    factor_ref,
    sha256_text,
)


VOLATILITY_INDICATOR_TYPES = ("AVERAGE_TRUE_RANGE", "TRUE_RANGE")
MAX_PRICE = Decimal("1E30")


@dataclass(frozen=True)
class RegisteredOHLCPoint:
    point_id: str
    instrument_id: str
    interval_id: str
    observed_at_utc: str
    available_at_utc: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    source_artifact_hash: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        for name in ("point_id", "instrument_id", "interval_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("OHLC availability precedes observation")
        for name in ("open", "high", "low", "close"):
            value = decimal_value(getattr(self, name), name)
            if value <= 0 or value > MAX_PRICE:
                raise ValueError(f"{name} is outside positive bounded scope")
            object.__setattr__(self, name, value)
        if not self.low <= self.open <= self.high:
            raise ValueError("open must be within low and high")
        if not self.low <= self.close <= self.high:
            raise ValueError("close must be within low and high")
        object.__setattr__(
            self,
            "source_artifact_hash",
            sha256_text(self.source_artifact_hash, "source_artifact_hash"),
        )
        if self.registered_local_only is not True:
            raise ValueError("OHLC point must remain registered and local")


@dataclass(frozen=True)
class RegisteredOHLCSeries:
    series_id: str
    points: tuple[RegisteredOHLCPoint, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "series_id", identifier(self.series_id, "series_id"))
        if not 1 <= len(self.points) <= 10000:
            raise ValueError("OHLC series size is invalid")
        identities = {(point.instrument_id, point.interval_id) for point in self.points}
        instants = tuple(instant(point.observed_at_utc) for point in self.points)
        point_ids = tuple(point.point_id for point in self.points)
        if len(identities) != 1:
            raise ValueError("OHLC series identity mismatch")
        if tuple(sorted(instants)) != instants or len(set(instants)) != len(instants):
            raise ValueError("OHLC observations must be unique and ordered")
        if len(set(point_ids)) != len(point_ids):
            raise ValueError("OHLC point identifiers must be unique")

    @property
    def instrument_id(self) -> str:
        return self.points[0].instrument_id

    @property
    def interval_id(self) -> str:
        return self.points[0].interval_id


@dataclass(frozen=True)
class VolatilityIndicatorPolicy:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    registry_id: str
    registry_version: str
    instrument_id: str
    interval_id: str
    window: int
    decimal_places: int = 6
    operator_registered: bool = True
    score_rank_or_signal_allowed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "indicator_id",
            "indicator_version",
            "registry_id",
            "registry_version",
            "instrument_id",
            "interval_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        indicator_type = str(self.indicator_type).strip().upper()
        if indicator_type not in VOLATILITY_INDICATOR_TYPES:
            raise ValueError("unsupported volatility indicator type")
        object.__setattr__(self, "indicator_type", indicator_type)
        object.__setattr__(
            self,
            "factor_definition_ref",
            factor_ref(self.factor_definition_ref, "factor_definition_ref"),
        )
        if isinstance(self.window, bool) or not 2 <= self.window <= 10000:
            raise ValueError("volatility indicator window is invalid")
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("volatility policy must be Operator-registered")
        if self.score_rank_or_signal_allowed:
            raise ValueError("volatility policy exceeds calculation-only scope")
