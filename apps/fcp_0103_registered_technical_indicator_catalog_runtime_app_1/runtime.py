from __future__ import annotations

import hashlib
import json

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (
    RegisteredFactorRuntimeSnapshot,
)
from apps.v2_r12_local_technical_indicator_foundation_app_1.contracts import (
    INDICATOR_TYPES,
)
from apps.v2_r13_local_momentum_indicator_foundation_app_1.contracts import (
    MOMENTUM_INDICATOR_TYPES,
)
from apps.v2_r14_local_trend_indicator_foundation_app_1.contracts import (
    TREND_INDICATOR_TYPES,
)
from apps.v2_r15_local_volatility_indicator_foundation_app_1.contracts import (
    VOLATILITY_INDICATOR_TYPES,
)
from apps.v2_r16_local_range_channel_indicator_foundation_app_1.contracts import (
    CHANNEL_INDICATOR_TYPES,
)
from apps.v2_r17_local_stochastic_oscillator_foundation_app_1.contracts import (
    STOCHASTIC_INDICATOR_TYPES,
)
from apps.v2_r18_local_directional_trend_strength_foundation_app_1.contracts import (
    DIRECTIONAL_STRENGTH_TYPES,
)
from apps.v2_r19_local_percentage_price_oscillator_foundation_app_1.contracts import (
    PERCENTAGE_OSCILLATOR_TYPES,
)
from apps.v2_r20_local_triple_exponential_oscillator_foundation_app_1.contracts import (
    TRIX_TYPES,
)

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    IndicatorCatalogEntry,
    RegisteredIndicatorCatalogArtifact,
    RegisteredIndicatorCatalogSnapshot,
)


TOP_LEVEL_FIELDS = {
    "catalog_id",
    "catalog_version",
    "entries",
    "registry_id",
    "registry_version",
    "schema_version",
}
ENTRY_FIELDS = {"factor_ref", "foundation_ref", "indicator_kind"}

FOUNDATION_KIND_SOURCES = {
    **{
        ("BOLLINGER" if kind == "BOLLINGER_BANDS" else kind): "V2-R12"
        for kind in INDICATOR_TYPES
    },
    **{
        ("ROC" if kind == "RATE_OF_CHANGE" else kind): "V2-R13"
        for kind in MOMENTUM_INDICATOR_TYPES
    },
    **{kind: "V2-R14" for kind in TREND_INDICATOR_TYPES},
    **{
        ("ATR" if kind == "AVERAGE_TRUE_RANGE" else kind): "V2-R15"
        for kind in VOLATILITY_INDICATOR_TYPES
    },
    **{kind: "V2-R16" for kind in CHANNEL_INDICATOR_TYPES},
    **{kind: "V2-R17" for kind in STOCHASTIC_INDICATOR_TYPES},
    **{kind: "V2-R18" for kind in DIRECTIONAL_STRENGTH_TYPES},
    **{kind: "V2-R19" for kind in PERCENTAGE_OSCILLATOR_TYPES},
    **{kind: "V2-R20" for kind in TRIX_TYPES},
    "VWAP": "FCP-0101",
}

