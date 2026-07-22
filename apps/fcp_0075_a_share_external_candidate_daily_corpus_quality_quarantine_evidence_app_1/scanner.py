from __future__ import annotations

import csv
import hashlib
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)

from .contracts import CandidateDailyCorpusQualityEvidence


EXPECTED_HEADER = (
    "\u80a1\u7968\u4ee3\u7801",
    "\u80a1\u7968\u540d\u79f0",
    "\u4ea4\u6613\u65e5\u671f",
    "\u5f00\u76d8\u4ef7",
    "\u6700\u9ad8\u4ef7",
    "\u6700\u4f4e\u4ef7",
    "\u6536\u76d8\u4ef7",
    "\u524d\u6536\u76d8\u4ef7",
    "\u6210\u4ea4\u91cf",
    "\u6210\u4ea4\u989d",
    "\u6d41\u901a\u5e02\u503c",
    "\u603b\u5e02\u503c",
    "\u6da8\u8dcc\u5e45",
    "\u6536\u76d8\u4ef7_\u590d\u6743",
    "\u5f00\u76d8\u4ef7_\u590d\u6743",
    "\u6700\u9ad8\u4ef7_\u590d\u6743",
    "\u6700\u4f4e\u4ef7_\u590d\u6743",
)
FILE_NAME = re.compile(r"^(bj|sh|sz)(\d{6})\.csv$")
HEADER_HASH = canonical_sha256({"header": list(EXPECTED_HEADER)})
FLOAT_TOLERANCE = 1e-9


def _decode(data: bytes, encoding: str | None = None) -> tuple[str, str]:
    if encoding is not None:
        return data.decode(encoding), encoding
    for candidate in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(candidate), candidate
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError("gb18030", data, 0, len(data), "unsupported encoding")


def _row(line: str) -> tuple[str, ...]:
    return tuple(next(csv.reader([line])))


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=FLOAT_TOLERANCE, abs_tol=FLOAT_TOLERANCE)


