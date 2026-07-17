from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from types import MappingProxyType
from typing import Mapping

from .contracts import decimal_value, identifier, utc
from .registry import HistoricalObservationRegistry


def _canonical_decimal(value: Decimal) -> str:
    return format(value, "f")


@dataclass(frozen=True)
class BaselineRequest:
    request_id: str
    instrument_id: str
    field_id: str
    as_of_utc: str
    window_size: int
    minimum_history: int
    quantiles: tuple[Decimal, ...] = (Decimal("0.25"), Decimal("0.5"), Decimal("0.75"))

    def __post_init__(self) -> None:
        for name in ("request_id", "instrument_id", "field_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "as_of_utc", utc(self.as_of_utc, "as_of_utc"))
        for name in ("window_size", "minimum_history"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 2:
                raise ValueError(f"{name} must be an integer of at least two")
        if self.minimum_history > self.window_size:
            raise ValueError("minimum_history cannot exceed window_size")
        quantiles = tuple(sorted({decimal_value(item, "quantile") for item in self.quantiles}))
        if not quantiles or any(item < 0 or item > 1 for item in quantiles):
            raise ValueError("quantiles must be within zero and one")
        object.__setattr__(self, "quantiles", quantiles)


@dataclass(frozen=True)
class HistoricalBaseline:
    request: BaselineRequest
    status: str
    observation_ids: tuple[str, ...]
    sample_count: int
    mean: Decimal | None
    variance: Decimal | None
    standard_deviation: Decimal | None
    quantile_values: Mapping[str, Decimal]
    replay_hash: str

    def __post_init__(self) -> None:
        allowed = {"READY", "INSUFFICIENT_HISTORY"}
        if self.status not in allowed:
            raise ValueError("invalid baseline status")
        if self.sample_count != len(self.observation_ids):
            raise ValueError("sample_count does not match observation ids")
        if len(self.replay_hash) != 64 or any(
            item not in "0123456789abcdef" for item in self.replay_hash
        ):
            raise ValueError("replay_hash must be lowercase SHA-256")
        metrics = (self.mean, self.variance, self.standard_deviation)
        if self.status == "READY" and any(item is None for item in metrics):
            raise ValueError("ready baseline requires statistics")
        if self.status == "INSUFFICIENT_HISTORY" and any(
            item is not None for item in metrics
        ):
            raise ValueError("abstained baseline cannot expose statistics")
        object.__setattr__(
            self, "quantile_values", MappingProxyType(dict(self.quantile_values))
        )

    def standardize(self, value: object) -> tuple[str, Decimal | None]:
        if self.status != "READY":
            return "INSUFFICIENT_HISTORY", None
        if self.standard_deviation == 0:
            return "ZERO_VARIANCE", None
        assert self.mean is not None and self.standard_deviation is not None
        return "READY", (decimal_value(value, "value") - self.mean) / self.standard_deviation


def build_historical_baseline(
    registry: HistoricalObservationRegistry,
    request: BaselineRequest,
) -> HistoricalBaseline:
    available = registry.available_before(
        instrument_id=request.instrument_id,
        field_id=request.field_id,
        as_of_utc=request.as_of_utc,
    )
    window = available[-request.window_size :]
    ids = tuple(item.observation_id for item in window)
    if len(window) < request.minimum_history:
        payload = {
            "ids": ids,
            "request_id": request.request_id,
            "status": "INSUFFICIENT_HISTORY",
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("ascii")
        ).hexdigest()
        return HistoricalBaseline(
            request,
            "INSUFFICIENT_HISTORY",
            ids,
            len(window),
            None,
            None,
            None,
            {},
            digest,
        )
    values = tuple(item.value for item in window)
    with localcontext() as context:
        context.prec = 34
        count = Decimal(len(values))
        mean = sum(values, Decimal(0)) / count
        variance = sum((item - mean) ** 2 for item in values) / count
        standard_deviation = variance.sqrt()
    ordered = tuple(sorted(values))
    quantile_values: dict[str, Decimal] = {}
    for quantile in request.quantiles:
        rank = int((quantile * len(ordered)).to_integral_value(rounding=ROUND_CEILING))
        index = max(1, rank) - 1
        quantile_values[_canonical_decimal(quantile)] = ordered[index]
    payload = {
        "request_id": request.request_id,
        "as_of_utc": request.as_of_utc,
        "ids": ids,
        "values": [_canonical_decimal(item) for item in values],
        "mean": _canonical_decimal(mean),
        "variance": _canonical_decimal(variance),
        "quantiles": {key: _canonical_decimal(value) for key, value in quantile_values.items()},
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    ).hexdigest()
    return HistoricalBaseline(
        request,
        "READY",
        ids,
        len(values),
        mean,
        variance,
        standard_deviation,
        quantile_values,
        digest,
    )
