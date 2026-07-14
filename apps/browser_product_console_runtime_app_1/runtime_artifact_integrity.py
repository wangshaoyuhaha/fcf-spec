from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Optional

from .runtime_hardening import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
    RuntimeHardeningLimits,
)


def _require_limits(
    limits: RuntimeHardeningLimits,
) -> RuntimeHardeningLimits:
    if not isinstance(limits, RuntimeHardeningLimits):
        raise ValueError("limits must be RuntimeHardeningLimits")
    return limits


def normalize_registered_relative_path(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("relative_path must be text")

    if (
        not value
        or value != value.strip()
        or "\x00" in value
        or any(ord(character) < 32 for character in value)
    ):
        raise ValueError(
            "relative_path must be non-empty canonical text"
        )

    if ":" in value:
        raise ValueError(
            "relative_path must not contain drive or stream syntax"
        )

    raw_parts = value.replace("\\", "/").split("/")

    if any(part in {"", ".", ".."} for part in raw_parts):
        raise ValueError(
            "artifact path is outside the allowed root or contains traversal segments"
        )

    parsed = PureWindowsPath(value)

    if parsed.is_absolute() or parsed.drive or parsed.root:
        raise ValueError("relative_path must remain relative")

    parts = parsed.parts

    if not parts:
        raise ValueError("relative_path is required")

    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(
            "artifact path is outside the allowed root or contains traversal segments"
        )

    normalized = "/".join(parts)

    if normalized.startswith("/") or normalized.endswith("/"):
        raise ValueError("relative_path is not canonical")

    return normalized


def _resolved_allowed_root(allowed_root: Path) -> Path:
    root = Path(allowed_root)

    if root.is_symlink():
        raise ValueError(
            "symbolic allowed roots are not permitted"
        )

    resolved = root.resolve(strict=True)

    if not resolved.is_dir():
        raise ValueError("allowed_root must be a directory")

    return resolved


def _candidate_relative_parts(
    candidate: Path,
    root: Path,
) -> tuple[str, ...]:
    absolute_candidate = Path(
        os.path.abspath(str(candidate))
    )

    try:
        lexical_relative = absolute_candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            "artifact path is outside the allowed root"
        ) from exc

    parts = lexical_relative.parts

    if not parts:
        raise ValueError(
            "registered artifact path must be a file"
        )

    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(
            "artifact path contains traversal segments"
        )

    return tuple(parts)


def resolve_runtime_artifact_path(
    path: Path,
    allowed_root: Path,
    limits: RuntimeHardeningLimits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    ),
) -> Path:
    active_limits = _require_limits(limits)
    root = _resolved_allowed_root(allowed_root)
    candidate = Path(path)

    if not candidate.is_absolute():
        candidate = root / candidate

    parts = _candidate_relative_parts(
        candidate,
        root,
    )

    current = root

    for part in parts:
        current = current / part

        if current.is_symlink():
            raise ValueError(
                "symbolic artifact paths are not permitted"
            )

    resolved = current.resolve(strict=True)

    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            "artifact path is outside the allowed root"
        ) from exc

    if not resolved.is_file():
        raise ValueError(
            "registered artifact path must be a file"
        )

    size = resolved.stat().st_size

    if size > active_limits.artifact_max_bytes:
        raise ValueError(
            "registered artifact exceeds size limit"
        )

    return resolved


@dataclass(frozen=True)
class RuntimeArtifactSnapshot:
    resolved_path: str
    size_bytes: int
    content_sha256: str
    content: bytes

    def __post_init__(self) -> None:
        path = str(self.resolved_path).strip()

        if not path:
            raise ValueError("resolved_path is required")

        if (
            isinstance(self.size_bytes, bool)
            or not isinstance(self.size_bytes, int)
            or self.size_bytes < 0
        ):
            raise ValueError(
                "size_bytes must be a non-negative integer"
            )

        digest = str(self.content_sha256).strip().lower()

        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError(
                "content_sha256 must be a SHA-256 digest"
            )

        if not isinstance(self.content, bytes):
            raise ValueError("content must be bytes")

        if len(self.content) != self.size_bytes:
            raise ValueError(
                "content size does not match size_bytes"
            )

        object.__setattr__(
            self,
            "resolved_path",
            path,
        )
        object.__setattr__(
            self,
            "content_sha256",
            digest,
        )


def read_runtime_artifact_snapshot(
    path: Path,
    allowed_root: Path,
    expected_sha256: Optional[str] = None,
    limits: RuntimeHardeningLimits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    ),
) -> RuntimeArtifactSnapshot:
    active_limits = _require_limits(limits)
    resolved = resolve_runtime_artifact_path(
        path,
        allowed_root,
        active_limits,
    )

    before = resolved.stat()

    with resolved.open("rb") as handle:
        content = handle.read(
            active_limits.artifact_max_bytes + 1
        )

    after = resolved.stat()

    if len(content) > active_limits.artifact_max_bytes:
        raise ValueError(
            "registered artifact exceeds size limit"
        )

    if (
        before.st_size != after.st_size
        or before.st_mtime_ns != after.st_mtime_ns
        or before.st_size != len(content)
    ):
        raise ValueError(
            "registered artifact changed during read"
        )

    digest = hashlib.sha256(content).hexdigest()

    if expected_sha256 is not None:
        expected = str(expected_sha256).strip().lower()

        if len(expected) != 64 or any(
            character not in "0123456789abcdef"
            for character in expected
        ):
            raise ValueError(
                "expected_sha256 must be a SHA-256 digest"
            )

        if digest != expected:
            raise ValueError(
                "registered artifact SHA-256 mismatch"
            )

    return RuntimeArtifactSnapshot(
        resolved_path=str(resolved),
        size_bytes=len(content),
        content_sha256=digest,
        content=content,
    )
