from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


ALLOWED_OPERATOR_DECISIONS = {
    "ACKNOWLEDGE_EVIDENCE",
    "REJECT_CANDIDATE",
    "REQUEST_REVISION",
}


def _require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _require_sha256(value: object, field_name: str) -> str:
    digest = str(value).strip().lower()
    if len(digest) != 64 or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise ValueError(f"{field_name} must be a SHA-256 digest")
    return digest


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _resolve_registered_evidence(path: Path, allowed_root: Path) -> Path:
    root = Path(allowed_root)
    if root.is_symlink():
        raise ValueError("symbolic allowed roots are not permitted")
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise ValueError("allowed_root must be a directory")
    candidate = Path(path)
    if candidate.is_symlink():
        raise ValueError("symbolic evidence paths are not permitted")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("evidence path is outside the allowed root") from exc
    if not resolved.is_file():
        raise ValueError("evidence path must be a file")
    return resolved


@dataclass(frozen=True)
class ConsoleOperatorCommandBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    registered_evidence_only: bool = True
    operator_present_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.registered_evidence_only,
            self.operator_present_required,
            self.deterministic_authority,
            self.ai_advisory_only,
        )
        if not all(required):
            raise ValueError("operator command authority flags must remain enabled")
        prohibited = (
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited operator command capability cannot be enabled")


BROWSER_CONSOLE_OPERATOR_COMMAND_BOUNDARY = ConsoleOperatorCommandBoundary()


@dataclass(frozen=True)
class OperatorReviewCommand:
    command_id: str
    correlation_id: str
    artifact_id: str
    expected_artifact_sha256: str
    decision: str
    reviewer_id: str
    submitted_at_utc: str
    note: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "command_id",
            "correlation_id",
            "artifact_id",
            "reviewer_id",
            "submitted_at_utc",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "expected_artifact_sha256",
            _require_sha256(
                self.expected_artifact_sha256,
                "expected_artifact_sha256",
            ),
        )
        normalized_decision = _require_text(self.decision, "decision").upper()
        if normalized_decision not in ALLOWED_OPERATOR_DECISIONS:
            raise ValueError(f"unsupported operator decision: {normalized_decision}")
        object.__setattr__(self, "decision", normalized_decision)
        normalized_note = str(self.note).strip()
        if normalized_decision in {"REJECT_CANDIDATE", "REQUEST_REVISION"} and not normalized_note:
            raise ValueError("note is required for rejection or revision")
        object.__setattr__(self, "note", normalized_note)

    def as_payload(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "artifact_id": self.artifact_id,
                "command_id": self.command_id,
                "correlation_id": self.correlation_id,
                "decision": self.decision,
                "expected_artifact_sha256": self.expected_artifact_sha256,
                "note": self.note,
                "reviewer_id": self.reviewer_id,
                "submitted_at_utc": self.submitted_at_utc,
            }
        )

    @property
    def command_sha256(self) -> str:
        return _sha256_bytes(_canonical_bytes(dict(self.as_payload())))


@dataclass(frozen=True)
class ValidatedOperatorReviewCommand:
    command: OperatorReviewCommand
    evidence_path: str
    evidence_sha256: str
    command_sha256: str
    peer_host: str
    paper_only: bool = True
    operator_review_required: bool = True
    automatic_transition_allowed: bool = False

    def __post_init__(self) -> None:
        if self.peer_host != "127.0.0.1":
            raise ValueError("operator command peer must be exactly 127.0.0.1")
        if not self.paper_only or not self.operator_review_required:
            raise ValueError("operator command must remain paper-only and reviewed")
        if self.automatic_transition_allowed:
            raise ValueError("automatic governance transition is prohibited")


@dataclass(frozen=True)
class OperatorApiResponse:
    status: int
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.status < 100 or self.status > 599:
            raise ValueError("invalid API status")


class GovernedOperatorCommandService:
    def __init__(self, allowed_root: Path) -> None:
        self._allowed_root = Path(allowed_root)

    @property
    def allowed_root(self) -> Path:
        return self._allowed_root

    def validate(
        self,
        payload: Mapping[str, Any],
        evidence_path: Path,
        peer_host: str,
    ) -> ValidatedOperatorReviewCommand:
        if peer_host != "127.0.0.1":
            raise ValueError("operator command peer must be exactly 127.0.0.1")
        if not isinstance(payload, dict):
            raise ValueError("operator command payload must be an object")
        command = OperatorReviewCommand(
            command_id=payload.get("command_id", ""),
            correlation_id=payload.get("correlation_id", ""),
            artifact_id=payload.get("artifact_id", ""),
            expected_artifact_sha256=payload.get("expected_artifact_sha256", ""),
            decision=payload.get("decision", ""),
            reviewer_id=payload.get("reviewer_id", ""),
            submitted_at_utc=payload.get("submitted_at_utc", ""),
            note=payload.get("note", ""),
        )
        resolved = _resolve_registered_evidence(evidence_path, self._allowed_root)
        actual_sha256 = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if actual_sha256 != command.expected_artifact_sha256:
            raise ValueError("registered evidence SHA-256 mismatch")
        return ValidatedOperatorReviewCommand(
            command=command,
            evidence_path=str(resolved),
            evidence_sha256=actual_sha256,
            command_sha256=command.command_sha256,
            peer_host=peer_host,
        )


def handle_operator_api_request(
    method: str,
    path: str,
    peer_host: str,
    payload: Mapping[str, Any],
    evidence_path: Path,
    service: GovernedOperatorCommandService,
) -> OperatorApiResponse:
    if peer_host != "127.0.0.1":
        return OperatorApiResponse(
            status=403,
            payload=MappingProxyType({"error": "loopback peer required"}),
        )
    if path != "/api/operator-review/validate":
        return OperatorApiResponse(
            status=404,
            payload=MappingProxyType({"error": "not found"}),
        )
    if method.upper().strip() != "POST":
        return OperatorApiResponse(
            status=405,
            payload=MappingProxyType({"error": "method not allowed"}),
        )
    try:
        validated = service.validate(payload, evidence_path, peer_host)
    except (OSError, ValueError) as exc:
        return OperatorApiResponse(
            status=400,
            payload=MappingProxyType({"error": str(exc), "status": "BLOCKED"}),
        )
    return OperatorApiResponse(
        status=200,
        payload=MappingProxyType(
            {
                "automatic_transition_allowed": False,
                "command_id": validated.command.command_id,
                "command_sha256": validated.command_sha256,
                "decision": validated.command.decision,
                "operator_review_required": True,
                "paper_only": True,
                "status": "VALIDATED_OPERATOR_COMMAND",
            }
        ),
    )
