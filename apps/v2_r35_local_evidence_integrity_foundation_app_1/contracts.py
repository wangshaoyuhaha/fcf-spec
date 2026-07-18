from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc


EVIDENCE_ORIGINS = ("INFERRED", "OBSERVED")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256_text(value: object, name: str) -> str:
    normalized = str(value).strip().lower()
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


def canonical_payload_sha256(fields: tuple[tuple[str, str], ...]) -> str:
    payload = json.dumps(
        [list(item) for item in fields],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _record_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RegisteredEvidenceArtifact:
    record_id: str
    evidence_series_id: str
    evidence_type: str
    market: str
    horizon: str
    source_id: str
    registered_artifact_id: str
    artifact_version: str
    effective_at_utc: str
    published_at_utc: str
    retrieved_at_utc: str
    ingested_at_utc: str
    available_at_utc: str
    canonical_fields: tuple[tuple[str, str], ...]
    content_sha256: str
    origin: str = "OBSERVED"
    derivation_id: str | None = None
    source_record_hashes: tuple[str, ...] = ()
    revision_number: int = 0
    revises_record_hash: str | None = None
    operator_registered: bool = True
    local_artifact_only: bool = True
    network_retrieval_allowed: bool = False
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "record_id",
            "evidence_series_id",
            "evidence_type",
            "market",
            "horizon",
            "source_id",
            "registered_artifact_id",
            "artifact_version",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "effective_at_utc",
            "published_at_utc",
            "retrieved_at_utc",
            "ingested_at_utc",
            "available_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not (
            instant(self.published_at_utc)
            <= instant(self.retrieved_at_utc)
            <= instant(self.ingested_at_utc)
            <= instant(self.available_at_utc)
        ):
            raise ValueError("publication, retrieval, ingest, and availability must be ordered")
        fields = tuple(
            sorted(
                (
                    identifier(name, "field_name"),
                    identifier(value, "field_value"),
                )
                for name, value in self.canonical_fields
            )
        )
        if not fields or len({name for name, _ in fields}) != len(fields):
            raise ValueError("canonical fields require unique names")
        object.__setattr__(self, "canonical_fields", fields)
        digest = sha256_text(self.content_sha256, "content_sha256")
        if digest != canonical_payload_sha256(fields):
            raise ValueError("content digest does not match canonical fields")
        object.__setattr__(self, "content_sha256", digest)
        origin = str(self.origin).strip().upper()
        if origin not in EVIDENCE_ORIGINS:
            raise ValueError("origin is not registered")
        object.__setattr__(self, "origin", origin)
        sources = tuple(sha256_text(item, "source_record_hash") for item in self.source_record_hashes)
        if len(set(sources)) != len(sources):
            raise ValueError("source record hashes must be unique")
        object.__setattr__(self, "source_record_hashes", sources)
        if origin == "OBSERVED":
            if self.derivation_id is not None or sources:
                raise ValueError("observed evidence cannot carry inference lineage")
        else:
            if self.derivation_id is None or not sources:
                raise ValueError("inferred evidence requires derivation and source lineage")
            object.__setattr__(
                self, "derivation_id", identifier(self.derivation_id, "derivation_id")
            )
        if (
            isinstance(self.revision_number, bool)
            or not isinstance(self.revision_number, int)
            or self.revision_number < 0
        ):
            raise ValueError("revision_number must be a nonnegative integer")
        if self.revision_number == 0:
            if self.revises_record_hash is not None:
                raise ValueError("revision zero cannot identify a predecessor")
        else:
            if self.revises_record_hash is None:
                raise ValueError("later revision requires a predecessor")
            object.__setattr__(
                self,
                "revises_record_hash",
                sha256_text(self.revises_record_hash, "revises_record_hash"),
            )
        if self.operator_registered is not True or self.local_artifact_only is not True:
            raise ValueError("evidence requires Operator-registered local artifact")
        if self.network_retrieval_allowed:
            raise ValueError("network retrieval exceeds registered-local scope")
        object.__setattr__(
            self,
            "record_hash",
            _record_hash(
                {
                    "artifact": [self.registered_artifact_id, self.artifact_version],
                    "available_at_utc": self.available_at_utc,
                    "canonical_fields": [list(item) for item in fields],
                    "content_sha256": digest,
                    "derivation_id": self.derivation_id,
                    "effective_at_utc": self.effective_at_utc,
                    "evidence_series_id": self.evidence_series_id,
                    "evidence_type": self.evidence_type,
                    "horizon": self.horizon,
                    "ingested_at_utc": self.ingested_at_utc,
                    "market": self.market,
                    "origin": origin,
                    "published_at_utc": self.published_at_utc,
                    "record_id": self.record_id,
                    "retrieved_at_utc": self.retrieved_at_utc,
                    "revision_number": self.revision_number,
                    "revises_record_hash": self.revises_record_hash,
                    "source_id": self.source_id,
                    "source_record_hashes": list(sources),
                }
            ),
        )


@dataclass(frozen=True)
class EvidenceFreshnessPolicy:
    policy_id: str
    max_age_seconds: int
    operator_registered: bool = True
    stale_as_fresh_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        if (
            isinstance(self.max_age_seconds, bool)
            or not isinstance(self.max_age_seconds, int)
            or self.max_age_seconds <= 0
        ):
            raise ValueError("max_age_seconds must be positive")
        if self.operator_registered is not True:
            raise ValueError("freshness policy requires Operator registration")
        if self.stale_as_fresh_allowed:
            raise ValueError("stale evidence cannot be presented as fresh")
