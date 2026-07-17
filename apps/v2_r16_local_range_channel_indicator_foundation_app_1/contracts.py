from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import factor_ref


CHANNEL_INDICATOR_TYPES = ("DONCHIAN_CHANNEL",)


@dataclass(frozen=True)
class ChannelIndicatorPolicy:
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
    breakout_signal_allowed: bool = False
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
        if indicator_type not in CHANNEL_INDICATOR_TYPES:
            raise ValueError("unsupported channel indicator type")
        object.__setattr__(self, "indicator_type", indicator_type)
        object.__setattr__(
            self,
            "factor_definition_ref",
            factor_ref(self.factor_definition_ref, "factor_definition_ref"),
        )
        if isinstance(self.window, bool) or not 2 <= self.window <= 10000:
            raise ValueError("channel indicator window is invalid")
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("channel policy must be Operator-registered")
        if self.breakout_signal_allowed or self.score_rank_or_signal_allowed:
            raise ValueError("channel policy exceeds metric-only scope")
