from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping


SAFE_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
ALLOWED_MARKETS = ("SSE", "SZSE")
ALLOWED_CAPABILITIES = ("DAILY_BAR", "MINUTE_BAR", "ORDER_BOOK", "TICK")
ALLOWED_ENTITLEMENT_STATES = ("DENIED", "GRANTED", "UNKNOWN")
ALLOWED_PROBE_STATES = ("FAILED", "NOT_RUN", "SUCCEEDED")
ALLOWED_DOCUMENT_STATES = ("DOCUMENTED", "UNRESOLVED")
ALLOWED_CLOCK_SEMANTICS = ("ASIA_SHANGHAI_EXCHANGE_TIME", "UTC")
ALLOWED_DECISIONS = ("INSUFFICIENT_EVIDENCE", "OPERATOR_REVIEW_ELIGIBLE")
FORBIDDEN_KEY_FRAGMENTS = (
    "account",
    "authorization",
    "credential",
    "id_card",
    "license_key",
    "password",
    "phone",
    "secret",
    "token",
    "username",
)
EVIDENCE_FIELDS = (
    "capabilities",
    "captured_at_utc",
    "clock_semantics",
    "entitlement_declared_state",
    "evidence_revision",
    "expires_at_utc",
    "markets",
    "module_file_sha256",
    "probe_status",
    "python_module_name",
    "python_module_version",
    "retention_state",
    "rights_state",
    "supporting_document_sha256",
    "terminal_product",
    "terminal_version",
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


def require_safe(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not SAFE_VALUE.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a safe value")
    return normalized


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


def _closed_tuple(values: object, allowed: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise TypeError(f"{field_name} must be a sequence")
    normalized = tuple(sorted({str(value).strip().upper() for value in values}))
    if not normalized or any(value not in allowed for value in normalized):
        raise ValueError(f"{field_name} contains an unregistered value")
    return normalized


@dataclass(frozen=True)
class RegisteredEntitlementEvidenceArtifact:
    artifact_id: str
    artifact_path: str
    artifact_sha256: str
    byte_length: int
    source_kind: str = "OPERATOR_SANITIZED_LOCAL_EVIDENCE"
    credentials_committed: bool = False
    account_identifiers_committed: bool = False
    raw_market_values_committed: bool = False
    executable_request_committed: bool = False
    network_used_by_sidecar: bool = False
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", require_safe(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "artifact_path", require_safe(self.artifact_path, "artifact_path"))
        object.__setattr__(self, "artifact_sha256", require_sha256(self.artifact_sha256, "artifact_sha256"))
        if not isinstance(self.byte_length, int) or not 2 <= self.byte_length <= 65536:
            raise ValueError("byte_length is outside the bounded artifact limit")
        fixed = (
            self.source_kind == "OPERATOR_SANITIZED_LOCAL_EVIDENCE",
            self.credentials_committed is False,
            self.account_identifiers_committed is False,
            self.raw_market_values_committed is False,
            self.executable_request_committed is False,
            self.network_used_by_sidecar is False,
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("registered evidence boundary cannot be weakened")


@dataclass(frozen=True)
class MiniQMTEntitlementEvidence:
    terminal_product: str
    terminal_version: str
    python_module_name: str
    python_module_version: str
    module_file_sha256: str
    entitlement_declared_state: str
    markets: tuple[str, ...]
    capabilities: tuple[str, ...]
    clock_semantics: str
    probe_status: str
    rights_state: str
    retention_state: str
    evidence_revision: str
    captured_at_utc: str
    expires_at_utc: str | None
    supporting_document_sha256: str
    probe_invoked_by_sidecar: bool = False
    provider_selected: bool = False

    def __post_init__(self) -> None:
        if self.terminal_product != "GUOJIN_MINIQMT":
            raise ValueError("terminal_product must be GUOJIN_MINIQMT")
        if self.python_module_name != "xtquant":
            raise ValueError("python_module_name must be xtquant")
        for name in ("terminal_version", "python_module_version", "evidence_revision"):
            object.__setattr__(self, name, require_safe(getattr(self, name), name))
        object.__setattr__(self, "module_file_sha256", require_sha256(self.module_file_sha256, "module_file_sha256"))
        object.__setattr__(self, "supporting_document_sha256", require_sha256(self.supporting_document_sha256, "supporting_document_sha256"))
        entitlement = str(self.entitlement_declared_state).strip().upper()
        probe = str(self.probe_status).strip().upper()
        rights = str(self.rights_state).strip().upper()
        retention = str(self.retention_state).strip().upper()
        clock = str(self.clock_semantics).strip().upper()
        if entitlement not in ALLOWED_ENTITLEMENT_STATES:
            raise ValueError("entitlement_declared_state is invalid")
        if probe not in ALLOWED_PROBE_STATES:
            raise ValueError("probe_status is invalid")
        if rights not in ALLOWED_DOCUMENT_STATES or retention not in ALLOWED_DOCUMENT_STATES:
            raise ValueError("rights or retention state is invalid")
        if clock not in ALLOWED_CLOCK_SEMANTICS:
            raise ValueError("clock_semantics is invalid")
        object.__setattr__(self, "entitlement_declared_state", entitlement)
        object.__setattr__(self, "probe_status", probe)
        object.__setattr__(self, "rights_state", rights)
        object.__setattr__(self, "retention_state", retention)
        object.__setattr__(self, "clock_semantics", clock)
        object.__setattr__(self, "markets", _closed_tuple(self.markets, ALLOWED_MARKETS, "markets"))
        object.__setattr__(self, "capabilities", _closed_tuple(self.capabilities, ALLOWED_CAPABILITIES, "capabilities"))
        object.__setattr__(self, "captured_at_utc", require_utc(self.captured_at_utc, "captured_at_utc"))
        if self.expires_at_utc is not None:
            object.__setattr__(self, "expires_at_utc", require_utc(self.expires_at_utc, "expires_at_utc"))
        if self.probe_invoked_by_sidecar is not False or self.provider_selected is not False:
            raise ValueError("sidecar invocation and provider selection are forbidden")


@dataclass(frozen=True)
class MiniQMTEntitlementReviewPacket:
    artifact_id: str
    terminal_product: str
    terminal_version: str
    python_module_name: str
    python_module_version: str
    markets: tuple[str, ...]
    capabilities: tuple[str, ...]
    observed_entitlement_state: str
    probe_status: str
    blockers: tuple[str, ...]
    decision_state: str
    entitlement_authorized: bool = False
    registered_evidence_authority: bool = False
    realtime_activation_authorized: bool = False
    provider_selected: bool = False
    data_promotion_authorized: bool = False
    closes_gap: bool = False
    operator_review_required: bool = True
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", require_safe(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "blockers", tuple(sorted(set(self.blockers))))
        if self.decision_state not in ALLOWED_DECISIONS:
            raise ValueError("decision_state is invalid")
        if (self.decision_state == "OPERATOR_REVIEW_ELIGIBLE") != (not self.blockers):
            raise ValueError("decision_state must match exact blockers")
        fixed_false = (
            self.entitlement_authorized,
            self.registered_evidence_authority,
            self.realtime_activation_authorized,
            self.provider_selected,
            self.data_promotion_authorized,
            self.closes_gap,
        )
        if any(fixed_false) or self.operator_review_required is not True:
            raise ValueError("review packet authority boundary cannot be weakened")
        object.__setattr__(self, "packet_hash", canonical_sha256(self.as_payload(include_hash=False)))

    def as_payload(self, *, include_hash: bool = True) -> Mapping[str, object]:
        payload: dict[str, object] = {
            "artifact_id": self.artifact_id,
            "blockers": self.blockers,
            "capabilities": self.capabilities,
            "closes_gap": self.closes_gap,
            "data_promotion_authorized": self.data_promotion_authorized,
            "decision_state": self.decision_state,
            "entitlement_authorized": self.entitlement_authorized,
            "markets": self.markets,
            "observed_entitlement_state": self.observed_entitlement_state,
            "operator_review_required": self.operator_review_required,
            "probe_status": self.probe_status,
            "provider_selected": self.provider_selected,
            "python_module_name": self.python_module_name,
            "python_module_version": self.python_module_version,
            "realtime_activation_authorized": self.realtime_activation_authorized,
            "registered_evidence_authority": self.registered_evidence_authority,
            "terminal_product": self.terminal_product,
            "terminal_version": self.terminal_version,
        }
        if include_hash:
            payload["packet_hash"] = self.packet_hash
        return MappingProxyType(payload)


def reject_secret_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if any(fragment in normalized for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError("secret-bearing or account-bearing key is forbidden")
            reject_secret_keys(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            reject_secret_keys(nested)
