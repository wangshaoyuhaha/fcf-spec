from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent
from apps.v2_r25_local_causal_transmission_graph_foundation_app_1 import RegisteredCausalTransmissionGraph

SERIES_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")

def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()

def _decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool): raise ValueError(f"{name} must be finite")
    try: result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc: raise ValueError(f"{name} must be finite") from exc
    if not result.is_finite() or abs(result) > Decimal("1E30"): raise ValueError(f"{name} must be bounded")
    return result

def _mean(values: tuple[Decimal, ...]) -> Decimal:
    return sum(values, Decimal("0")) / Decimal(len(values))

def _covariance(left: tuple[Decimal, ...], right: tuple[Decimal, ...]) -> Decimal:
    lm, rm = _mean(left), _mean(right)
    return sum(((a - lm) * (b - rm) for a, b in zip(left, right)), Decimal("0")) / Decimal(len(left))

@dataclass(frozen=True)
class RegisteredFXTransmissionSeries:
    series_id: str
    subject_id: str
    market: str
    horizon: str
    observed_at_utc: str
    available_at_utc: str
    asset_returns: tuple[Decimal | str | int, ...]
    usd_cny_returns: tuple[Decimal | str | int, ...]
    usd_cnh_returns: tuple[Decimal | str | int, ...]
    dxy_returns: tuple[Decimal | str | int, ...]
    rate_changes: tuple[Decimal | str | int, ...]
    source_event: InstitutionalCalendarEvent
    causal_graph: RegisteredCausalTransmissionGraph | None = None
    series_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    series_hash: str = field(init=False)
    def __post_init__(self) -> None:
        for name in ("series_id", "subject_id", "market", "horizon"): object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("observed_at_utc", "available_at_utc"): object.__setattr__(self, name, utc(getattr(self, name), name))
        if not isinstance(self.source_event, InstitutionalCalendarEvent): raise ValueError("FX series requires registered R23 evidence")
        if instant(self.available_at_utc) < max(instant(self.observed_at_utc), instant(self.source_event.ingested_at_utc)): raise ValueError("series availability cannot precede evidence")
        if self.causal_graph is not None and not isinstance(self.causal_graph, RegisteredCausalTransmissionGraph): raise ValueError("causal_graph must be registered R25 evidence")
        state = str(self.series_state).strip().upper()
        if state not in SERIES_STATES: raise ValueError("series_state is not registered")
        object.__setattr__(self, "series_state", state)
        names = ("asset_returns", "usd_cny_returns", "usd_cnh_returns", "dxy_returns", "rate_changes")
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields); object.__setattr__(self, "missing_fields", missing)
        if state == "OBSERVED":
            values = [tuple(_decimal(item, name) for item in getattr(self, name)) for name in names]
            if len(values[0]) < 3 or len({len(items) for items in values}) != 1: raise ValueError("observed FX series requires equal length and at least three samples")
            for name, items in zip(names, values): object.__setattr__(self, name, items)
            if missing: raise ValueError("observed FX series cannot be missing")
        elif any(getattr(self, name) for name in names) or not missing: raise ValueError("non-observed FX series requires empty values and missing_fields")
        if self.operator_registered is not True: raise ValueError("FX series requires Operator registration")
        payload = {"available_at_utc": self.available_at_utc, "causal_graph_hash": None if self.causal_graph is None else self.causal_graph.graph_hash, "market": self.market, "missing_fields": list(missing), "observed_at_utc": self.observed_at_utc, "series_id": self.series_id, "series_state": state, "source_event_hash": self.source_event.record_hash, "subject_id": self.subject_id, "values": {name: [str(item) for item in getattr(self, name)] for name in names}}
        object.__setattr__(self, "series_hash", _hash(payload))

@dataclass(frozen=True)
class FXTransmissionSensitivityRecord:
    record_id: str
    series: RegisteredFXTransmissionSeries
    available_at_utc: str
    foreign_flow_inference: bool = False
    causal_conclusion: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    usd_cny_beta_bps: int = field(init=False)
    usd_cnh_beta_bps: int = field(init=False)
    dxy_beta_bps: int = field(init=False)
    rate_beta_bps: int = field(init=False)
    usd_cny_correlation_bps: int = field(init=False)
    record_hash: str = field(init=False)
    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id, "record_id"))
        if not isinstance(self.series, RegisteredFXTransmissionSeries) or self.series.series_state != "OBSERVED": raise ValueError("sensitivity requires observed registered FX series")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if instant(self.available_at_utc) < instant(self.series.available_at_utc): raise ValueError("sensitivity availability cannot precede series")
        asset = self.series.asset_returns
        metrics = []
        for values in (self.series.usd_cny_returns, self.series.usd_cnh_returns, self.series.dxy_returns, self.series.rate_changes):
            variance = _covariance(values, values)
            if variance == 0: raise ValueError("sensitivity driver variance must be positive")
            metrics.append(int(((_covariance(asset, values) / variance) * Decimal("10000")).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)))
        asset_var, fx_var = _covariance(asset, asset), _covariance(self.series.usd_cny_returns, self.series.usd_cny_returns)
        correlation = int(((_covariance(asset, self.series.usd_cny_returns) / (asset_var * fx_var).sqrt()) * Decimal("10000")).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
        for name, value in zip(("usd_cny_beta_bps", "usd_cnh_beta_bps", "dxy_beta_bps", "rate_beta_bps"), metrics): object.__setattr__(self, name, value)
        object.__setattr__(self, "usd_cny_correlation_bps", correlation)
        if self.foreign_flow_inference: raise ValueError("FX evidence cannot infer foreign flow")
        if self.causal_conclusion: raise ValueError("FX sensitivity cannot prove causation")
        if self.factor_activated: raise ValueError("FX sensitivity cannot activate a factor")
        if self.operator_registered is not True: raise ValueError("sensitivity requires Operator registration")
        object.__setattr__(self, "record_hash", _hash({"available_at_utc": self.available_at_utc, "correlation": correlation, "metrics": metrics, "record_id": self.record_id, "series_hash": self.series.series_hash}))
