from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
import json

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredBar,
    RegisteredIndicatorRequest,
    RegisteredIndicatorSnapshot,
    RegisteredMarketArtifact,
    canonical_sha256,
    decimal_value,
    instant,
    utc,
)


TOP_LEVEL_FIELDS = {
    "amount_currency",
    "bars",
    "dataset_id",
    "dataset_version",
    "indicator_requests",
    "schema_version",
    "volume_unit",
}
BAR_FIELDS = {
    "amount",
    "close",
    "high",
    "is_suspended",
    "low",
    "open",
    "timestamp_utc",
    "volume",
}
REQUEST_FIELDS = {
    "factor_id",
    "factor_version",
    "indicator_kind",
    "multiplier_bps",
    "request_id",
    "suspension_policy",
    "window",
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


def _mean(values: list[Decimal]) -> Decimal:
    return sum(values, Decimal(0)) / Decimal(len(values))


def _calculate(
    request: RegisteredIndicatorRequest,
    bars: list[RegisteredBar],
) -> dict[str, str]:
    eligible = [bar for bar in bars if not bar.is_suspended]
    required = request.window + (1 if request.indicator_kind in {"RSI", "ATR"} else 0)
    if len(eligible) < required:
        raise ValueError(f"{request.request_id} has insufficient eligible bars")
    closes = [bar.close for bar in eligible]
    window = request.window
    with localcontext() as context:
        context.prec = 50
        if request.indicator_kind == "SMA":
            return {"value": _text(_mean(closes[-window:]))}
        if request.indicator_kind == "EMA":
            value = _mean(closes[:window])
            alpha = Decimal(2) / Decimal(window + 1)
            for close in closes[window:]:
                value = alpha * close + (Decimal(1) - alpha) * value
            return {"value": _text(value)}
        if request.indicator_kind == "BOLLINGER":
            selected = closes[-window:]
            middle = _mean(selected)
            variance = _mean([(value - middle) ** 2 for value in selected])
            deviation = variance.sqrt()
            multiplier = Decimal(request.multiplier_bps) / Decimal(10000)
            return {
                "lower": _text(middle - multiplier * deviation),
                "middle": _text(middle),
                "stddev": _text(deviation),
                "upper": _text(middle + multiplier * deviation),
            }
        if request.indicator_kind == "RSI":
            selected = closes[-(window + 1):]
            changes = [
                selected[index] - selected[index - 1]
                for index in range(1, len(selected))
            ]
            gain = _mean([max(change, Decimal(0)) for change in changes])
            loss = _mean([max(-change, Decimal(0)) for change in changes])
            if gain == 0 and loss == 0:
                value = Decimal(50)
            elif loss == 0:
                value = Decimal(100)
            else:
                value = Decimal(100) - Decimal(100) / (
                    Decimal(1) + gain / loss
                )
            return {"value": _text(value)}
        if request.indicator_kind == "ATR":
            selected = eligible[-(window + 1):]
            ranges = []
            for index in range(1, len(selected)):
                bar = selected[index]
                prior_close = selected[index - 1].close
                ranges.append(
                    max(
                        bar.high - bar.low,
                        abs(bar.high - prior_close),
                        abs(bar.low - prior_close),
                    )
                )
            return {"value": _text(_mean(ranges))}
        selected = eligible[-window:]
        volume = sum((bar.volume for bar in selected), Decimal(0))
        if volume == 0:
            raise ValueError(f"{request.request_id} has zero eligible VWAP volume")
        amount = sum((bar.amount for bar in selected), Decimal(0))
        return {"value": _text(amount / volume)}


def calculate_registered_indicators(
    content: bytes,
    artifact: RegisteredMarketArtifact,
    *,
    as_of_utc: str,
) -> RegisteredIndicatorSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered market artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered market artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered market artifact must be ASCII JSON") from exc
    payload = _closed(payload, TOP_LEVEL_FIELDS, "market dataset")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered technical indicator schema mismatch")
    if payload["volume_unit"] != "SHARES" or payload["amount_currency"] != "CNY":
        raise ValueError("reference runtime requires registered SHARES and CNY units")
    raw_bars = payload["bars"]
    if type(raw_bars) is not list or not raw_bars:
        raise ValueError("market dataset must contain bars")
    bars = [
        RegisteredBar(
            **{
                **_closed(raw, BAR_FIELDS, "bar"),
                **{
                    name: decimal_value(raw[name], name)
                    for name in (
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "amount",
                    )
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
        raise ValueError("registered dataset cannot contain future bars")
    raw_requests = payload["indicator_requests"]
    if type(raw_requests) is not list or not raw_requests:
        raise ValueError("market dataset must contain indicator requests")
    requests = [
        RegisteredIndicatorRequest(
            **_closed(raw, REQUEST_FIELDS, "indicator request")
        )
        for raw in raw_requests
    ]
    request_ids = [request.request_id for request in requests]
    if request_ids != sorted(set(request_ids)):
        raise ValueError("indicator requests must be unique and sorted")
    result_values = {
        request.request_id: _calculate(request, bars) for request in requests
    }
    result_hashes = {
        request.request_id: canonical_sha256(
            {
                "factor_id": request.factor_id,
                "factor_version": request.factor_version,
                "indicator_kind": request.indicator_kind,
                "result": result_values[request.request_id],
                "source_last_timestamp_utc": bars[-1].timestamp_utc,
                "suspension_policy": request.suspension_policy,
                "window": request.window,
            }
        )
        for request in requests
    }
    return RegisteredIndicatorSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        dataset_id=payload["dataset_id"],
        dataset_version=payload["dataset_version"],
        result_values=result_values,
        result_hashes=result_hashes,
        source_last_timestamp_utc=bars[-1].timestamp_utc,
        as_of_utc=as_of,
    )
