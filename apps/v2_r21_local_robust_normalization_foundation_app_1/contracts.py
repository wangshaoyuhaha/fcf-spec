from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import decimal_value, identifier, instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import factor_ref, sha256_text


MISSING_STATES = ("AVAILABLE", "NOT_APPLICABLE", "NOT_YET_PUBLISHED", "MISSING", "SOURCE_FAILURE")


@dataclass(frozen=True)
class RegisteredFactorPoint:
    point_id: str
    factor_definition_ref: str
    instrument_id: str
    observed_at_utc: str
    available_at_utc: str
    value: Decimal | None
    missing_state: str
    source_artifact_hash: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "point_id", identifier(self.point_id, "point_id"))
        object.__setattr__(self, "factor_definition_ref", factor_ref(self.factor_definition_ref, "factor_definition_ref"))
        object.__setattr__(self, "instrument_id", identifier(self.instrument_id, "instrument_id"))
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("factor availability precedes observation")
        state = str(self.missing_state).strip().upper()
        if state not in MISSING_STATES:
            raise ValueError("unsupported missing state")
        object.__setattr__(self, "missing_state", state)
        if state == "AVAILABLE":
            if self.value is None:
                raise ValueError("available factor point requires a value")
            object.__setattr__(self, "value", decimal_value(self.value, "value"))
        elif self.value is not None:
            raise ValueError("missing factor point cannot carry a value")
        object.__setattr__(self, "source_artifact_hash", sha256_text(self.source_artifact_hash, "source_artifact_hash"))
        if self.registered_local_only is not True:
            raise ValueError("factor point must remain registered and local")


@dataclass(frozen=True)
class RegisteredFactorSeries:
    series_id: str
    points: tuple[RegisteredFactorPoint, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "series_id", identifier(self.series_id, "series_id"))
        if not self.points:
            raise ValueError("factor series must be nonempty")
        if len({point.factor_definition_ref for point in self.points}) != 1:
            raise ValueError("factor series definition mismatch")
        ids = tuple(point.point_id for point in self.points)
        times = tuple(instant(point.observed_at_utc) for point in self.points)
        if len(set(ids)) != len(ids) or len(set(times)) != len(times) or tuple(sorted(times)) != times:
            raise ValueError("factor points must be unique and ordered")

    @property
    def factor_definition_ref(self) -> str:
        return self.points[0].factor_definition_ref


@dataclass(frozen=True)
class NormalizationPolicy:
    normalization_id: str
    normalization_version: str
    factor_definition_ref: str
    registry_id: str
    registry_version: str
    target_point_id: str
    minimum_samples: int
    mad_clip_multiplier: Decimal = Decimal("3")
    decimal_places: int = 6
    operator_registered: bool = True
    direction_weight_score_rank_allowed: bool = False

    def __post_init__(self) -> None:
        for name in ("normalization_id", "normalization_version", "registry_id", "registry_version", "target_point_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "factor_definition_ref", factor_ref(self.factor_definition_ref, "factor_definition_ref"))
        if isinstance(self.minimum_samples, bool) or not 3 <= self.minimum_samples <= 10000:
            raise ValueError("minimum_samples is invalid")
        multiplier = decimal_value(self.mad_clip_multiplier, "mad_clip_multiplier")
        if multiplier <= 0 or multiplier > 100:
            raise ValueError("MAD clip multiplier is invalid")
        object.__setattr__(self, "mad_clip_multiplier", multiplier)
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("normalization policy must be Operator-registered")
        if self.direction_weight_score_rank_allowed:
            raise ValueError("normalization policy exceeds metric-only scope")
