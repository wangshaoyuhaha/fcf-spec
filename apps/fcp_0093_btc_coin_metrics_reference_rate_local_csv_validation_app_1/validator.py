from __future__ import annotations

import csv
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import hashlib
from io import StringIO
import json
from pathlib import Path
import re

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import (
    EXPECTED_CADENCE_SECONDS,
    EXPECTED_HEADER,
    CoinMetricsBTCReferenceCSVValidationRequest,
    CoinMetricsBTCReferenceCSVValidationResult,
)


_DECIMAL = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")


@dataclass(frozen=True)
class _ReferenceObservation:
    asset: str
    observed_at_utc: str
    reference_rate_usd: Decimal
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.asset != "btc":
            raise ValueError("asset must be btc")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        if (
            not isinstance(self.reference_rate_usd, Decimal)
            or not self.reference_rate_usd.is_finite()
            or self.reference_rate_usd <= 0
        ):
            raise ValueError("ReferenceRateUSD must be a positive finite decimal")
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "asset": self.asset,
                    "observed_at_utc": observed,
                    "reference_rate_usd": format(self.reference_rate_usd, "f"),
                }
            ),
        )


def _read_registered_bytes(
    file_path: str | Path,
    request: CoinMetricsBTCReferenceCSVValidationRequest,
) -> bytes:
    path = Path(file_path)
    if path.is_symlink():
        raise ValueError("registered reference CSV must not be a symlink")
    if not path.is_file():
        raise FileNotFoundError("registered reference CSV is not a regular file")
    if path.stat().st_size != request.registration.byte_length:
        raise ValueError("registered reference CSV byte length mismatch")
    raw = path.read_bytes()
    if len(raw) != request.registration.byte_length:
        raise ValueError("registered reference CSV changed while reading")
    if hashlib.sha256(raw).hexdigest() != request.registration.content_sha256:
        raise ValueError("registered reference CSV SHA-256 mismatch")
    return raw


def _parse_observations(
    raw: bytes,
    request: CoinMetricsBTCReferenceCSVValidationRequest,
) -> tuple[_ReferenceObservation, ...]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("registered reference CSV must not contain a BOM")
    if b"\x00" in raw:
        raise ValueError("registered reference CSV must not contain NUL bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("registered reference CSV must be UTF-8") from error
    if not text.endswith("\n"):
        raise ValueError("registered reference CSV must end with a newline")
    reader = csv.reader(StringIO(text, newline=""), strict=True)
    try:
        header = tuple(next(reader))
    except (StopIteration, csv.Error) as error:
        raise ValueError("registered reference CSV lacks a valid header") from error
    if header != request.expected_header:
        raise ValueError("registered reference CSV header mismatch")

    observations: list[_ReferenceObservation] = []
    try:
        for row_number, row in enumerate(reader, start=2):
            if not row or all(not value for value in row):
                raise ValueError(f"blank CSV row at line {row_number}")
            if len(row) != len(EXPECTED_HEADER):
                raise ValueError(f"CSV row width mismatch at line {row_number}")
            asset, observed_at, rate_lexeme = row
            if asset != request.expected_asset:
                raise ValueError(f"unexpected asset at line {row_number}")
            if _DECIMAL.fullmatch(rate_lexeme) is None:
                raise ValueError(f"invalid decimal lexeme at line {row_number}")
            try:
                rate = Decimal(rate_lexeme)
            except InvalidOperation as error:
                raise ValueError(f"invalid decimal at line {row_number}") from error
            observations.append(
                _ReferenceObservation(
                    asset=asset,
                    observed_at_utc=observed_at,
                    reference_rate_usd=rate,
                )
            )
    except csv.Error as error:
        raise ValueError("registered reference CSV is malformed") from error
    result = tuple(observations)
    if len(result) < 2:
        raise ValueError("registered reference CSV requires at least two rows")
    return result


def _validate_clocks(
    observations: tuple[_ReferenceObservation, ...],
    request: CoinMetricsBTCReferenceCSVValidationRequest,
) -> None:
    clocks = tuple(instant(item.observed_at_utc) for item in observations)
    if len(set(clocks)) != len(clocks):
        raise ValueError("registered reference CSV contains duplicate clocks")
    if clocks != tuple(sorted(clocks)):
        raise ValueError("registered reference CSV clocks are not ordered")
    if clocks[-1] > instant(request.as_of_utc):
        raise ValueError("registered reference CSV contains future observations")
    deltas = tuple(
        int((current - previous).total_seconds())
        for previous, current in zip(clocks, clocks[1:])
    )
    if not deltas or any(
        delta != request.expected_cadence_seconds for delta in deltas
    ):
        raise ValueError("registered reference CSV cadence mismatch")


def validate_registered_coin_metrics_btc_reference_csv(
    file_path: str | Path,
    request: CoinMetricsBTCReferenceCSVValidationRequest,
) -> CoinMetricsBTCReferenceCSVValidationResult:
    if not isinstance(request, CoinMetricsBTCReferenceCSVValidationRequest):
        raise TypeError("request must be typed")
    raw = _read_registered_bytes(file_path, request)
    observations = _parse_observations(raw, request)
    _validate_clocks(observations, request)
    return CoinMetricsBTCReferenceCSVValidationResult(
        source_artifact_id=request.registration.artifact_id,
        source_artifact_sha256=request.registration.content_sha256,
        source_byte_length=request.registration.byte_length,
        output_artifact_id=request.output_artifact_id,
        header_sha256=canonical_sha256(list(EXPECTED_HEADER)),
        observation_hashes_sha256=canonical_sha256(
            [item.observation_hash for item in observations]
        ),
        observation_count=len(observations),
        observation_start_utc=observations[0].observed_at_utc,
        observation_end_utc=observations[-1].observed_at_utc,
        cadence_seconds=EXPECTED_CADENCE_SECONDS,
        as_of_utc=request.as_of_utc,
    )


def render_validation_json(
    result: CoinMetricsBTCReferenceCSVValidationResult,
) -> str:
    if not isinstance(result, CoinMetricsBTCReferenceCSVValidationResult):
        raise TypeError("result must be typed")
    return json.dumps(
        result.to_record(),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def build_reference_result() -> CoinMetricsBTCReferenceCSVValidationResult:
    return CoinMetricsBTCReferenceCSVValidationResult(
        source_artifact_id="coin-metrics-btc-reference-source-v1",
        source_artifact_sha256=canonical_sha256("source-reference"),
        source_byte_length=391,
        output_artifact_id="coin-metrics-btc-reference-validation-v1",
        header_sha256=canonical_sha256(list(EXPECTED_HEADER)),
        observation_hashes_sha256=canonical_sha256("observation-reference"),
        observation_count=7,
        observation_start_utc="2026-07-22T22:00:00Z",
        observation_end_utc="2026-07-23T04:00:00Z",
        cadence_seconds=EXPECTED_CADENCE_SECONDS,
        as_of_utc="2026-07-23T04:10:00Z",
    )
