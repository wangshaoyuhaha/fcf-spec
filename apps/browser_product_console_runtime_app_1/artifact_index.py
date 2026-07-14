from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Tuple

from .runtime_artifact_integrity import (
    normalize_registered_relative_path,
    read_runtime_artifact_snapshot,
    resolve_runtime_artifact_path,
)
from .runtime_hardening import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
    RuntimeHardeningLimits,
)


SUPPORTED_ARTIFACT_TYPES = {
    "data_snapshot",
    "data_quality",
    "research_run",
    "workflow_status",
    "ranked_watchlist",
    "ai_explanation",
    "ai_evaluation",
    "paper_validation",
    "shadow_observation",
    "operator_review",
    "report_archive",
    "model_governance",
    "policy_snapshot",
    "audit_receipt",
    "manifest",
}


def _require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_registered_file(
    path: Path,
    allowed_root: Path,
    limits: RuntimeHardeningLimits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    ),
) -> Path:
    return resolve_runtime_artifact_path(
        path,
        allowed_root,
        limits,
    )


def _load_json_bytes(
    content: bytes,
) -> Mapping[str, Any]:
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "artifact must be UTF-8 JSON"
        ) from exc

    try:
        value = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "artifact contains invalid JSON"
        ) from exc

    if not isinstance(value, dict):
        raise ValueError(
            "artifact JSON must be an object"
        )

    return value


@dataclass(frozen=True)
class RegisteredConsoleArtifact:
    artifact_id: str
    artifact_type: str
    correlation_id: str
    relative_path: str
    content_sha256: str

    def __post_init__(self) -> None:
        for field_name in (
            "artifact_id",
            "artifact_type",
            "correlation_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(
                    getattr(self, field_name),
                    field_name,
                ),
            )

        object.__setattr__(
            self,
            "relative_path",
            normalize_registered_relative_path(
                self.relative_path
            ),
        )

        if self.artifact_type not in SUPPORTED_ARTIFACT_TYPES:
            raise ValueError(
                f"unsupported artifact_type: "
                f"{self.artifact_type}"
            )

        digest = _require_text(
            self.content_sha256,
            "content_sha256",
        ).lower()

        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError(
                "content_sha256 must be a SHA-256 digest"
            )

        object.__setattr__(
            self,
            "content_sha256",
            digest,
        )


@dataclass(frozen=True)
class LoadedConsoleArtifact:
    registration: RegisteredConsoleArtifact
    source_path: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.payload, dict):
            raise ValueError(
                "artifact payload must be an object"
            )


@dataclass(frozen=True)
class ConsoleArtifactIndex:
    schema_version: str
    correlation_id: str
    entries: Tuple[RegisteredConsoleArtifact, ...]

    def __post_init__(self) -> None:
        if (
            self.schema_version
            != "fcf.browser_console.artifact_index.v1"
        ):
            raise ValueError(
                "unsupported artifact index schema"
            )

        object.__setattr__(
            self,
            "correlation_id",
            _require_text(
                self.correlation_id,
                "correlation_id",
            ),
        )

        if not self.entries:
            raise ValueError(
                "artifact index must contain entries"
            )

        artifact_ids = tuple(
            item.artifact_id
            for item in self.entries
        )
        relative_paths = tuple(
            item.relative_path
            for item in self.entries
        )

        if len(set(artifact_ids)) != len(artifact_ids):
            raise ValueError(
                "artifact_id values must be unique"
            )

        if len(set(relative_paths)) != len(relative_paths):
            raise ValueError(
                "relative_path values must be unique"
            )

        for entry in self.entries:
            if entry.correlation_id != self.correlation_id:
                raise ValueError(
                    "artifact correlation_id mismatch"
                )


@dataclass(frozen=True)
class LoadedConsoleArtifactIndex:
    index: ConsoleArtifactIndex
    index_path: str
    artifacts: Tuple[LoadedConsoleArtifact, ...]

    def by_type(
        self,
        artifact_type: str,
    ) -> Tuple[LoadedConsoleArtifact, ...]:
        return tuple(
            artifact
            for artifact in self.artifacts
            if (
                artifact.registration.artifact_type
                == artifact_type
            )
        )


def load_console_artifact_index(
    index_path: Path,
    allowed_root: Path,
    *,
    limits: RuntimeHardeningLimits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    ),
) -> LoadedConsoleArtifactIndex:
    if not isinstance(limits, RuntimeHardeningLimits):
        raise ValueError(
            "limits must be RuntimeHardeningLimits"
        )

    root = Path(allowed_root)

    if root.is_symlink():
        raise ValueError(
            "symbolic allowed roots are not permitted"
        )

    resolved_root = root.resolve(strict=True)

    if not resolved_root.is_dir():
        raise ValueError(
            "allowed_root must be a directory"
        )

    resolved_index = _resolve_registered_file(
        index_path,
        resolved_root,
        limits,
    )
    index_snapshot = read_runtime_artifact_snapshot(
        resolved_index,
        resolved_root,
        limits=limits,
    )
    payload = _load_json_bytes(
        index_snapshot.content
    )
    raw_entries = payload.get("entries")

    if not isinstance(raw_entries, list):
        raise ValueError(
            "entries must be an array"
        )

    entries = tuple(
        RegisteredConsoleArtifact(
            artifact_id=item.get("artifact_id", ""),
            artifact_type=item.get(
                "artifact_type",
                "",
            ),
            correlation_id=item.get(
                "correlation_id",
                "",
            ),
            relative_path=item.get(
                "relative_path",
                "",
            ),
            content_sha256=item.get(
                "content_sha256",
                "",
            ),
        )
        for item in raw_entries
        if isinstance(item, dict)
    )

    if len(entries) != len(raw_entries):
        raise ValueError(
            "every artifact index entry "
            "must be an object"
        )

    index = ConsoleArtifactIndex(
        schema_version=str(
            payload.get("schema_version", "")
        ),
        correlation_id=str(
            payload.get("correlation_id", "")
        ),
        entries=entries,
    )

    loaded = []

    for entry in index.entries:
        try:
            source_snapshot = (
                read_runtime_artifact_snapshot(
                    resolved_root
                    / entry.relative_path,
                    resolved_root,
                    expected_sha256=(
                        entry.content_sha256
                    ),
                    limits=limits,
                )
            )
        except ValueError as exc:
            if str(exc) == (
                "registered artifact SHA-256 mismatch"
            ):
                raise ValueError(
                    "artifact SHA-256 mismatch: "
                    f"{entry.artifact_id}"
                ) from exc
            raise

        loaded.append(
            LoadedConsoleArtifact(
                registration=entry,
                source_path=(
                    source_snapshot.resolved_path
                ),
                payload=_load_json_bytes(
                    source_snapshot.content
                ),
            )
        )

    return LoadedConsoleArtifactIndex(
        index=index,
        index_path=str(resolved_index),
        artifacts=tuple(loaded),
    )
