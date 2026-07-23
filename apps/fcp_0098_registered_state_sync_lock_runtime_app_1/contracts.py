from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType


RUNTIME_SCHEMA_VERSION = "fcf-registered-state-sync-lock-runtime-v1"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


def identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def digest(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if _DIGEST.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be SHA-256")
    return normalized


def utc(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.utcoffset().total_seconds() != 0
    ):
        raise ValueError(f"{field_name} must be UTC")
    return normalized


def canonical_sha256(value: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True)
class RegisteredStateSyncArtifact:
    artifact_id: str
    artifact_hash: str
    byte_length: int
    rights_id: str
    registered_at_utc: str
    operator_registered: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "artifact_hash", digest(self.artifact_hash, "artifact_hash"))
        if isinstance(self.byte_length, bool) or self.byte_length <= 0:
            raise ValueError("byte_length must be a positive integer")
        object.__setattr__(self, "rights_id", identifier(self.rights_id, "rights_id"))
        object.__setattr__(self, "registered_at_utc", utc(self.registered_at_utc, "registered_at_utc"))
        if self.operator_registered is not True:
            raise ValueError("State-Sync artifact must be Operator-registered")


@dataclass(frozen=True)
class RegisteredStateSyncLockSnapshot:
    artifact_id: str
    artifact_hash: str
    registry_id: str
    registry_version: str
    anchor_hashes: Mapping[str, str]
    current_event_by_instrument: Mapping[str, str]
    expired_event_ids: tuple[str, ...]
    superseded_event_ids: tuple[str, ...]
    as_of_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    state_mutation_allowed: bool = False
    calculation_allowed: bool = False
    scoring_allowed: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        registry_id = identifier(self.registry_id, "registry_id")
        registry_version = identifier(self.registry_version, "registry_version")
        as_of = utc(self.as_of_utc, "as_of_utc")
        anchors = dict(sorted(self.anchor_hashes.items()))
        current = dict(sorted(self.current_event_by_instrument.items()))
        if not anchors:
            raise ValueError("lock snapshot requires anchors")
        if any(event_id not in anchors for event_id in current.values()):
            raise ValueError("current lock events must be registered anchors")
        for values, name in (
            (self.expired_event_ids, "expired_event_ids"),
            (self.superseded_event_ids, "superseded_event_ids"),
        ):
            if tuple(sorted(set(values))) != values or not set(values).issubset(anchors):
                raise ValueError(f"{name} must be unique sorted registered anchors")
        if set(current.values()).intersection(self.expired_event_ids):
            raise ValueError("expired events cannot hold the current lock")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or any(
                (
                    self.state_mutation_allowed,
                    self.calculation_allowed,
                    self.scoring_allowed,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("State-Sync snapshot exceeds read-only authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "registry_version", registry_version)
        object.__setattr__(self, "anchor_hashes", MappingProxyType(anchors))
        object.__setattr__(self, "current_event_by_instrument", MappingProxyType(current))
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "anchor_hashes": anchors,
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "as_of_utc": as_of,
                    "current_event_by_instrument": current,
                    "expired_event_ids": self.expired_event_ids,
                    "registry_id": registry_id,
                    "registry_version": registry_version,
                    "schema_version": self.schema_version,
                    "superseded_event_ids": self.superseded_event_ids,
                }
            ),
        )
