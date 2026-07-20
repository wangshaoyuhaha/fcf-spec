from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path

from .contracts import (
    LocalCSVPreview,
    RegisteredLocalCSVArtifact,
    canonical_sha256,
)


def _normalize_leading_bom(text: str) -> tuple[str, int]:
    lines: list[str] = []
    count = 0
    for line in text.splitlines():
        while line.startswith("\ufeff"):
            line = line[1:]
            count += 1
        lines.append(line)
    return "\n".join(lines), count


def _validate_column(value: object) -> str:
    column = str(value).strip()
    if not column or len(column) > 128:
        raise ValueError("CSV columns must be nonempty and bounded")
    if any(ord(character) < 32 for character in column):
        raise ValueError("CSV columns cannot contain control characters")
    return column


def inspect_registered_local_csv(
    file_path: str | Path,
    registration: RegisteredLocalCSVArtifact,
) -> LocalCSVPreview:
    if not isinstance(registration, RegisteredLocalCSVArtifact):
        raise TypeError("registration must be RegisteredLocalCSVArtifact")
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered local CSV not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered local CSV byte length mismatch")
    source_sha256 = hashlib.sha256(raw).hexdigest()
    if source_sha256 != registration.artifact_sha256:
        raise ValueError("registered local CSV SHA-256 mismatch")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("registered local CSV must be UTF-8") from exc
    normalized, bom_count = _normalize_leading_bom(text)
    normalized_sha256 = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    reader = csv.reader(io.StringIO(normalized, newline=""))
    try:
        raw_columns = next(reader)
    except StopIteration as exc:
        raise ValueError("registered local CSV must not be empty") from exc
    columns = tuple(_validate_column(value) for value in raw_columns)
    if len(set(columns)) != len(columns):
        raise ValueError("registered local CSV columns must be unique")
    row_count = 0
    for row in reader:
        row_count += 1
        if row_count > 100_000:
            raise ValueError("registered local CSV exceeds preview row limit")
        if len(row) != len(columns):
            raise ValueError("registered local CSV row width mismatch")
    if row_count == 0:
        raise ValueError("registered local CSV requires at least one data row")
    schema_sha256 = canonical_sha256(
        {
            "columns": columns,
            "format": "CSV",
            "row_count": row_count,
        }
    )
    return LocalCSVPreview(
        artifact_id=registration.artifact_id,
        source_id=registration.source_id,
        source_artifact_sha256=source_sha256,
        normalized_csv_sha256=normalized_sha256,
        schema_sha256=schema_sha256,
        columns=columns,
        row_count=row_count,
        repeated_bom_count=bom_count,
        rights_state=registration.rights_state,
        retention_state=registration.retention_state,
    )
