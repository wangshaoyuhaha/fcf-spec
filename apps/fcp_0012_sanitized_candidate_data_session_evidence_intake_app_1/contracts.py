from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1.contracts import (
    require_identifier,
)


ALLOWED_LICENSE_CLASSES = ("COMMERCIAL", "DEMO", "TRIAL", "UNKNOWN")
ALLOWED_PROBE_KINDS = ("DAILY_BAR", "MINUTE_BAR", "ORDER_BOOK", "TICK")
ALLOWED_PROBE_STATUSES = ("FAILED", "SUCCEEDED")
FORBIDDEN_KEY_FRAGMENTS = (
    "account",
    "authorization",
    "credential",
    "id-card",
    "license-key",
    "password",
    "phone",
    "secret",
    "token",
    "username",
)


def canonical_sha256(value: object) -> str:
    if isinstance(value, Mapping):
        value = dict(value)
    payload = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def require_sha256(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError(f"{field_name} must be a SHA-256 digest")
    return normalized


def require_utc(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be UTC") from exc
    if not normalized.endswith("Z") or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return normalized


@dataclass(frozen=True)
class RegisteredSessionEvidenceArtifact:
    artifact_id: str
    artifact_path: str
    artifact_sha256: str
    byte_length: int
    candidate_id: str
    evidence_id: str
    source_kind: str = "OPERATOR_SANITIZED_LOCAL_SESSION_OBSERVATION"
    usage_scope: str = "LOCAL_EVALUATION_ONLY"
    credentials_committed: bool = False
    raw_market_values_committed: bool = False
    network_used_by_sidecar: bool = False
    provider_selected: bool = False
    entitlement_state: str = "UNRESOLVED"
    retention_state: str = "UNRESOLVED"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", require_identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "evidence_id", require_identifier(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "artifact_sha256", require_sha256(self.artifact_sha256, "artifact_sha256"))
        if self.artifact_path != "FCF_LOCAL_ARTIFACT_FCP_0012_RQDATA_TRIAL_SESSION.json":
            raise ValueError("artifact_path must be the registered local artifact")
        if not isinstance(self.byte_length, int) or not 1 <= self.byte_length <= 65536:
            raise ValueError("byte_length is outside the bounded artifact limit")
        fixed = (
            self.source_kind == "OPERATOR_SANITIZED_LOCAL_SESSION_OBSERVATION",
            self.usage_scope == "LOCAL_EVALUATION_ONLY",
            self.credentials_committed is False,
            self.raw_market_values_committed is False,
            self.network_used_by_sidecar is False,
            self.provider_selected is False,
            self.entitlement_state == "UNRESOLVED",
            self.retention_state == "UNRESOLVED",
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("registered session evidence boundary cannot be weakened")


@dataclass(frozen=True)
class ReadOnlyProbeEvidence:
    kind: str
    status: str
    instrument_count: int
    row_count: int
    first_date: str | None
    last_date: str | None

    def __post_init__(self) -> None:
        kind = str(self.kind).strip().upper()
        status = str(self.status).strip().upper()
        if kind not in ALLOWED_PROBE_KINDS:
            raise ValueError("probe kind is not registered")
        if status not in ALLOWED_PROBE_STATUSES:
            raise ValueError("probe status is invalid")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "status", status)
        if not isinstance(self.instrument_count, int) or not 0 <= self.instrument_count <= 1000:
            raise ValueError("instrument_count is outside the bounded range")
        if not isinstance(self.row_count, int) or not 0 <= self.row_count <= 1000000:
            raise ValueError("row_count is outside the bounded range")
        for field_name in ("first_date", "last_date"):
            value = getattr(self, field_name)
            if value is not None:
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be an ISO date") from exc
        if status == "SUCCEEDED" and (self.row_count < 1 or self.first_date is None or self.last_date is None):
            raise ValueError("successful probe requires bounded rows and dates")
        if self.first_date and self.last_date and self.first_date > self.last_date:
            raise ValueError("probe date range is reversed")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "first_date": self.first_date,
                "instrument_count": self.instrument_count,
                "kind": self.kind,
                "last_date": self.last_date,
                "row_count": self.row_count,
                "status": self.status,
            }
        )


