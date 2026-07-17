from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import decimal_value, identifier, instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import factor_ref


INDICATOR_TYPES = ("BOLLINGER_BANDS", "SMA")
MAX_PRICE = Decimal("1E30")


@dataclass(frozen=True)
class RegisteredPricePoint:
    point_id: str
    instrument_id: str
    interval_id: str
    observed_at_utc: str
    available_at_utc: str
    close: Decimal
    source_artifact_hash: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import sha256_text

        for name in ("point_id", "instrument_id", "interval_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("price availability precedes observation")
        close = decimal_value(self.close, "close")
        if close <= 0 or close > MAX_PRICE:
            raise ValueError("close is outside positive bounded scope")
        object.__setattr__(self, "close", close)
        object.__setattr__(self, "source_artifact_hash", sha256_text(self.source_artifact_hash, "source_artifact_hash"))
        if self.registered_local_only is not True:
            raise ValueError("price point must remain registered and local")


@dataclass(frozen=True)
class RegisteredPriceSeries:
    series_id: str
    points: tuple[RegisteredPricePoint, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "series_id", identifier(self.series_id, "series_id"))
        if not self.points:
            raise ValueError("price series must be nonempty")
        identities = {(point.instrument_id, point.interval_id) for point in self.points}
        instants = tuple(instant(point.observed_at_utc) for point in self.points)
        point_ids = tuple(point.point_id for point in self.points)
        if len(identities) != 1:
            raise ValueError("price series identity mismatch")
        if tuple(sorted(instants)) != instants or len(set(instants)) != len(instants):
            raise ValueError("price series observations must be unique and ordered")
        if len(set(point_ids)) != len(point_ids):
            raise ValueError("price point identifiers must be unique")

    @property
    def instrument_id(self) -> str:
        return self.points[0].instrument_id

    @property
    def interval_id(self) -> str:
        return self.points[0].interval_id


@dataclass(frozen=True)
class TechnicalIndicatorPolicy:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    registry_id: str
    registry_version: str
    instrument_id: str
    interval_id: str
    window: int
    standard_deviation_multiplier: Decimal = Decimal("2")
    decimal_places: int = 6
    operator_registered: bool = True
    score_rank_or_signal_allowed: bool = False

    def __post_init__(self) -> None:
        for name in ("indicator_id", "indicator_version", "registry_id", "registry_version", "instrument_id", "interval_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        kind = str(self.indicator_type).strip().upper()
        if kind not in INDICATOR_TYPES:
            raise ValueError("unsupported technical indicator type")
        object.__setattr__(self, "indicator_type", kind)
        object.__setattr__(self, "factor_definition_ref", factor_ref(self.factor_definition_ref, "factor_definition_ref"))
        if isinstance(self.window, bool) or not 2 <= self.window <= 10000:
            raise ValueError("indicator window is invalid")
        multiplier = decimal_value(self.standard_deviation_multiplier, "standard_deviation_multiplier")
        if multiplier <= 0 or multiplier > Decimal("100"):
            raise ValueError("standard deviation multiplier is invalid")
        object.__setattr__(self, "standard_deviation_multiplier", multiplier)
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("indicator policy must be Operator-registered")
        if self.score_rank_or_signal_allowed:
            raise ValueError("indicator policy exceeds calculation-only scope")
