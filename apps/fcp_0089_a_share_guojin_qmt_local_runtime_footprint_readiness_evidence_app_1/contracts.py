from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


SAFE_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
UTC_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
REQUIRED_DIRECTORY_CLASSES = (
    "DATADIR",
    "DATAS",
    "DUMPS",
    "LOG",
    "QUOTER",
    "USERS",
)
REQUIRED_CACHE_FAMILIES = (
    "STOCK_LIST_SH",
    "STOCK_LIST_SZ",
    "TRADE_DATE_LIST",
)
ALLOWED_READINESS_STATES = (
    "INCOMPLETE_FOOTPRINT",
    "READY_FOR_OPERATOR_PROBE",
)
PERMANENT_BLOCKERS = (
    "MINIQMT_ENTITLEMENT_UNPROVEN",
    "QMT_TERMINAL_LIVENESS_UNPROVEN",
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


def _safe(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not SAFE_VALUE.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a safe value")
    return normalized


def _sha(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if not SHA256.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a SHA-256 digest")
    return normalized


def _closed_partition(
    present: object,
    missing: object,
    required: tuple[str, ...],
    field_name: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not isinstance(present, (list, tuple)) or not isinstance(missing, (list, tuple)):
        raise TypeError(f"{field_name} values must be sequences")
    normalized_present = tuple(sorted({str(value).strip().upper() for value in present}))
    normalized_missing = tuple(sorted({str(value).strip().upper() for value in missing}))
    if set(normalized_present) & set(normalized_missing):
        raise ValueError(f"{field_name} partitions overlap")
    if set(normalized_present) | set(normalized_missing) != set(required):
        raise ValueError(f"{field_name} partitions are not exact")
    return normalized_present, normalized_missing


@dataclass(frozen=True)
class RuntimeFootprintRegistration:
    artifact_id: str
    directory_kind: str = "GUOJIN_MINIQMT_USERDATA_MINI"
    max_top_level_entries: int = 64
    metadata_only: bool = True
    recursive_scan: bool = False
    file_content_read: bool = False
    arbitrary_names_emitted: bool = False
    local_path_emitted: bool = False
    sdk_invoked: bool = False
    network_used: bool = False
    credentials_used: bool = False
    account_accessed: bool = False
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", _safe(self.artifact_id, "artifact_id"))
        if self.directory_kind != "GUOJIN_MINIQMT_USERDATA_MINI":
            raise ValueError("directory_kind is invalid")
        if (
            not isinstance(self.max_top_level_entries, int)
            or isinstance(self.max_top_level_entries, bool)
            or not 1 <= self.max_top_level_entries <= 256
        ):
            raise ValueError("max_top_level_entries is outside the closed limit")
        fixed = (
            self.metadata_only is True,
            self.recursive_scan is False,
            self.file_content_read is False,
            self.arbitrary_names_emitted is False,
            self.local_path_emitted is False,
            self.sdk_invoked is False,
            self.network_used is False,
            self.credentials_used is False,
            self.account_accessed is False,
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("runtime footprint registration boundary cannot be weakened")


@dataclass(frozen=True)
class RuntimeFootprintSnapshot:
    top_level_entry_count: int
    directory_count: int
    regular_file_count: int
    aggregate_regular_file_bytes: int
    latest_metadata_time_utc: str
    required_directories_present: tuple[str, ...]
    required_directories_missing: tuple[str, ...]
    required_cache_families_present: tuple[str, ...]
    required_cache_families_missing: tuple[str, ...]
    manifest_sha256: str

    def __post_init__(self) -> None:
        counts = (
            self.top_level_entry_count,
            self.directory_count,
            self.regular_file_count,
            self.aggregate_regular_file_bytes,
        )
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in counts
        ):
            raise ValueError("snapshot counts must be non-negative integers")
        if self.directory_count + self.regular_file_count != self.top_level_entry_count:
            raise ValueError("snapshot entry counts are incoherent")
        if not UTC_TIME.fullmatch(str(self.latest_metadata_time_utc)):
            raise ValueError("latest_metadata_time_utc must be canonical UTC")
        directories = _closed_partition(
            self.required_directories_present,
            self.required_directories_missing,
            REQUIRED_DIRECTORY_CLASSES,
            "required directories",
        )
        caches = _closed_partition(
            self.required_cache_families_present,
            self.required_cache_families_missing,
            REQUIRED_CACHE_FAMILIES,
            "required cache families",
        )
        object.__setattr__(self, "required_directories_present", directories[0])
        object.__setattr__(self, "required_directories_missing", directories[1])
        object.__setattr__(self, "required_cache_families_present", caches[0])
        object.__setattr__(self, "required_cache_families_missing", caches[1])
        object.__setattr__(
            self,
            "manifest_sha256",
            _sha(self.manifest_sha256, "manifest_sha256"),
        )


@dataclass(frozen=True)
class RuntimeFootprintEvidence:
    artifact_id: str
    directory_kind: str
    top_level_entry_count: int
    directory_count: int
    regular_file_count: int
    aggregate_regular_file_bytes: int
    latest_metadata_time_utc: str
    required_directories_present: tuple[str, ...]
    required_directories_missing: tuple[str, ...]
    required_cache_families_present: tuple[str, ...]
    required_cache_families_missing: tuple[str, ...]
    manifest_sha256: str
    readiness_state: str
    blockers: tuple[str, ...]
    metadata_only: bool = True
    file_content_read: bool = False
    recursive_scan: bool = False
    local_path_emitted: bool = False
    arbitrary_names_emitted: bool = False
    terminal_liveness_proven: bool = False
    entitlement_proven: bool = False
    registered_evidence_authority: bool = False
    provider_selected: bool = False
    realtime_activation_authorized: bool = False
    data_promotion_authorized: bool = False
    closes_gap: bool = False
    operator_review_required: bool = True
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", _safe(self.artifact_id, "artifact_id"))
        object.__setattr__(
            self,
            "manifest_sha256",
            _sha(self.manifest_sha256, "manifest_sha256"),
        )
        if self.readiness_state not in ALLOWED_READINESS_STATES:
            raise ValueError("readiness_state is invalid")
        blockers = tuple(sorted(set(self.blockers)))
        if not set(PERMANENT_BLOCKERS).issubset(set(blockers)):
            raise ValueError("permanent blockers are missing")
        ready = (
            not self.required_directories_missing
            and not self.required_cache_families_missing
        )
        if (self.readiness_state == "READY_FOR_OPERATOR_PROBE") != ready:
            raise ValueError("readiness_state does not match exact footprint")
        fixed_true = (
            self.metadata_only,
            self.operator_review_required,
        )
        fixed_false = (
            self.file_content_read,
            self.recursive_scan,
            self.local_path_emitted,
            self.arbitrary_names_emitted,
            self.terminal_liveness_proven,
            self.entitlement_proven,
            self.registered_evidence_authority,
            self.provider_selected,
            self.realtime_activation_authorized,
            self.data_promotion_authorized,
            self.closes_gap,
        )
        if not all(fixed_true) or any(fixed_false):
            raise ValueError("runtime footprint evidence boundary cannot be weakened")
        object.__setattr__(self, "blockers", blockers)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(self.as_payload(include_hash=False)),
        )

    def as_payload(self, *, include_hash: bool = True) -> Mapping[str, object]:
        payload: dict[str, object] = {
            "account_accessed": False,
            "aggregate_regular_file_bytes": self.aggregate_regular_file_bytes,
            "arbitrary_names_emitted": self.arbitrary_names_emitted,
            "artifact_id": self.artifact_id,
            "blockers": self.blockers,
            "closes_gap": self.closes_gap,
            "credentials_used": False,
            "data_promotion_authorized": self.data_promotion_authorized,
            "directory_count": self.directory_count,
            "directory_kind": self.directory_kind,
            "entitlement_proven": self.entitlement_proven,
            "file_content_read": self.file_content_read,
            "latest_metadata_time_utc": self.latest_metadata_time_utc,
            "local_path_emitted": self.local_path_emitted,
            "manifest_sha256": self.manifest_sha256,
            "metadata_only": self.metadata_only,
            "network_used": False,
            "operator_review_required": self.operator_review_required,
            "provider_selected": self.provider_selected,
            "readiness_state": self.readiness_state,
            "realtime_activation_authorized": self.realtime_activation_authorized,
            "recursive_scan": self.recursive_scan,
            "registered_evidence_authority": self.registered_evidence_authority,
            "regular_file_count": self.regular_file_count,
            "required_cache_families_missing": self.required_cache_families_missing,
            "required_cache_families_present": self.required_cache_families_present,
            "required_directories_missing": self.required_directories_missing,
            "required_directories_present": self.required_directories_present,
            "sdk_invoked": False,
            "terminal_liveness_proven": self.terminal_liveness_proven,
            "top_level_entry_count": self.top_level_entry_count,
        }
        if include_hash:
            payload["evidence_hash"] = self.evidence_hash
        return MappingProxyType(payload)


def build_runtime_footprint_evidence(
    registration: RuntimeFootprintRegistration,
    snapshot: RuntimeFootprintSnapshot,
) -> RuntimeFootprintEvidence:
    missing = tuple(
        sorted(
            {
                *(f"MISSING_DIRECTORY_{value}" for value in snapshot.required_directories_missing),
                *(f"MISSING_CACHE_{value}" for value in snapshot.required_cache_families_missing),
                *PERMANENT_BLOCKERS,
            }
        )
    )
    readiness_state = (
        "READY_FOR_OPERATOR_PROBE"
        if not snapshot.required_directories_missing
        and not snapshot.required_cache_families_missing
        else "INCOMPLETE_FOOTPRINT"
    )
    return RuntimeFootprintEvidence(
        artifact_id=registration.artifact_id,
        directory_kind=registration.directory_kind,
        top_level_entry_count=snapshot.top_level_entry_count,
        directory_count=snapshot.directory_count,
        regular_file_count=snapshot.regular_file_count,
        aggregate_regular_file_bytes=snapshot.aggregate_regular_file_bytes,
        latest_metadata_time_utc=snapshot.latest_metadata_time_utc,
        required_directories_present=snapshot.required_directories_present,
        required_directories_missing=snapshot.required_directories_missing,
        required_cache_families_present=snapshot.required_cache_families_present,
        required_cache_families_missing=snapshot.required_cache_families_missing,
        manifest_sha256=snapshot.manifest_sha256,
        readiness_state=readiness_state,
        blockers=missing,
    )


def build_reference_evidence() -> RuntimeFootprintEvidence:
    registration = RuntimeFootprintRegistration(
        artifact_id="qmt-runtime-reference-v1",
    )
    snapshot = RuntimeFootprintSnapshot(
        top_level_entry_count=9,
        directory_count=6,
        regular_file_count=3,
        aggregate_regular_file_bytes=6,
        latest_metadata_time_utc="2026-07-23T00:00:00.000000Z",
        required_directories_present=REQUIRED_DIRECTORY_CLASSES,
        required_directories_missing=(),
        required_cache_families_present=REQUIRED_CACHE_FAMILIES,
        required_cache_families_missing=(),
        manifest_sha256="1" * 64,
    )
    return build_runtime_footprint_evidence(registration, snapshot)