@dataclass(frozen=True)
class CandidateSessionEvidence:
    candidate_id: str
    captured_at_utc: str
    license_class: str
    remaining_days: int
    quota_limit_bytes: int
    quota_used_bytes: int
    probe: ReadOnlyProbeEvidence
    source_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "captured_at_utc", require_utc(self.captured_at_utc, "captured_at_utc"))
        license_class = str(self.license_class).strip().upper()
        if license_class not in ALLOWED_LICENSE_CLASSES:
            raise ValueError("license_class is invalid")
        object.__setattr__(self, "license_class", license_class)
        if not isinstance(self.remaining_days, int) or not 0 <= self.remaining_days <= 3660:
            raise ValueError("remaining_days is outside the bounded range")
        if not isinstance(self.quota_limit_bytes, int) or not 0 <= self.quota_limit_bytes <= 10**15:
            raise ValueError("quota_limit_bytes is outside the bounded range")
        if not isinstance(self.quota_used_bytes, int) or not 0 <= self.quota_used_bytes <= self.quota_limit_bytes:
            raise ValueError("quota_used_bytes is outside the bounded range")
        if not isinstance(self.probe, ReadOnlyProbeEvidence):
            raise TypeError("probe must be ReadOnlyProbeEvidence")
        object.__setattr__(self, "source_sha256", require_sha256(self.source_sha256, "source_sha256"))


@dataclass(frozen=True)
class CandidateSessionReviewPacket:
    candidate_id: str
    evidence_id: str
    license_class: str
    remaining_days: int
    quota_limit_bytes: int
    quota_used_bytes: int
    probe_kind: str
    probe_status: str
    probe_row_count: int
    documentary_status: str
    compatibility_status: str
    missing_evidence_categories: tuple[str, ...]
    missing_fields_by_kind: Mapping[str, tuple[str, ...]]
    operational_observation_status: str
    external_activation_state: str = "BLOCKED"
    provider_selection_state: str = "UNSELECTED"
    credential_state: str = "ABSENT"
    network_state: str = "DISABLED"
    entitlement_state: str = "UNRESOLVED"
    operator_review_required: bool = True
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "evidence_id", require_identifier(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "missing_evidence_categories", tuple(sorted(set(self.missing_evidence_categories))))
        missing = {kind: tuple(values) for kind, values in dict(self.missing_fields_by_kind).items()}
        object.__setattr__(self, "missing_fields_by_kind", MappingProxyType(dict(sorted(missing.items()))))
        if self.operational_observation_status not in {"OBSERVED_READ_ONLY_PROBE", "PROBE_NOT_CONFIRMED"}:
            raise ValueError("operational observation status is invalid")
        fixed = (
            self.external_activation_state == "BLOCKED",
            self.provider_selection_state == "UNSELECTED",
            self.credential_state == "ABSENT",
            self.network_state == "DISABLED",
            self.entitlement_state == "UNRESOLVED",
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("session review boundary cannot be weakened")
        object.__setattr__(self, "packet_hash", canonical_sha256(self.as_payload(include_hash=False)))

    def as_payload(self, *, include_hash: bool = True) -> Mapping[str, object]:
        payload: dict[str, object] = {
            "candidate_id": self.candidate_id,
            "compatibility_status": self.compatibility_status,
            "credential_state": self.credential_state,
            "documentary_status": self.documentary_status,
            "entitlement_state": self.entitlement_state,
            "evidence_id": self.evidence_id,
            "external_activation_state": self.external_activation_state,
            "license_class": self.license_class,
            "missing_evidence_categories": self.missing_evidence_categories,
            "missing_fields_by_kind": dict(self.missing_fields_by_kind),
            "network_state": self.network_state,
            "operational_observation_status": self.operational_observation_status,
            "operator_review_required": self.operator_review_required,
            "probe_kind": self.probe_kind,
            "probe_row_count": self.probe_row_count,
            "probe_status": self.probe_status,
            "provider_selection_state": self.provider_selection_state,
            "quota_limit_bytes": self.quota_limit_bytes,
            "quota_used_bytes": self.quota_used_bytes,
            "remaining_days": self.remaining_days,
        }
        if include_hash:
            payload["packet_hash"] = self.packet_hash
        return MappingProxyType(payload)
