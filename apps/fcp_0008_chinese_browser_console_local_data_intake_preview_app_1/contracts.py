from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


SUPPORTED_LOCALES = ("zh-CN", "en")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")


def _identifier(value: object, name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return normalized


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip().lower()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ConsoleLocale:
    locale_id: str = "zh-CN"

    def __post_init__(self) -> None:
        if self.locale_id not in SUPPORTED_LOCALES:
            raise ValueError("unsupported console locale")


@dataclass(frozen=True)
class RegisteredLocalCSVArtifact:
    artifact_id: str
    source_id: str
    artifact_sha256: str
    byte_length: int
    rights_state: str = "UNRESOLVED"
    retention_state: str = "UNRESOLVED"
    usage_scope: str = "LOCAL_EVALUATION_ONLY"
    provider_selected: bool = False
    raw_repository_storage_allowed: bool = False
    redistribution_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", _identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", _identifier(self.source_id, "source_id"))
        object.__setattr__(
            self,
            "artifact_sha256",
            _sha256(self.artifact_sha256, "artifact_sha256"),
        )
        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or not 1 <= self.byte_length <= 10_000_000
        ):
            raise ValueError("byte_length must be within the local preview limit")
        if self.rights_state != "UNRESOLVED" or self.retention_state != "UNRESOLVED":
            raise ValueError("local preview rights must remain unresolved")
        if self.usage_scope != "LOCAL_EVALUATION_ONLY":
            raise ValueError("local preview usage must remain evaluation only")
        if (
            self.provider_selected
            or self.raw_repository_storage_allowed
            or self.redistribution_allowed
        ):
            raise ValueError("local preview cannot grant provider or storage authority")


@dataclass(frozen=True)
class LocalCSVPreview:
    artifact_id: str
    source_id: str
    source_artifact_sha256: str
    normalized_csv_sha256: str
    schema_sha256: str
    columns: tuple[str, ...]
    row_count: int
    repeated_bom_count: int
    schema_state: str = "READY_FOR_REGISTERED_LOCAL_PREVIEW"
    product_evidence_state: str = "BLOCKED"
    rights_state: str = "UNRESOLVED"
    retention_state: str = "UNRESOLVED"
    read_only: bool = True
    source_mutated: bool = False
    automatic_registration: bool = False
    provider_selected: bool = False
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", _identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", _identifier(self.source_id, "source_id"))
        for field_name in (
            "source_artifact_sha256",
            "normalized_csv_sha256",
            "schema_sha256",
        ):
            object.__setattr__(
                self,
                field_name,
                _sha256(getattr(self, field_name), field_name),
            )
        if not self.columns or len(set(self.columns)) != len(self.columns):
            raise ValueError("preview columns must be nonempty and unique")
        if self.row_count <= 0 or self.row_count > 100_000:
            raise ValueError("preview row_count is outside the bounded range")
        if self.repeated_bom_count < 0:
            raise ValueError("repeated_bom_count must be nonnegative")
        if self.schema_state != "READY_FOR_REGISTERED_LOCAL_PREVIEW":
            raise ValueError("unexpected local preview schema state")
        if self.product_evidence_state != "BLOCKED":
            raise ValueError("local preview cannot satisfy product evidence")
        if self.rights_state != "UNRESOLVED" or self.retention_state != "UNRESOLVED":
            raise ValueError("local preview rights must remain unresolved")
        if (
            not self.read_only
            or self.source_mutated
            or self.automatic_registration
            or self.provider_selected
            or not self.operator_review_required
        ):
            raise ValueError("local preview authority boundary was weakened")

    def as_mapping(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "artifact_id": self.artifact_id,
                "automatic_registration": False,
                "columns": self.columns,
                "normalized_csv_sha256": self.normalized_csv_sha256,
                "operator_review_required": True,
                "product_evidence_state": self.product_evidence_state,
                "provider_selected": False,
                "read_only": True,
                "repeated_bom_count": self.repeated_bom_count,
                "retention_state": self.retention_state,
                "rights_state": self.rights_state,
                "row_count": self.row_count,
                "schema_sha256": self.schema_sha256,
                "schema_state": self.schema_state,
                "source_artifact_sha256": self.source_artifact_sha256,
                "source_id": self.source_id,
                "source_mutated": False,
            }
        )
