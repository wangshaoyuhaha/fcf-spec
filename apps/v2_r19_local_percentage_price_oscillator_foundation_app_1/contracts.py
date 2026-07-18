from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import factor_ref


PERCENTAGE_OSCILLATOR_TYPES = ("PPO",)


@dataclass(frozen=True)
class PercentageOscillatorPolicy:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    registry_id: str
    registry_version: str
    instrument_id: str
    interval_id: str
    fast_window: int
    slow_window: int
    signal_window: int
    decimal_places: int = 6
    operator_registered: bool = True
    direction_label_allowed: bool = False
    threshold_or_crossover_allowed: bool = False
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
        if indicator_type not in PERCENTAGE_OSCILLATOR_TYPES:
            raise ValueError("unsupported percentage oscillator type")
        object.__setattr__(self, "indicator_type", indicator_type)
        object.__setattr__(
            self,
            "factor_definition_ref",
            factor_ref(self.factor_definition_ref, "factor_definition_ref"),
        )
        for name in ("fast_window", "slow_window", "signal_window"):
            value = getattr(self, name)
            if isinstance(value, bool) or not 2 <= value <= 10000:
                raise ValueError(f"{name} is invalid")
        if self.fast_window >= self.slow_window:
            raise ValueError("PPO fast_window must be less than slow_window")
        if self.slow_window + self.signal_window - 1 > 10000:
            raise ValueError("PPO warm-up exceeds bounded scope")
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("percentage oscillator policy must be Operator-registered")
        if any(
            (
                self.direction_label_allowed,
                self.threshold_or_crossover_allowed,
                self.score_rank_or_signal_allowed,
            )
        ):
            raise ValueError("percentage oscillator policy exceeds metric-only scope")
