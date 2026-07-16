from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .artifact_reader import VerifiedArtifactRead
from .contracts import ArtifactFormat


DEFAULT_MAX_NORMALIZED_RECORDS = 10_000
_CREDENTIAL_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "credential",
    "password",
    "private_key",
    "secret",
    "secret_key",
    "wallet_private_key",
}
_SENSITIVE_TEXT = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bAKIA[0-9A-Z]{16}\b"
)


class ArtifactNormalizationError(ValueError):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def _fail(reason_code: str) -> None:
    raise ArtifactNormalizationError(reason_code)


def _decode(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        _fail("artifact-encoding-not-utf8")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("json-duplicate-object-key")
        value[key] = item
    return value


def _reject_non_finite(value: str) -> None:
    _fail("json-non-finite-number")


def _json_records(text: str) -> list[dict[str, Any]]:
    try:
        raw = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_non_finite,
        )
    except ArtifactNormalizationError:
        raise
    except (json.JSONDecodeError, TypeError):
        _fail("json-parse-failed")
    if isinstance(raw, dict) and "rows" in raw:
        raw = raw["rows"]
    elif isinstance(raw, dict) and "items" in raw:
        raw = raw["items"]
    elif isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        _fail("json-root-must-contain-records")
    if not all(isinstance(item, dict) for item in raw):
        _fail("normalized-record-must-be-object")
    return raw


def _csv_records(text: str) -> list[dict[str, Any]]:
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        headers = reader.fieldnames
        if not headers or any(not str(item).strip() for item in headers):
            _fail("csv-header-invalid")
        normalized_headers = [str(item).strip() for item in headers]
        if len(normalized_headers) != len(set(normalized_headers)):
            _fail("csv-duplicate-header")
        records: list[dict[str, Any]] = []
        for row in reader:
            if None in row:
                _fail("csv-row-width-mismatch")
            records.append(
                {
                    header: "" if row.get(original) is None else str(row[original]).strip()
                    for header, original in zip(normalized_headers, headers)
                }
            )
        return records
    except ArtifactNormalizationError:
        raise
    except (csv.Error, TypeError):
        _fail("csv-parse-failed")


def _has_credential_material(value: Any, key: str | None = None) -> bool:
    normalized_key = "" if key is None else key.strip().lower().replace("-", "_")
    if normalized_key in _CREDENTIAL_KEYS and value not in (None, "", False):
        return True
    if isinstance(value, Mapping):
        return any(_has_credential_material(item, str(name)) for name, item in value.items())
    if isinstance(value, list):
        return any(_has_credential_material(item) for item in value)
    return isinstance(value, str) and _SENSITIVE_TEXT.search(value) is not None


def _validate_json_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            _fail("normalized-record-non-finite-number")
        return
    if isinstance(value, list):
        for item in value:
            _validate_json_value(item)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                _fail("normalized-record-key-invalid")
            _validate_json_value(item)
        return
    _fail("normalized-record-value-invalid")


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in sorted(value.items())})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class NormalizedArtifactEnvelope:
    source_id: str
    evidence_id: str
    artifact_format: ArtifactFormat
    artifact_sha256: str
    normalized_records_sha256: str
    records: tuple[Mapping[str, Any], ...]
    source_class: str
    trust_level: str
    license_type: str
    allowed_use: str
    freshness_status: str
    operator_review_required: bool = True
    credential_scan_status: str = "CLEAR"

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("normalized envelope records must not be empty")
        if not all(isinstance(item, MappingProxyType) for item in self.records):
            raise TypeError("normalized envelope records must be immutable mappings")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.credential_scan_status != "CLEAR":
            raise ValueError("credential_scan_status must be CLEAR")

    @property
    def record_count(self) -> int:
        return len(self.records)

    def as_payload(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "allowed_use": self.allowed_use,
                "artifact_format": self.artifact_format.value,
                "artifact_sha256": self.artifact_sha256,
                "credential_scan_status": self.credential_scan_status,
                "evidence_id": self.evidence_id,
                "freshness_status": self.freshness_status,
                "license_type": self.license_type,
                "normalized_records_sha256": self.normalized_records_sha256,
                "operator_review_required": self.operator_review_required,
                "record_count": self.record_count,
                "records": tuple(_thaw(item) for item in self.records),
                "source_class": self.source_class,
                "source_id": self.source_id,
                "trust_level": self.trust_level,
            }
        )


def normalize_verified_artifact(
    artifact: VerifiedArtifactRead,
    max_records: int = DEFAULT_MAX_NORMALIZED_RECORDS,
) -> NormalizedArtifactEnvelope:
    if not isinstance(artifact, VerifiedArtifactRead):
        raise TypeError("artifact must be a VerifiedArtifactRead")
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records <= 0:
        raise ValueError("max_records must be a positive integer")
    text = _decode(artifact.content)
    if artifact.source.artifact_format is ArtifactFormat.JSON:
        records = _json_records(text)
    elif artifact.source.artifact_format is ArtifactFormat.CSV:
        records = _csv_records(text)
    else:
        _fail("artifact-format-not-supported")
    if not records:
        _fail("artifact-records-empty")
    if len(records) > max_records:
        _fail("artifact-record-limit-exceeded")
    for record in records:
        _validate_json_value(record)
        if _has_credential_material(record):
            _fail("credential-material-detected")
    canonical = json.dumps(
        records,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    frozen_records = tuple(_freeze(item) for item in records)
    source = artifact.source
    return NormalizedArtifactEnvelope(
        source_id=source.source_id,
        evidence_id=source.evidence_id,
        artifact_format=source.artifact_format,
        artifact_sha256=artifact.receipt.actual_sha256 or "",
        normalized_records_sha256=hashlib.sha256(canonical).hexdigest(),
        records=frozen_records,
        source_class=source.source_class,
        trust_level=source.trust_level,
        license_type=source.license_type,
        allowed_use=source.allowed_use,
        freshness_status=source.freshness_status,
    )
