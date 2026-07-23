from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

from apps.v2_r1_factor_contract_foundation_app_1 import ForecastTargetDefinition


RUNTIME_SCHEMA_VERSION = "fcf-registered-target-label-registry-runtime-v1"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


def identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def reference(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    parts = normalized.split("@")
    if len(parts) != 2:
        raise ValueError(f"{field_name} must be an id-at-version reference")
    identifier(parts[0], f"{field_name} id")
    identifier(parts[1], f"{field_name} version")
    return normalized


def text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized or any(ord(character) > 127 for character in normalized):
        raise ValueError(f"{field_name} must be nonempty ASCII text")
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
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return normalized


def canonical_sha256(value: Mapping[str, object]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def target_ref(definition: ForecastTargetDefinition) -> str:
    return f"{definition.target_id}@{definition.target_version}"


@dataclass(frozen=True)
class RegisteredTargetLabelArtifact:
    artifact_id: str
    artifact_hash: str
    byte_length: int
    rights_id: str
    registered_at_utc: str
    operator_registered: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(
            self,
            "artifact_hash",
            digest(self.artifact_hash, "artifact_hash"),
        )
        if isinstance(self.byte_length, bool) or self.byte_length <= 0:
            raise ValueError("byte_length must be a positive integer")
        object.__setattr__(self, "rights_id", identifier(self.rights_id, "rights_id"))
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if self.operator_registered is not True:
            raise ValueError("target-label artifact must be Operator-registered")


@dataclass(frozen=True)
class RegisteredLabelDefinition:
    label_id: str
    label_version: str
    target_ref: str
    maturity_rule: str
    value_type: str
    observation_key_rule: str
    decision_time_field: str
    maturity_time_field: str
    published_time_field: str
    available_time_field: str
    first_tradable_time_field: str
    source_evidence_rule: str
    missing_behavior: str
    invalid_behavior: str
    censored_behavior: str
    revision_policy: str
    effective_at_utc: str
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        identifier_fields = (
            "label_id",
            "label_version",
            "maturity_rule",
            "value_type",
            "observation_key_rule",
            "decision_time_field",
            "maturity_time_field",
            "published_time_field",
            "available_time_field",
            "first_tradable_time_field",
            "source_evidence_rule",
            "missing_behavior",
            "invalid_behavior",
            "censored_behavior",
            "revision_policy",
        )
        for field_name in identifier_fields:
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "target_ref",
            reference(self.target_ref, "target_ref"),
        )
        effective = utc(self.effective_at_utc, "effective_at_utc")
        object.__setattr__(self, "effective_at_utc", effective)
        object.__setattr__(
            self,
            "record_hash",
            canonical_sha256(
                {
                    field_name: getattr(self, field_name)
                    for field_name in identifier_fields
                    + ("target_ref", "effective_at_utc")
                }
            ),
        )

    @property
    def natural_key(self) -> str:
        return f"{self.label_id}@{self.label_version}"


@dataclass(frozen=True)
class RegisteredTargetLabelRuntimeSnapshot:
    artifact_id: str
    artifact_hash: str
    registry_id: str
    registry_version: str
    target_record_hashes: Mapping[str, str]
    label_record_hashes: Mapping[str, str]
    target_to_label_refs: Mapping[str, tuple[str, ...]]
    label_to_target_ref: Mapping[str, str]
    observed_at_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    target_selection_allowed: bool = False
    label_materialization_allowed: bool = False
    scoring_allowed: bool = False
    promotion_allowed: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        registry_id = identifier(self.registry_id, "registry_id")
        registry_version = identifier(self.registry_version, "registry_version")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        target_hashes = dict(sorted(self.target_record_hashes.items()))
        label_hashes = dict(sorted(self.label_record_hashes.items()))
        target_to_labels = {
            key: tuple(value)
            for key, value in sorted(self.target_to_label_refs.items())
        }
        label_to_target = dict(sorted(self.label_to_target_ref.items()))
        if not target_hashes or not label_hashes:
            raise ValueError("runtime snapshot requires targets and labels")
        if set(target_to_labels) != set(target_hashes):
            raise ValueError("target-to-label keys must match target records")
        if set(label_to_target) != set(label_hashes):
            raise ValueError("label-to-target keys must match label records")
        linked_labels = [
            label_ref
            for labels in target_to_labels.values()
            for label_ref in labels
        ]
        if sorted(linked_labels) != sorted(label_hashes):
            raise ValueError("each label must be linked exactly once")
        for target_key, labels in target_to_labels.items():
            if tuple(sorted(set(labels))) != labels:
                raise ValueError("target label references must be unique and sorted")
            if any(label_to_target[label] != target_key for label in labels):
                raise ValueError("target-label indexes disagree")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or any(
                (
                    self.target_selection_allowed,
                    self.label_materialization_allowed,
                    self.scoring_allowed,
                    self.promotion_allowed,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("runtime snapshot exceeds read-only registry authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "registry_version", registry_version)
        object.__setattr__(
            self,
            "target_record_hashes",
            MappingProxyType(target_hashes),
        )
        object.__setattr__(
            self,
            "label_record_hashes",
            MappingProxyType(label_hashes),
        )
        object.__setattr__(
            self,
            "target_to_label_refs",
            MappingProxyType(target_to_labels),
        )
        object.__setattr__(
            self,
            "label_to_target_ref",
            MappingProxyType(label_to_target),
        )
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "label_record_hashes": label_hashes,
                    "label_to_target_ref": label_to_target,
                    "observed_at_utc": observed,
                    "registry_id": registry_id,
                    "registry_version": registry_version,
                    "schema_version": self.schema_version,
                    "target_record_hashes": target_hashes,
                    "target_to_label_refs": target_to_labels,
                }
            ),
        )
