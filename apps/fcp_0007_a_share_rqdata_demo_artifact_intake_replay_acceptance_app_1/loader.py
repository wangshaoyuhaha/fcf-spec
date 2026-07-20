from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path

from .contracts import (
    REQUIRED_COLUMNS,
    AShareDailyBar,
    RQDataDemoLoadResult,
    RegisteredRQDataDemoArtifact,
    canonical_sha256,
)


def _normalize_leading_bom(text: str) -> tuple[str, int]:
    normalized_lines: list[str] = []
    count = 0
    for line in text.splitlines():
        while line.startswith("\ufeff"):
            line = line[1:]
            count += 1
        normalized_lines.append(line)
    return "\n".join(normalized_lines), count


def _integer(value: object, field_name: str) -> int:
    normalized = str(value).strip()
    if not normalized or not normalized.isdigit():
        raise ValueError(f"{field_name} must be an integer")
    return int(normalized)


def load_registered_rqdata_demo(
    file_path: str | Path,
    registration: RegisteredRQDataDemoArtifact,
) -> RQDataDemoLoadResult:
    if not isinstance(registration, RegisteredRQDataDemoArtifact):
        raise TypeError("registration must be RegisteredRQDataDemoArtifact")
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered local demo not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered demo byte length mismatch")
    source_sha256 = hashlib.sha256(raw).hexdigest()
    if source_sha256 != registration.artifact_sha256:
        raise ValueError("registered demo SHA-256 mismatch")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("registered demo must be UTF-8") from exc
    normalized, bom_count = _normalize_leading_bom(text)
    normalized_sha256 = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    reader = csv.DictReader(io.StringIO(normalized, newline=""))
    columns = tuple(reader.fieldnames or ())
    if columns != REQUIRED_COLUMNS:
        raise ValueError("registered demo CSV columns are not exact")
    rows: list[AShareDailyBar] = []
    for row_number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError("registered demo contains a malformed CSV row")
        rows.append(
            AShareDailyBar(
                row_number=row_number,
                instrument_id=row["order_book_id"],
                trade_date=row["date"],
                low=row["low"],
                open=row["open"],
                high=row["high"],
                limit_down=row["limit_down"],
                num_trades=_integer(row["num_trades"], "num_trades"),
                close=row["close"],
                limit_up=row["limit_up"],
                volume=_integer(row["volume"], "volume"),
                total_turnover=row["total_turnover"],
                source_artifact_sha256=source_sha256,
            )
        )
    if not rows:
        raise ValueError("registered demo CSV must not be empty")
    keys = tuple((item.instrument_id, item.trade_date) for item in rows)
    if len(keys) != len(set(keys)):
        raise ValueError("registered demo contains duplicate instrument dates")
    if keys != tuple(sorted(keys)):
        raise ValueError("registered demo rows must be chronologically ordered")
    payloads = [dict(item.as_payload()) for item in rows]
    rowset_sha256 = canonical_sha256(sorted(payloads, key=lambda item: (item["instrument_id"], item["trade_date"])))
    replay_sha256 = canonical_sha256(
        {
            "artifact_sha256": source_sha256,
            "rows": payloads,
            "schema": REQUIRED_COLUMNS,
        }
    )
    return RQDataDemoLoadResult(
        artifact=registration,
        columns=columns,
        rows=tuple(rows),
        repeated_bom_count=bom_count,
        normalized_csv_sha256=normalized_sha256,
        rowset_sha256=rowset_sha256,
        replay_sha256=replay_sha256,
    )
