from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping


_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$"
)
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ArtifactFormat(str, Enum):
    CSV = "CSV"
    JSON = "JSON"


class GatewayReadStatus(str, Enum):
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"


def _require_identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def _require_sha256(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if _SHA256_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a SHA-256 digest")
    return normalized


def _require_utc_timestamp(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return normalized


def normalize_registered_relative_path(value: object) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError("relative_path is required")
    if "\\" in normalized:
        raise ValueError("relative_path must use POSIX separators")
    path = PurePosixPath(normalized)
    if path.is_absolute() or normalized.startswith("/"):
        raise ValueError("relative_path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("relative_path contains a prohibited segment")
    if any(":" in part for part in path.parts):
        raise ValueError("relative_path must not contain a drive or URI scheme")
    canonical = path.as_posix()
    if canonical != normalized:
        raise ValueError("relative_path must be canonical")
    return canonical


@dataclass(frozen=True)
class RegisteredArtifactSource:
    source_id: str
    evidence_id: str
    relative_path: str
    artifact_format: ArtifactFormat
    expected_sha256: str
    source_class: str
    trust_level: str
    license_type: str
    allowed_use: str
    freshness_status: str
    published_at_utc: str
    operator_review_required: bool = True
    credential_material_expected: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_id", "evidence_id"):
            object.__setattr__(
                self,
                field_name,
                _require_identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "relative_path",
            normalize_registered_relative_path(self.relative_path),
        )
        try:
            artifact_format = ArtifactFormat(self.artifact_format)
        except (TypeError, ValueError) as exc:
            raise ValueError("artifact_format must be CSV or JSON") from exc
        object.__setattr__(self, "artifact_format", artifact_format)
        expected_suffix = f".{artifact_format.value.lower()}"
        if not self.relative_path.lower().endswith(expected_suffix):
            raise ValueError("relative_path suffix must match artifact_format")
        object.__setattr__(
            self,
            "expected_sha256",
            _require_sha256(self.expected_sha256, "expected_sha256"),
        )
        for field_name in (
            "source_class",
            "trust_level",
            "license_type",
            "allowed_use",
            "freshness_status",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_identifier(getattr(self, field_name), field_name).upper(),
            )
        object.__setattr__(
            self,
            "published_at_utc",
            _require_utc_timestamp(self.published_at_utc, "published_at_utc"),
        )
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.credential_material_expected is not False:
            raise ValueError("registered artifacts must not expect credential material")

    def as_payload(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "allowed_use": self.allowed_use,
                "artifact_format": self.artifact_format.value,
                "credential_material_expected": self.credential_material_expected,
                "evidence_id": self.evidence_id,
                "expected_sha256": self.expected_sha256,
                "freshness_status": self.freshness_status,
                "license_type": self.license_type,
                "operator_review_required": self.operator_review_required,
                "published_at_utc": self.published_at_utc,
                "relative_path": self.relative_path,
                "source_class": self.source_class,
                "source_id": self.source_id,
                "trust_level": self.trust_level,
            }
        )


@dataclass(frozen=True)
class GatewayReadRequest:
    request_id: str
    correlation_id: str
    source_id: str
    requested_at_utc: str
    peer_host: str = "127.0.0.1"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in ("request_id", "correlation_id", "source_id"):
            object.__setattr__(
                self,
                field_name,
                _require_identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "requested_at_utc",
            _require_utc_timestamp(self.requested_at_utc, "requested_at_utc"),
        )
        if self.peer_host != "127.0.0.1":
            raise ValueError("gateway request peer must be exactly 127.0.0.1")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class GatewayReadReceipt:
    request_id: str
    correlation_id: str
    source_id: str
    evidence_id: str
    status: GatewayReadStatus
    artifact_format: ArtifactFormat
    actual_sha256: str | None
    byte_length: int | None
    blocking_reasons: tuple[str, ...] = ()
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "request_id",
            "correlation_id",
            "source_id",
            "evidence_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_identifier(getattr(self, field_name), field_name),
            )
        try:
            status = GatewayReadStatus(self.status)
            artifact_format = ArtifactFormat(self.artifact_format)
        except (TypeError, ValueError) as exc:
            raise ValueError("receipt enum value is invalid") from exc
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "artifact_format", artifact_format)
        reasons = tuple(sorted({_require_identifier(item, "blocking_reason") for item in self.blocking_reasons}))
        object.__setattr__(self, "blocking_reasons", reasons)
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if status is GatewayReadStatus.VERIFIED:
            object.__setattr__(
                self,
                "actual_sha256",
                _require_sha256(self.actual_sha256, "actual_sha256"),
            )
            if not isinstance(self.byte_length, int) or self.byte_length < 0:
                raise ValueError("verified receipt byte_length must be non-negative")
            if reasons:
                raise ValueError("verified receipt must not contain blocking reasons")
        else:
            if not reasons:
                raise ValueError("blocked receipt must contain a blocking reason")
            if self.actual_sha256 is not None or self.byte_length is not None:
                raise ValueError("blocked receipt must not expose artifact metadata")
