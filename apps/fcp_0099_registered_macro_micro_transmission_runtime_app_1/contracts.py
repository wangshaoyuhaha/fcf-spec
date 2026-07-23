from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType


RUNTIME_SCHEMA_VERSION = "fcf-registered-macro-micro-transmission-runtime-v1"
CHAIN_LEVELS = (
    "MACRO",
    "ASSET_CLASS",
    "MARKET",
    "SECTOR",
    "INSTRUMENT",
    "MICROSTRUCTURE",
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
class RegisteredTransmissionArtifact:
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
            raise ValueError("transmission artifact must be Operator-registered")


@dataclass(frozen=True)
class TransmissionChainNode:
    level: str
    subject_id: str
    node_hash: str = field(init=False)

    def __post_init__(self) -> None:
        level = str(self.level).strip().upper()
        if level not in CHAIN_LEVELS:
            raise ValueError("chain level is not registered")
        subject_id = identifier(self.subject_id, "subject_id")
        object.__setattr__(self, "level", level)
        object.__setattr__(self, "subject_id", subject_id)
        object.__setattr__(
            self,
            "node_hash",
            canonical_sha256({"level": level, "subject_id": subject_id}),
        )


@dataclass(frozen=True)
class RegisteredTransmissionRecord:
    transmission_id: str
    transmission_version: str
    macro_event_id: str
    publication_time_utc: str
    expected_value_id: str
    observed_value_id: str
    surprise_definition_id: str
    source_evidence_hashes: tuple[str, ...]
    available_at_utc: str
    chain: tuple[TransmissionChainNode, ...]
    hypothesized_direction: str
    mechanism_id: str
    horizon_id: str
    decay_seconds: int
    supporting_evidence_hashes: tuple[str, ...]
    contradicting_evidence_hashes: tuple[str, ...]
    regime_ids: tuple[str, ...]
    state_hash: str
    correlation_id: str
    invalidation_ids: tuple[str, ...]
    expires_at_utc: str
    uncertainty_bps: int
    causal_truth_claimed: bool = False
    operator_registered: bool = True
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "transmission_id",
            "transmission_version",
            "macro_event_id",
            "expected_value_id",
            "observed_value_id",
            "surprise_definition_id",
            "mechanism_id",
            "horizon_id",
            "correlation_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        publication = utc(self.publication_time_utc, "publication_time_utc")
        available = utc(self.available_at_utc, "available_at_utc")
        expires = utc(self.expires_at_utc, "expires_at_utc")
        if instant(available) < instant(publication):
            raise ValueError("availability cannot precede publication")
        if instant(expires) <= instant(available):
            raise ValueError("expiry must follow availability")
        direction = str(self.hypothesized_direction).strip().upper()
        if direction not in {"UP", "DOWN", "MIXED", "NEUTRAL"}:
            raise ValueError("hypothesized_direction is not registered")
        if isinstance(self.decay_seconds, bool) or self.decay_seconds <= 0:
            raise ValueError("decay_seconds must be positive")
        if (
            isinstance(self.uncertainty_bps, bool)
            or not 0 <= self.uncertainty_bps <= 10000
        ):
            raise ValueError("uncertainty_bps must be between zero and 10000")
        chain = tuple(self.chain)
        if tuple(node.level for node in chain) != CHAIN_LEVELS:
            raise ValueError("transmission chain must use every official level in order")
        if len({node.subject_id for node in chain}) != len(chain):
            raise ValueError("transmission chain subjects must be unique")

        def hashes(values: tuple[str, ...], name: str) -> tuple[str, ...]:
            normalized = tuple(digest(value, name) for value in values)
            if tuple(sorted(set(normalized))) != normalized:
                raise ValueError(f"{name} must be unique and sorted")
            return normalized

        def identifiers(values: tuple[str, ...], name: str) -> tuple[str, ...]:
            normalized = tuple(identifier(value, name) for value in values)
            if tuple(sorted(set(normalized))) != normalized:
                raise ValueError(f"{name} must be unique and sorted")
            return normalized

        source = hashes(self.source_evidence_hashes, "source_evidence_hash")
        supporting = hashes(
            self.supporting_evidence_hashes, "supporting_evidence_hash"
        )
        contradicting = hashes(
            self.contradicting_evidence_hashes, "contradicting_evidence_hash"
        )
        if not source or not supporting or not contradicting:
            raise ValueError("transmission requires source, support, and contradiction")
        if not set(supporting).issubset(source) or not set(contradicting).issubset(
            source
        ):
            raise ValueError("support and contradiction must resolve to source evidence")
        regimes = identifiers(self.regime_ids, "regime_id")
        invalidations = identifiers(self.invalidation_ids, "invalidation_id")
        if not regimes or not invalidations:
            raise ValueError("transmission requires regime and invalidation identities")
        state_hash = digest(self.state_hash, "state_hash")
        if self.causal_truth_claimed or self.operator_registered is not True:
            raise ValueError("transmission must remain an Operator-registered hypothesis")
        object.__setattr__(self, "publication_time_utc", publication)
        object.__setattr__(self, "available_at_utc", available)
        object.__setattr__(self, "expires_at_utc", expires)
        object.__setattr__(self, "hypothesized_direction", direction)
        object.__setattr__(self, "chain", chain)
        object.__setattr__(self, "source_evidence_hashes", source)
        object.__setattr__(self, "supporting_evidence_hashes", supporting)
        object.__setattr__(self, "contradicting_evidence_hashes", contradicting)
        object.__setattr__(self, "regime_ids", regimes)
        object.__setattr__(self, "invalidation_ids", invalidations)
        object.__setattr__(self, "state_hash", state_hash)
        object.__setattr__(
            self,
            "record_hash",
            canonical_sha256(
                {
                    "available_at_utc": available,
                    "causal_truth_claimed": self.causal_truth_claimed,
                    "chain_hashes": [node.node_hash for node in chain],
                    "contradicting_evidence_hashes": contradicting,
                    "correlation_id": self.correlation_id,
                    "decay_seconds": self.decay_seconds,
                    "expected_value_id": self.expected_value_id,
                    "expires_at_utc": expires,
                    "horizon_id": self.horizon_id,
                    "hypothesized_direction": direction,
                    "invalidation_ids": invalidations,
                    "macro_event_id": self.macro_event_id,
                    "mechanism_id": self.mechanism_id,
                    "observed_value_id": self.observed_value_id,
                    "operator_registered": self.operator_registered,
                    "publication_time_utc": publication,
                    "regime_ids": regimes,
                    "source_evidence_hashes": source,
                    "state_hash": state_hash,
                    "supporting_evidence_hashes": supporting,
                    "surprise_definition_id": self.surprise_definition_id,
                    "transmission_id": self.transmission_id,
                    "transmission_version": self.transmission_version,
                    "uncertainty_bps": self.uncertainty_bps,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredTransmissionSnapshot:
    artifact_id: str
    artifact_hash: str
    registry_id: str
    registry_version: str
    record_hashes: Mapping[str, str]
    active_transmission_ids: tuple[str, ...]
    expired_transmission_ids: tuple[str, ...]
    chain_subjects: Mapping[str, tuple[str, ...]]
    as_of_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    calculation_allowed: bool = False
    scoring_allowed: bool = False
    causal_truth_authority: bool = False
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
        record_hashes = dict(sorted(self.record_hashes.items()))
        subjects = {
            key: tuple(value)
            for key, value in sorted(self.chain_subjects.items())
        }
        active = tuple(sorted(set(self.active_transmission_ids)))
        expired = tuple(sorted(set(self.expired_transmission_ids)))
        if set(active).intersection(expired) or set(active + expired) != set(
            record_hashes
        ):
            raise ValueError("snapshot lifecycle partition is invalid")
        if set(subjects) != set(record_hashes):
            raise ValueError("snapshot chain subjects must cover every record")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or any(
                (
                    self.calculation_allowed,
                    self.scoring_allowed,
                    self.causal_truth_authority,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("transmission snapshot exceeds read-only authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "registry_version", registry_version)
        object.__setattr__(self, "record_hashes", MappingProxyType(record_hashes))
        object.__setattr__(self, "chain_subjects", MappingProxyType(subjects))
        object.__setattr__(self, "active_transmission_ids", active)
        object.__setattr__(self, "expired_transmission_ids", expired)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "active_transmission_ids": active,
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "as_of_utc": as_of,
                    "chain_subjects": subjects,
                    "expired_transmission_ids": expired,
                    "record_hashes": record_hashes,
                    "registry_id": registry_id,
                    "registry_version": registry_version,
                    "schema_version": self.schema_version,
                }
            ),
        )
