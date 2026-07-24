from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
import json

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (
    RegisteredFactorRuntimeSnapshot,
)
from apps.fcp_0101_registered_technical_indicator_core_runtime_app_1.contracts import (
    canonical_sha256,
    decimal_value,
    instant,
    utc,
)
from apps.fcp_0103_registered_technical_indicator_catalog_runtime_app_1 import (
    ACCEPTED_CANDIDATE_KINDS,
)
from apps.fcp_0104_registered_volume_flow_indicator_runtime_app_1.runtime import (
    SUCCESSOR_KIND_SOURCES as VOLUME_FLOW_KIND_SOURCES,
)

from .contracts import (
    INDICATOR_KINDS,
    RUNTIME_SCHEMA_VERSION,
    PriceShapeBar,
    PriceShapeRequest,
    RegisteredPriceShapeArtifact,
    RegisteredPriceShapeSnapshot,
)


TOP_LEVEL_FIELDS = {
    "bars",
    "catalog_id",
    "catalog_version",
    "dataset_id",
    "dataset_version",
    "indicator_requests",
    "price_currency",
    "registry_id",
    "registry_version",
    "schema_version",
}
BAR_FIELDS = {"close", "is_suspended", "timestamp_utc"}
REQUEST_FIELDS = {
    "factor_ref",
    "indicator_kind",
    "request_id",
    "suspension_policy",
    "window",
}
SUCCESSOR_KIND_SOURCES = {
    **VOLUME_FLOW_KIND_SOURCES,
    **{kind: "FCP-0105" for kind in INDICATOR_KINDS},
}
_QUANTUM = Decimal("0.00000001")
_TWO = Decimal(2)


def _closed(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def _text(value: Decimal) -> str:
    rounded = value.quantize(_QUANTUM, rounding=ROUND_HALF_EVEN)
    text = format(rounded, "f").rstrip("0").rstrip(".")
    return text if text and text != "-0" else "0"


def _calculate(request: PriceShapeRequest, bars: list[PriceShapeBar]) -> str:
    eligible = [bar for bar in bars if not bar.is_suspended]
    if len(eligible) < request.window + 1:
        raise ValueError(f"{request.request_id} has insufficient eligible bars")
    selected = eligible[-(request.window + 1) :]
    history = [bar.close for bar in selected[:-1]]
    current = selected[-1].close
    with localcontext() as context:
        context.prec = 50
        mean = sum(history, Decimal(0)) / Decimal(request.window)
        variance = (
            sum(((value - mean) ** 2 for value in history), Decimal(0))
            / Decimal(request.window)
        )
        deviation = variance.sqrt()
        kind = request.indicator_kind
        if kind == "BOLLINGER_BAND_WIDTH":
            return _text((_TWO * _TWO * deviation) / mean)
        if kind == "BOLLINGER_Z_SCORE":
            if deviation == 0:
                raise ValueError(f"{request.request_id} has zero reference dispersion")
            return _text((current - mean) / deviation)
        if kind == "BOLLINGER_BREAKOUT":
            upper = mean + _TWO * deviation
            lower = mean - _TWO * deviation
            return "1" if current > upper else "-1" if current < lower else "0"
        if kind == "MOMENTUM":
            return _text(current - history[0])
        if kind == "MOVING_AVERAGE_SLOPE":
            current_mean = (
                sum((bar.close for bar in selected[1:]), Decimal(0))
                / Decimal(request.window)
            )
            return _text(current_mean - mean)
        if kind == "PRICE_DISTANCE_FROM_MOVING_AVERAGE":
            return _text(current / mean - Decimal(1))
        if kind == "PRIOR_HIGH_BREAKOUT":
            return "1" if current > max(history) else "0"
        if current > max(history):
            return "1"
        if current < min(history):
            return "-1"
        return "0"


def calculate_registered_price_shape_indicators(
    content: bytes,
    artifact: RegisteredPriceShapeArtifact,
    registry: RegisteredFactorRuntimeSnapshot,
    *,
    as_of_utc: str,
) -> RegisteredPriceShapeSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if type(registry) is not RegisteredFactorRuntimeSnapshot:
        raise TypeError("registry must be an exact runtime snapshot")
    if len(content) != artifact.byte_length:
        raise ValueError("artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("artifact must be ASCII JSON") from exc
    payload = _closed(payload, TOP_LEVEL_FIELDS, "dataset")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("schema version mismatch")
    if payload["price_currency"] != "CNY":
        raise ValueError("runtime requires registered CNY prices")
    if (
        payload["registry_id"] != registry.registry_id
        or payload["registry_version"] != registry.registry_version
    ):
        raise ValueError("registry identity mismatch")
    if payload["catalog_version"] != "v3":
        raise ValueError("catalog successor version must be v3")
    raw_bars = payload["bars"]
    if type(raw_bars) is not list or not raw_bars:
        raise ValueError("dataset must contain bars")
    bars = [
        PriceShapeBar(
            **{
                **_closed(raw, BAR_FIELDS, "bar"),
                "close": decimal_value(raw["close"], "close"),
            }
        )
        for raw in raw_bars
    ]
    timestamps = [bar.timestamp_utc for bar in bars]
    if timestamps != sorted(set(timestamps)):
        raise ValueError("bars must be unique and strictly time ordered")
    as_of = utc(as_of_utc, "as_of_utc")
    if any(instant(bar.timestamp_utc) > instant(as_of) for bar in bars):
        raise ValueError("dataset cannot contain future bars")
    raw_requests = payload["indicator_requests"]
    if type(raw_requests) is not list or not raw_requests:
        raise ValueError("dataset must contain requests")
    requests = [
        PriceShapeRequest(**_closed(raw, REQUEST_FIELDS, "request"))
        for raw in raw_requests
    ]
    request_ids = [request.request_id for request in requests]
    if request_ids != sorted(set(request_ids)):
        raise ValueError("requests must be unique and sorted")
    if {request.indicator_kind for request in requests} != set(INDICATOR_KINDS):
        raise ValueError("reference pack must cover every registered kind")
    for request in requests:
        if request.factor_ref not in registry.record_hashes:
            raise ValueError("factor is not registered")
        if request.factor_ref in registry.invalidated_factor_refs:
            raise ValueError("factor is invalidated")
    result_values = {
        request.request_id: {"value": _calculate(request, bars)}
        for request in requests
    }
    result_hashes = {
        request.request_id: canonical_sha256(
            {
                "factor_ref": request.factor_ref,
                "indicator_kind": request.indicator_kind,
                "result": result_values[request.request_id],
                "source_last_timestamp_utc": bars[-1].timestamp_utc,
                "suspension_policy": request.suspension_policy,
                "window": request.window,
            }
        )
        for request in requests
    }
    missing = tuple(
        sorted(set(ACCEPTED_CANDIDATE_KINDS) - set(SUCCESSOR_KIND_SOURCES))
    )
    return RegisteredPriceShapeSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        dataset_id=payload["dataset_id"],
        dataset_version=payload["dataset_version"],
        registry_id=registry.registry_id,
        registry_version=registry.registry_version,
        registry_snapshot_hash=registry.snapshot_hash,
        catalog_id=payload["catalog_id"],
        catalog_version=payload["catalog_version"],
        supported_kind_sources=SUCCESSOR_KIND_SOURCES,
        missing_candidate_kinds=missing,
        result_values=result_values,
        result_hashes=result_hashes,
        source_last_timestamp_utc=bars[-1].timestamp_utc,
        as_of_utc=as_of,
    )
