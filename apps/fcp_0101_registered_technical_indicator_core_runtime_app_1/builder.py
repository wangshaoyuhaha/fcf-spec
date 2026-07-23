from __future__ import annotations

import hashlib
import json

from .contracts import RegisteredIndicatorSnapshot, RegisteredMarketArtifact
from .runtime import calculate_registered_indicators


REFERENCE_AS_OF_UTC = "2026-07-24T02:20:00Z"


def _bar(
    minute: int,
    open_price: str,
    high: str,
    low: str,
    close: str,
    volume: str,
    amount: str,
    suspended: bool = False,
) -> dict[str, object]:
    return {
        "amount": amount,
        "close": close,
        "high": high,
        "is_suspended": suspended,
        "low": low,
        "open": open_price,
        "timestamp_utc": f"2026-07-24T02:{minute:02d}:00Z",
        "volume": volume,
    }


def _request(
    request_id: str,
    kind: str,
    *,
    multiplier_bps: int = 0,
) -> dict[str, object]:
    return {
        "factor_id": f"factor.technical.{kind.lower()}",
        "factor_version": "v1",
        "indicator_kind": kind,
        "multiplier_bps": multiplier_bps,
        "request_id": request_id,
        "suspension_policy": "EXCLUDE",
        "window": 3,
    }


def build_reference_artifact_bytes() -> bytes:
    payload = {
        "amount_currency": "CNY",
        "bars": [
            _bar(0, "10", "12", "9", "11", "100", "1100"),
            _bar(1, "11", "13", "10", "12", "110", "1320"),
            _bar(2, "12", "14", "11", "13", "120", "1560"),
            _bar(3, "13", "13", "13", "13", "0", "0", True),
            _bar(4, "13", "15", "12", "14", "130", "1820"),
            _bar(5, "14", "16", "13", "15", "140", "2100"),
            _bar(6, "15", "17", "14", "16", "150", "2400"),
        ],
        "dataset_id": "dataset.ashare.SH600000.reference",
        "dataset_version": "v1",
        "indicator_requests": [
            _request("request.atr", "ATR"),
            _request("request.bollinger", "BOLLINGER", multiplier_bps=20000),
            _request("request.ema", "EMA"),
            _request("request.rsi", "RSI"),
            _request("request.sma", "SMA"),
            _request("request.vwap", "VWAP"),
        ],
        "schema_version": "fcf-registered-technical-indicator-core-runtime-v1",
        "volume_unit": "SHARES",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_indicator_snapshot() -> RegisteredIndicatorSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredMarketArtifact(
        artifact_id="registered-technical-indicator-reference-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T02:10:00Z",
    )
    return calculate_registered_indicators(
        content,
        artifact,
        as_of_utc=REFERENCE_AS_OF_UTC,
    )


def render_indicator_snapshot_json(snapshot: RegisteredIndicatorSnapshot) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "as_of_utc": snapshot.as_of_utc,
            "dataset_id": snapshot.dataset_id,
            "dataset_version": snapshot.dataset_version,
            "deterministic_engine_authority": (
                snapshot.deterministic_engine_authority
            ),
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "result_hashes": dict(snapshot.result_hashes),
            "result_values": {
                key: dict(value) for key, value in snapshot.result_values.items()
            },
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
            "source_last_timestamp_utc": snapshot.source_last_timestamp_utc,
        },
        indent=2,
        sort_keys=True,
    )
