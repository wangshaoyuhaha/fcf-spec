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
    FOUNDATION_KIND_SOURCES,
)

from .contracts import (
    INDICATOR_KINDS,
    RUNTIME_SCHEMA_VERSION,
    RegisteredVolumeFlowArtifact,
    RegisteredVolumeFlowSnapshot,
    VolumeFlowBar,
    VolumeFlowRequest,
)


TOP_LEVEL_FIELDS = {
    "amount_currency",
    "bars",
    "catalog_id",
    "catalog_version",
    "dataset_id",
    "dataset_version",
    "indicator_requests",
    "registry_id",
    "registry_version",
    "schema_version",
    "volume_unit",
}
BAR_FIELDS = {
    "amount",
    "close",
    "high",
    "is_suspended",
    "low",
    "timestamp_utc",
    "volume",
}
REQUEST_FIELDS = {
    "factor_ref",
    "indicator_kind",
    "request_id",
    "suspension_policy",
    "window",
}
SUCCESSOR_KIND_SOURCES = {
    **FOUNDATION_KIND_SOURCES,
    "MFI": "FCP-0104",
    "OBV": "FCP-0104",
    "VOLUME_PRICE_TREND": "FCP-0104",
}
_QUANTUM = Decimal("0.00000001")


def _closed(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def _text(value: Decimal) -> str:
    rounded = value.quantize(_QUANTUM, rounding=ROUND_HALF_EVEN)
    text = format(rounded, "f").rstrip("0").rstrip(".")
    return text if text and text != "-0" else "0"


def _calculate(request: VolumeFlowRequest, bars: list[VolumeFlowBar]) -> str:
    eligible = [bar for bar in bars if not bar.is_suspended]
    if len(eligible) < request.window + 1:
        raise ValueError(f"{request.request_id} has insufficient eligible bars")
    selected = eligible[-(request.window + 1) :]
    with localcontext() as context:
        context.prec = 50
        if request.indicator_kind == "OBV":
            value = Decimal(0)
            for previous, current in zip(selected, selected[1:]):
                if current.close > previous.close:
                    value += current.volume
                elif current.close < previous.close:
                    value -= current.volume
            return _text(value)
        if request.indicator_kind == "VOLUME_PRICE_TREND":
            value = Decimal(0)
            for previous, current in zip(selected, selected[1:]):
                value += current.volume * (
                    (current.close - previous.close) / previous.close
                )
            return _text(value)
        typical = [
            (bar.high + bar.low + bar.close) / Decimal(3) for bar in selected
        ]
        positive = Decimal(0)
        negative = Decimal(0)
        for index in range(1, len(selected)):
            flow = typical[index] * selected[index].volume
            if typical[index] > typical[index - 1]:
                positive += flow
            elif typical[index] < typical[index - 1]:
                negative += flow
        if positive == 0 and negative == 0:
            return _text(Decimal(50))
        if negative == 0:
            return _text(Decimal(100))
        if positive == 0:
            return _text(Decimal(0))
        return _text(Decimal(100) - Decimal(100) / (Decimal(1) + positive / negative))


def calculate_registered_volume_flow_indicators(
    content: bytes,
    artifact: RegisteredVolumeFlowArtifact,
    registry: RegisteredFactorRuntimeSnapshot,
    *,
    as_of_utc: str,
) -> RegisteredVolumeFlowSnapshot:
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
    if payload["volume_unit"] != "SHARES" or payload["amount_currency"] != "CNY":
        raise ValueError("runtime requires registered SHARES and CNY units")
    if (
        payload["registry_id"] != registry.registry_id
        or payload["registry_version"] != registry.registry_version
    ):
        raise ValueError("registry identity mismatch")
    if payload["catalog_version"] != "v2":
        raise ValueError("catalog successor version must be v2")
    raw_bars = payload["bars"]
    if type(raw_bars) is not list or not raw_bars:
        raise ValueError("dataset must contain bars")
    bars = [
        VolumeFlowBar(
            **{
                **_closed(raw, BAR_FIELDS, "bar"),
                **{
                    name: decimal_value(raw[name], name)
                    for name in ("high", "low", "close", "volume", "amount")
                },
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
        VolumeFlowRequest(**_closed(raw, REQUEST_FIELDS, "request"))
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
    return RegisteredVolumeFlowSnapshot(
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