def scan_candidate_daily_corpus(
    root: Path,
    *,
    observed_at_utc: str,
    evidence_id: str = "a-share-external-candidate-daily-corpus-quality-v1",
) -> CandidateDailyCorpusQualityEvidence:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("candidate corpus root must be a real local directory")

    market_counts = Counter({"bj": 0, "sh": 0, "sz": 0, "other": 0})
    terminal_dates: list[str] = []
    all_dates: list[str] = []
    manifest_entries: list[dict[str, object]] = []
    metrics = Counter()

    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if entry.is_symlink() or not entry.is_file() or entry.suffix.lower() != ".csv":
            metrics["unexpected_entry_count"] += 1
            continue
        metrics["file_count"] += 1
        size = entry.stat().st_size
        metrics["total_bytes"] += size
        match = FILE_NAME.fullmatch(entry.name)
        market = match.group(1) if match else "other"
        market_counts[market] += 1
        if match is None:
            metrics["invalid_filename_count"] += 1

        content_hash = hashlib.sha256()
        encoding: str | None = None
        previous_date: date | None = None
        first_valid_ratio: float | None = None
        last_valid_ratio: float | None = None
        file_first_date: str | None = None
        file_last_date: str | None = None
        header_valid = False

        try:
            with entry.open("rb") as handle:
                for line_number, raw_line in enumerate(handle):
                    content_hash.update(raw_line)
                    try:
                        decoded, encoding = _decode(raw_line, encoding)
                        values = _row(decoded.rstrip("\r\n"))
                    except (UnicodeDecodeError, csv.Error):
                        if line_number == 0:
                            metrics["malformed_file_count"] += 1
                        else:
                            metrics["malformed_row_count"] += 1
                        continue
                    if line_number == 0:
                        header_valid = values == EXPECTED_HEADER
                        if not header_valid:
                            metrics["header_mismatch_file_count"] += 1
                        continue
                    if not header_valid:
                        continue
                    if len(values) != len(EXPECTED_HEADER):
                        metrics["malformed_row_count"] += 1
                        continue
                    try:
                        trade_date = date.fromisoformat(values[2])
                        numbers = tuple(float(value) for value in values[3:])
                    except (ValueError, OverflowError):
                        metrics["malformed_row_count"] += 1
                        continue
                    if any(not math.isfinite(value) for value in numbers):
                        metrics["malformed_row_count"] += 1
                        continue
                    metrics["row_count"] += 1
                    normalized_date = trade_date.isoformat()
                    all_dates.append(normalized_date)
                    file_first_date = file_first_date or normalized_date
                    file_last_date = normalized_date
                    if match is not None and values[0] != entry.stem:
                        metrics["code_mismatch_row_count"] += 1
                    if previous_date is not None:
                        if trade_date == previous_date:
                            metrics["duplicate_date_count"] += 1
                        elif trade_date < previous_date:
                            metrics["non_monotonic_date_count"] += 1
                    previous_date = trade_date

                    open_price, high, low, close, previous_close = numbers[:5]
                    volume, amount, float_market_value, total_market_value = numbers[5:9]
                    reported_return = numbers[9]
                    adjusted_close, adjusted_open, adjusted_high, adjusted_low = numbers[10:14]
                    raw_prices = (open_price, high, low, close, previous_close)
                    adjusted_prices = (adjusted_open, adjusted_high, adjusted_low, adjusted_close)
                    if (
                        any(value <= 0 for value in raw_prices)
                        or any(value <= 0 for value in adjusted_prices)
                        or high < max(open_price, low, close)
                        or low > min(open_price, high, close)
                        or adjusted_high < max(adjusted_open, adjusted_low, adjusted_close)
                        or adjusted_low > min(adjusted_open, adjusted_high, adjusted_close)
                    ):
                        metrics["invalid_ohlc_row_count"] += 1
                    if any(
                        value < 0
                        for value in (volume, amount, float_market_value, total_market_value)
                    ):
                        metrics["negative_numeric_row_count"] += 1
                    if volume == 0:
                        metrics["zero_volume_row_count"] += 1
                    expected_return = close / previous_close - 1.0
                    if not _close(reported_return, expected_return):
                        metrics["return_mismatch_row_count"] += 1
                    ratios = (
                        adjusted_open / open_price,
                        adjusted_high / high,
                        adjusted_low / low,
                        adjusted_close / close,
                    )
                    if any(not _close(ratios[0], ratio) for ratio in ratios[1:]):
                        metrics["adjustment_ratio_mismatch_row_count"] += 1
                    first_valid_ratio = first_valid_ratio if first_valid_ratio is not None else ratios[-1]
                    last_valid_ratio = ratios[-1]
        except OSError:
            metrics["malformed_file_count"] += 1

        manifest_entries.append(
            {"name": entry.name, "size": size, "sha256": content_hash.hexdigest()}
        )
        if file_first_date is not None and file_last_date is not None:
            terminal_dates.append(file_last_date)
            if first_valid_ratio is not None and _close(first_valid_ratio, 1.0):
                metrics["first_adjustment_ratio_unit_file_count"] += 1
            if last_valid_ratio is not None and not _close(last_valid_ratio, 1.0):
                metrics["terminal_adjustment_ratio_nonunit_file_count"] += 1

    if metrics["file_count"] == 0 or not all_dates or not terminal_dates:
        raise ValueError("candidate corpus contains no valid daily observations")
    latest_terminal = max(terminal_dates)
    latest_terminal_count = sum(value == latest_terminal for value in terminal_dates)
    stale_terminal_count = sum(value < latest_terminal for value in terminal_dates)
    return CandidateDailyCorpusQualityEvidence(
        evidence_id=evidence_id,
        observed_at_utc=observed_at_utc,
        manifest_hash=canonical_sha256({"entries": manifest_entries}),
        header_hash=HEADER_HASH,
        file_count=metrics["file_count"],
        total_bytes=metrics["total_bytes"],
        row_count=metrics["row_count"],
        market_file_counts=tuple((name, market_counts[name]) for name in ("bj", "sh", "sz", "other")),
        header_mismatch_file_count=metrics["header_mismatch_file_count"],
        invalid_filename_count=metrics["invalid_filename_count"],
        unexpected_entry_count=metrics["unexpected_entry_count"],
        malformed_file_count=metrics["malformed_file_count"],
        malformed_row_count=metrics["malformed_row_count"],
        code_mismatch_row_count=metrics["code_mismatch_row_count"],
        non_monotonic_date_count=metrics["non_monotonic_date_count"],
        duplicate_date_count=metrics["duplicate_date_count"],
        invalid_ohlc_row_count=metrics["invalid_ohlc_row_count"],
        negative_numeric_row_count=metrics["negative_numeric_row_count"],
        return_mismatch_row_count=metrics["return_mismatch_row_count"],
        adjustment_ratio_mismatch_row_count=metrics["adjustment_ratio_mismatch_row_count"],
        zero_volume_row_count=metrics["zero_volume_row_count"],
        earliest_trade_date=min(all_dates),
        latest_trade_date=max(all_dates),
        latest_terminal_date=latest_terminal,
        latest_terminal_file_count=latest_terminal_count,
        stale_terminal_file_count=stale_terminal_count,
        first_adjustment_ratio_unit_file_count=metrics["first_adjustment_ratio_unit_file_count"],
        terminal_adjustment_ratio_nonunit_file_count=metrics[
            "terminal_adjustment_ratio_nonunit_file_count"
        ],
    )