ACCEPTED_CANDIDATE_KINDS = tuple(
    sorted(
        {
            "ADX",
            "ATR",
            "BOLLINGER",
            "BOLLINGER_BAND_WIDTH",
            "BOLLINGER_BREAKOUT",
            "BOLLINGER_Z_SCORE",
            "CROSS_SECTIONAL_MOMENTUM",
            "DONCHIAN_CHANNEL",
            "EMA",
            "GAP_REVERSION",
            "GARMAN_KLASS_VOLATILITY",
            "HISTORICAL_VOLATILITY",
            "INDEX_RELATIVE_STRENGTH",
            "JUMP_VOLATILITY",
            "KDJ",
            "MACD",
            "MFI",
            "MOMENTUM",
            "MOVING_AVERAGE_ALIGNMENT",
            "MOVING_AVERAGE_SLOPE",
            "MULTI_PERIOD_VWAP",
            "NOTIONAL_VELOCITY",
            "OBV",
            "PARKINSON_VOLATILITY",
            "PPO",
            "PRICE_DISTANCE_FROM_MOVING_AVERAGE",
            "PRIOR_HIGH_BREAKOUT",
            "RANGE_BREAKOUT",
            "REALIZED_VOLATILITY",
            "RELATIVE_VOLUME",
            "RISK_ADJUSTED_MOMENTUM",
            "RISING_HIGHS_LOWS",
            "ROC",
            "RSI",
            "SAME_TIME_HISTORICAL_VOLUME",
            "SECTOR_RELATIVE_STRENGTH",
            "SHORT_REVERSAL",
            "SMA",
            "TIME_SERIES_MOMENTUM",
            "TREND_DURATION",
            "TRIX",
            "TRUE_RANGE",
            "TURNOVER_CHANGE",
            "VOLATILITY_ASYMMETRY",
            "VOLATILITY_EXPANSION",
            "VOLUME_CONCENTRATION_ZONE",
            "VOLUME_PRICE_DIVERGENCE",
            "VOLUME_PRICE_TREND",
            "VWAP",
            "VWAP_BREAKOUT",
            "VWAP_DEVIATION",
            "VWAP_RETEST",
            "VWAP_SLOPE",
        }
    )
)


def _closed(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def load_registered_indicator_catalog(
    content: bytes,
    artifact: RegisteredIndicatorCatalogArtifact,
    registry: RegisteredFactorRuntimeSnapshot,
    *,
    observed_at_utc: str,
) -> RegisteredIndicatorCatalogSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if type(registry) is not RegisteredFactorRuntimeSnapshot:
        raise TypeError("registry must be an exact runtime snapshot")
    if len(content) != artifact.byte_length:
        raise ValueError("catalog artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("catalog artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("catalog artifact must be ASCII JSON") from exc
    payload = _closed(payload, TOP_LEVEL_FIELDS, "catalog")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("catalog schema version mismatch")
    if (
        payload["registry_id"] != registry.registry_id
        or payload["registry_version"] != registry.registry_version
    ):
        raise ValueError("catalog registry identity mismatch")
    raw_entries = payload["entries"]
    if type(raw_entries) is not list or not raw_entries:
        raise ValueError("catalog entries must be a nonempty list")
    entries = tuple(
        IndicatorCatalogEntry(**_closed(item, ENTRY_FIELDS, "catalog entry"))
        for item in raw_entries
    )
    kinds = tuple(entry.indicator_kind for entry in entries)
    if len(set(kinds)) != len(kinds):
        raise ValueError("catalog indicator kinds must be unique")
    for entry in entries:
        if FOUNDATION_KIND_SOURCES.get(entry.indicator_kind) != entry.foundation_ref:
            raise ValueError("catalog foundation mapping is not registered")
        if entry.factor_ref not in registry.record_hashes:
            raise ValueError("catalog factor is not registered")
        if entry.factor_ref in registry.invalidated_factor_refs:
            raise ValueError("catalog factor is invalidated")
    sources = {entry.indicator_kind: entry.foundation_ref for entry in entries}
    factors = {entry.indicator_kind: entry.factor_ref for entry in entries}
    missing = tuple(sorted(set(ACCEPTED_CANDIDATE_KINDS) - set(kinds)))
    state = "CATALOG_PARTIAL" if missing else "CATALOG_READY"
    reasons = (
        ("REGISTERED_FOUNDATION_COVERAGE_PARTIAL", "MISSING_CANDIDATES_VISIBLE")
        if missing
        else ("REGISTERED_FOUNDATION_COVERAGE_COMPLETE",)
    )
    return RegisteredIndicatorCatalogSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        catalog_id=payload["catalog_id"],
        catalog_version=payload["catalog_version"],
        registry_id=registry.registry_id,
        registry_version=registry.registry_version,
        registry_snapshot_hash=registry.snapshot_hash,
        supported_kind_sources=sources,
        factor_refs=factors,
        missing_candidate_kinds=missing,
        reason_codes=reasons,
        observed_at_utc=observed_at_utc,
        state=state,
    )
