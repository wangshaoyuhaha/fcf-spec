from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from .contracts import (
    GatewayReadReceipt,
    GatewayReadRequest,
    GatewayReadStatus,
    RegisteredArtifactSource,
)
from .registry import RegisteredArtifactRegistry


DEFAULT_MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


class RegisteredArtifactReadError(ValueError):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def _raise(reason_code: str) -> None:
    raise RegisteredArtifactReadError(reason_code)


def _resolved_allowed_root(allowed_root: Path) -> Path:
    root = Path(allowed_root)
    if root.is_symlink():
        _raise("symbolic-allowed-root-prohibited")
    try:
        resolved = root.resolve(strict=True)
    except OSError:
        _raise("allowed-root-unavailable")
    if not resolved.is_dir():
        _raise("allowed-root-not-directory")
    return resolved


def resolve_registered_artifact_path(
    allowed_root: Path,
    source: RegisteredArtifactSource,
) -> Path:
    if not isinstance(source, RegisteredArtifactSource):
        raise TypeError("source must be a RegisteredArtifactSource")
    root = _resolved_allowed_root(allowed_root)
    current = root
    for segment in source.relative_path.split("/"):
        current = current / segment
        if current.is_symlink():
            _raise("symbolic-artifact-path-prohibited")
    try:
        resolved = current.resolve(strict=True)
    except OSError:
        _raise("registered-artifact-unavailable")
    try:
        resolved.relative_to(root)
    except ValueError:
        _raise("registered-artifact-outside-allowed-root")
    if not resolved.is_file():
        _raise("registered-artifact-not-file")
    return resolved


@dataclass(frozen=True)
class VerifiedArtifactRead:
    source: RegisteredArtifactSource
    content: bytes
    receipt: GatewayReadReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.source, RegisteredArtifactSource):
            raise TypeError("source must be a RegisteredArtifactSource")
        if not isinstance(self.content, bytes):
            raise TypeError("content must be immutable bytes")
        if not isinstance(self.receipt, GatewayReadReceipt):
            raise TypeError("receipt must be a GatewayReadReceipt")
        digest = hashlib.sha256(self.content).hexdigest()
        if self.receipt.status is not GatewayReadStatus.VERIFIED:
            raise ValueError("verified artifact read requires a VERIFIED receipt")
        if self.receipt.source_id != self.source.source_id:
            raise ValueError("receipt source_id mismatch")
        if self.receipt.evidence_id != self.source.evidence_id:
            raise ValueError("receipt evidence_id mismatch")
        if self.receipt.artifact_format is not self.source.artifact_format:
            raise ValueError("receipt artifact_format mismatch")
        if self.receipt.actual_sha256 != digest:
            raise ValueError("receipt SHA-256 mismatch")
        if self.receipt.byte_length != len(self.content):
            raise ValueError("receipt byte_length mismatch")


class LocalRegisteredArtifactReader:
    def __init__(
        self,
        allowed_root: Path,
        max_artifact_bytes: int = DEFAULT_MAX_ARTIFACT_BYTES,
    ) -> None:
        if (
            isinstance(max_artifact_bytes, bool)
            or not isinstance(max_artifact_bytes, int)
            or max_artifact_bytes <= 0
        ):
            raise ValueError("max_artifact_bytes must be a positive integer")
        self._allowed_root = _resolved_allowed_root(Path(allowed_root))
        self._max_artifact_bytes = max_artifact_bytes

    @property
    def allowed_root(self) -> Path:
        return self._allowed_root

    @property
    def max_artifact_bytes(self) -> int:
        return self._max_artifact_bytes

    def read(
        self,
        request: GatewayReadRequest,
        registry: RegisteredArtifactRegistry,
    ) -> VerifiedArtifactRead:
        if not isinstance(request, GatewayReadRequest):
            raise TypeError("request must be a GatewayReadRequest")
        if not isinstance(registry, RegisteredArtifactRegistry):
            raise TypeError("registry must be a RegisteredArtifactRegistry")
        try:
            source = registry.require(request.source_id)
        except KeyError:
            _raise("source-not-registered")
        path = resolve_registered_artifact_path(self._allowed_root, source)
        try:
            declared_size = path.stat().st_size
        except OSError:
            _raise("registered-artifact-unavailable")
        if declared_size > self._max_artifact_bytes:
            _raise("registered-artifact-size-limit-exceeded")
        try:
            with path.open("rb") as handle:
                content = handle.read(self._max_artifact_bytes + 1)
                opened_size = os.fstat(handle.fileno()).st_size
        except OSError:
            _raise("registered-artifact-read-failed")
        if len(content) > self._max_artifact_bytes:
            _raise("registered-artifact-size-limit-exceeded")
        if opened_size != len(content) or declared_size != opened_size:
            _raise("registered-artifact-mutated-during-read")
        actual_sha256 = hashlib.sha256(content).hexdigest()
        if actual_sha256 != source.expected_sha256:
            _raise("registered-artifact-checksum-mismatch")
        receipt = GatewayReadReceipt(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            source_id=source.source_id,
            evidence_id=source.evidence_id,
            status=GatewayReadStatus.VERIFIED,
            artifact_format=source.artifact_format,
            actual_sha256=actual_sha256,
            byte_length=len(content),
        )
        return VerifiedArtifactRead(
            source=source,
            content=content,
            receipt=receipt,
        )
