from dataclasses import dataclass, replace

from .contracts import HolidayLiquidityMeasurement, RegisteredHolidayLiquidityObservation


@dataclass(frozen=True)
class LocalHolidayLiquidityRegistry:
    observations: tuple[RegisteredHolidayLiquidityObservation, ...] = ()
    measurements: tuple[HolidayLiquidityMeasurement, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        observations, measurements = tuple(self.observations), tuple(self.measurements)
        if (
            isinstance(self.capacity, bool)
            or not 1 <= self.capacity <= 100000
            or len(observations) + len(measurements) > self.capacity
        ):
            raise ValueError("holiday liquidity registry capacity is invalid")
        if len({item.observation_id for item in observations}) != len(observations):
            raise ValueError("duplicate holiday observation id is prohibited")
        if len({item.observation_hash for item in observations}) != len(observations):
            raise ValueError("duplicate holiday observation evidence is prohibited")
        if len({item.measurement_id for item in measurements}) != len(measurements):
            raise ValueError("duplicate holiday measurement id is prohibited")
        hashes = {item.observation_hash for item in observations}
        if any(item.observation.observation_hash not in hashes for item in measurements):
            raise ValueError("measurement observation must be registered")
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "measurements", measurements)

    def append_observation(
        self, item: RegisteredHolidayLiquidityObservation
    ) -> "LocalHolidayLiquidityRegistry":
        if not isinstance(item, RegisteredHolidayLiquidityObservation):
            raise ValueError("registry accepts holiday observations only")
        return replace(self, observations=(*self.observations, item))

    def append_measurement(
        self, item: HolidayLiquidityMeasurement
    ) -> "LocalHolidayLiquidityRegistry":
        if not isinstance(item, HolidayLiquidityMeasurement):
            raise ValueError("registry accepts holiday measurements only")
        return replace(self, measurements=(*self.measurements, item))
