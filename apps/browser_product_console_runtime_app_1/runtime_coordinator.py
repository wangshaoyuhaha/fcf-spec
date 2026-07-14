from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .operator_commands import GovernedOperatorCommandService


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _safe_component(value: str) -> str:
    normalized = value.strip()
    if not normalized or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in normalized):
        raise ValueError("command_id must contain only letters, digits, hyphen, or underscore")
    return normalized


def _resolve_output_root(output_root: Path, allowed_root: Path) -> Path:
    root = Path(allowed_root)
    if root.is_symlink():
        raise ValueError("symbolic allowed roots are not permitted")
    resolved_allowed = root.resolve(strict=True)
    candidate = Path(output_root)
    if candidate.exists() and candidate.is_symlink():
        raise ValueError("symbolic output roots are not permitted")
    candidate.mkdir(parents=True, exist_ok=True)
    resolved_output = candidate.resolve(strict=True)
    try:
        resolved_output.relative_to(resolved_allowed)
    except ValueError as exc:
        raise ValueError("output_root must remain inside allowed_root") from exc
    if not resolved_output.is_dir():
        raise ValueError("output_root must be a directory")
    return resolved_output


def _write_bytes(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


@dataclass(frozen=True)
class ConsoleRuntimeResult:
    command_id: str
    correlation_id: str
    decision: str
    status: str
    output_directory: str
    receipt_sha256: str
    audit_sha256: str
    manifest_sha256: str
    reused_existing_bundle: bool
    paper_only: bool = True
    operator_review_required: bool = True
    automatic_approval: bool = False
    automatic_promotion: bool = False
    automatic_archive: bool = False

    def __post_init__(self) -> None:
        if self.status != "OPERATOR_REVIEW_RECORDED":
            raise ValueError("unexpected runtime result status")
        if not self.paper_only or not self.operator_review_required:
            raise ValueError("runtime result must remain paper-only and reviewed")
        if self.automatic_approval or self.automatic_promotion or self.automatic_archive:
            raise ValueError("automatic governance authority is prohibited")


class ConsoleRuntimeCoordinator:
    def __init__(self, allowed_root: Path, output_root: Path) -> None:
        self._allowed_root = Path(allowed_root)
        self._output_root = _resolve_output_root(output_root, self._allowed_root)
        self._service = GovernedOperatorCommandService(self._allowed_root)

    @property
    def output_root(self) -> Path:
        return self._output_root

    def process_operator_review(
        self,
        payload: Mapping[str, Any],
        evidence_path: Path,
        peer_host: str = "127.0.0.1",
    ) -> ConsoleRuntimeResult:
        validated = self._service.validate(payload, evidence_path, peer_host)
        command = validated.command
        command_id = _safe_component(command.command_id)
        target = self._output_root / command_id

        receipt_payload = {
            "automatic_approval": False,
            "automatic_archive": False,
            "automatic_baseline_replacement": False,
            "automatic_learning_activation": False,
            "automatic_promotion": False,
            "command_id": command.command_id,
            "command_sha256": validated.command_sha256,
            "correlation_id": command.correlation_id,
            "decision": command.decision,
            "evidence_sha256": validated.evidence_sha256,
            "operator_review_required": True,
            "paper_only": True,
            "reviewer_id": command.reviewer_id,
            "status": "OPERATOR_REVIEW_RECORDED",
            "submitted_at_utc": command.submitted_at_utc,
        }
        audit_payload = {
            "action": "RECORD_OPERATOR_REVIEW_ONLY",
            "artifact_id": command.artifact_id,
            "command_id": command.command_id,
            "command_sha256": validated.command_sha256,
            "correlation_id": command.correlation_id,
            "decision": command.decision,
            "evidence_path": validated.evidence_path,
            "evidence_sha256": validated.evidence_sha256,
            "note": command.note,
            "peer_host": peer_host,
            "prohibited_transitions": [
                "automatic_approval",
                "automatic_promotion",
                "automatic_baseline_replacement",
                "automatic_learning_activation",
                "automatic_archive",
                "order_path",
                "real_execution",
            ],
            "reviewer_id": command.reviewer_id,
            "submitted_at_utc": command.submitted_at_utc,
        }
        receipt_bytes = _canonical_bytes(receipt_payload)
        audit_bytes = _canonical_bytes(audit_payload)
        receipt_sha256 = _sha256_bytes(receipt_bytes)
        audit_sha256 = _sha256_bytes(audit_bytes)
        manifest_payload = {
            "audit_file": "audit.json",
            "audit_sha256": audit_sha256,
            "bundle_schema": "fcf.browser_console.operator_review_bundle.v1",
            "command_id": command.command_id,
            "command_sha256": validated.command_sha256,
            "correlation_id": command.correlation_id,
            "receipt_file": "receipt.json",
            "receipt_sha256": receipt_sha256,
        }
        manifest_bytes = _canonical_bytes(manifest_payload)
        manifest_sha256 = _sha256_bytes(manifest_bytes)

        if target.exists():
            return self._reuse_existing(
                target=target,
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                decision=command.decision,
                receipt_bytes=receipt_bytes,
                audit_bytes=audit_bytes,
                manifest_bytes=manifest_bytes,
                receipt_sha256=receipt_sha256,
                audit_sha256=audit_sha256,
                manifest_sha256=manifest_sha256,
            )

        temporary = self._output_root / f".{command_id}.{uuid.uuid4().hex}.tmp"
        temporary.mkdir(parents=False, exist_ok=False)
        try:
            _write_bytes(temporary / "receipt.json", receipt_bytes)
            _write_bytes(temporary / "audit.json", audit_bytes)
            _write_bytes(temporary / "manifest.json", manifest_bytes)
            os.replace(str(temporary), str(target))
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise

        return ConsoleRuntimeResult(
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            decision=command.decision,
            status="OPERATOR_REVIEW_RECORDED",
            output_directory=str(target),
            receipt_sha256=receipt_sha256,
            audit_sha256=audit_sha256,
            manifest_sha256=manifest_sha256,
            reused_existing_bundle=False,
        )

    def _reuse_existing(
        self,
        *,
        target: Path,
        command_id: str,
        correlation_id: str,
        decision: str,
        receipt_bytes: bytes,
        audit_bytes: bytes,
        manifest_bytes: bytes,
        receipt_sha256: str,
        audit_sha256: str,
        manifest_sha256: str,
    ) -> ConsoleRuntimeResult:
        if target.is_symlink() or not target.is_dir():
            raise ValueError("existing review bundle must be a directory")
        expected = {
            "receipt.json": receipt_bytes,
            "audit.json": audit_bytes,
            "manifest.json": manifest_bytes,
        }
        actual_names = {path.name for path in target.iterdir()}
        if actual_names != set(expected):
            raise ValueError("existing review bundle is incomplete or unexpected")
        for name, expected_bytes in expected.items():
            path = target / name
            if path.is_symlink() or not path.is_file():
                raise ValueError("existing review bundle contains invalid paths")
            if path.read_bytes() != expected_bytes:
                raise ValueError("existing review bundle was tampered or command changed")
        return ConsoleRuntimeResult(
            command_id=command_id,
            correlation_id=correlation_id,
            decision=decision,
            status="OPERATOR_REVIEW_RECORDED",
            output_directory=str(target),
            receipt_sha256=receipt_sha256,
            audit_sha256=audit_sha256,
            manifest_sha256=manifest_sha256,
            reused_existing_bundle=True,
        )
