from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType


RUNTIME_SCHEMA_VERSION = "fcf-registered-multi-horizon-conflict-runtime-v1"
HORIZON_IDS = (
    "EQUITY_MEDIUM",
    "EQUITY_SHORT",
    "ASHARE_INTRADAY",
    "BTC_SHORT",
)
RESULT_GROUPS = (
    "SUPPORTING",
    "OPPOSING",
    "NEUTRAL",
    "MISSING",
    "STALE",
    "BLOCKED",
)
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


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True)
class RegisteredConflictArtifact:
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
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if self.operator_registered is not True:
            raise ValueError("conflict artifact must be Operator-registered")


@dataclass(frozen=True)
class RegisteredHorizonResult:
    result_id: str
    horizon_id: str
    signal_direction: str
    evidence_state: str
    evidence_hashes: tuple[str, ...]
    available_at_utc: str
    expires_at_utc: str
    state_hash: str
    correlation_id: str
    invalidation_ids: tuple[str, ...]
    hard_risk_block: bool = False
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        result_id = identifier(self.result_id, "result_id")
        horizon_id = str(self.horizon_id).strip().upper()
        if horizon_id not in HORIZON_IDS:
            raise ValueError("horizon_id is not registered")
        direction = str(self.signal_direction).strip().upper()
        if direction not in {"UP", "DOWN", "NEUTRAL", "UNKNOWN"}:
            raise ValueError("signal_direction is not registered")
        evidence_state = str(self.evidence_state).strip().upper()
        if evidence_state not in {"OBSERVED", "MISSING", "STALE", "BLOCKED"}:
            raise ValueError("evidence_state is not registered")
        evidence = tuple(digest(value, "evidence_hash") for value in self.evidence_hashes)
        if tuple(sorted(set(evidence))) != evidence:
            raise ValueError("evidence_hashes must be unique and sorted")
        if evidence_state == "OBSERVED" and not evidence:
            raise ValueError("observed result requires evidence")
        if evidence_state == "MISSING" and evidence:
            raise ValueError("missing result cannot carry evidence")
        available = utc(self.available_at_utc, "available_at_utc")
        expires = utc(self.expires_at_utc, "expires_at_utc")
        if instant(expires) <= instant(available):
            raise ValueError("expiry must follow availability")
        state_hash = digest(self.state_hash, "state_hash")
        correlation_id = identifier(self.correlation_id, "correlation_id")
        invalidations = tuple(
            identifier(value, "invalidation_id") for value in self.invalidation_ids
        )
        if tuple(sorted(set(invalidations))) != invalidations or not invalidations:
            raise ValueError("invalidation_ids must be nonempty, unique, and sorted")
        if type(self.hard_risk_block) is not bool:
            raise ValueError("hard_risk_block must be boolean")
        object.__setattr__(self, "result_id", result_id)
        object.__setattr__(self, "horizon_id", horizon_id)
        object.__setattr__(self, "signal_direction", direction)
        object.__setattr__(self, "evidence_state", evidence_state)
        object.__setattr__(self, "evidence_hashes", evidence)
        object.__setattr__(self, "available_at_utc", available)
        object.__setattr__(self, "expires_at_utc", expires)
        object.__setattr__(self, "state_hash", state_hash)
        object.__setattr__(self, "correlation_id", correlation_id)
        object.__setattr__(self, "invalidation_ids", invalidations)
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(
                {
                    "available_at_utc": available,
                    "correlation_id": correlation_id,
                    "evidence_hashes": evidence,
                    "evidence_state": evidence_state,
                    "expires_at_utc": expires,
                    "hard_risk_block": self.hard_risk_block,
                    "horizon_id": horizon_id,
                    "invalidation_ids": invalidations,
                    "result_id": result_id,
                    "signal_direction": direction,
                    "state_hash": state_hash,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredConflictSet:
    conflict_set_id: str
    market_id: str
    instrument_id: str
    thesis_direction: str
    results: tuple[RegisteredHorizonResult, ...]
    set_hash: str = field(init=False)

    def __post_init__(self) -> None:
        conflict_set_id = identifier(self.conflict_set_id, "conflict_set_id")
        market_id = identifier(self.market_id, "market_id")
        instrument_id = identifier(self.instrument_id, "instrument_id")
        direction = str(self.thesis_direction).strip().upper()
        if direction not in {"UP", "DOWN"}:
            raise ValueError("thesis_direction must be UP or DOWN")
        results = tuple(self.results)
        if not results:
            raise ValueError("conflict set must contain horizon results")
        horizons = tuple(result.horizon_id for result in results)
        identities = tuple(result.result_id for result in results)
        if len(set(horizons)) != len(horizons):
            raise ValueError("conflict set cannot collapse duplicate horizons")
        if len(set(identities)) != len(identities):
            raise ValueError("result identities must be unique")
        if tuple(sorted(horizons, key=HORIZON_IDS.index)) != horizons:
            raise ValueError("horizon results must use registered order")
        object.__setattr__(self, "conflict_set_id", conflict_set_id)
        object.__setattr__(self, "market_id", market_id)
        object.__setattr__(self, "instrument_id", instrument_id)
        object.__setattr__(self, "thesis_direction", direction)
        object.__setattr__(self, "results", results)
        object.__setattr__(
            self,
            "set_hash",
            canonical_sha256(
                {
                    "conflict_set_id": conflict_set_id,
                    "instrument_id": instrument_id,
                    "market_id": market_id,
                    "result_hashes": [result.result_hash for result in results],
                    "thesis_direction": direction,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredConflictSnapshot:
    artifact_id: str
    artifact_hash: str
    registry_id: str
    registry_version: str
    set_hashes: Mapping[str, str]
    grouped_result_ids: Mapping[str, Mapping[str, tuple[str, ...]]]
    presentation_rows: Mapping[str, tuple[tuple[str, str, str], ...]]
    conflicting_set_ids: tuple[str, ...]
    as_of_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    mixed_score_allowed: bool = False
    consensus_collapse_allowed: bool = False
    calculation_authority: bool = False
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
        set_hashes = dict(sorted(self.set_hashes.items()))
        grouped = {
            set_id: MappingProxyType(
                {
                    group: tuple(groups[group])
                    for group in RESULT_GROUPS
                }
            )
            for set_id, groups in sorted(self.grouped_result_ids.items())
        }
        rows = {
            set_id: tuple(value)
            for set_id, value in sorted(self.presentation_rows.items())
        }
        conflicting = tuple(sorted(set(self.conflicting_set_ids)))
        if set(grouped) != set(set_hashes) or set(rows) != set(set_hashes):
            raise ValueError("snapshot views must cover every conflict set")
        if not set(conflicting).issubset(set_hashes):
            raise ValueError("conflicting_set_ids must resolve to registered sets")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or any(
                (
                    self.mixed_score_allowed,
                    self.consensus_collapse_allowed,
                    self.calculation_authority,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("conflict snapshot exceeds read-only authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "registry_version", registry_version)
        object.__setattr__(self, "set_hashes", MappingProxyType(set_hashes))
        object.__setattr__(self, "grouped_result_ids", MappingProxyType(grouped))
        object.__setattr__(self, "presentation_rows", MappingProxyType(rows))
        object.__setattr__(self, "conflicting_set_ids", conflicting)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "as_of_utc": as_of,
                    "conflicting_set_ids": conflicting,
                    "grouped_result_ids": {
                        key: dict(value) for key, value in grouped.items()
                    },
                    "presentation_rows": rows,
                    "registry_id": registry_id,
                    "registry_version": registry_version,
                    "schema_version": self.schema_version,
                    "set_hashes": set_hashes,
                }
            ),
        )
