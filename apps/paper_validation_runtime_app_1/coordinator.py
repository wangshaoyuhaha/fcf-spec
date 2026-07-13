from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

from .domain import (
    PAPER_VALIDATION_RUNTIME_BOUNDARY,
    ValidationRunRequest,
)
from .input_loader import (
    ArtifactRegistryEntry,
    LoadedValidationDataset,
    load_registered_validation_dataset,
)
from .metric_engine import ComparisonPacket, evaluate_candidate
from .packet_builder import (
    ContradictionRecord,
    OperatorReviewPacket,
    RiskFlag,
    ValidationResultPacket,
    build_operator_review_packet,
    build_validation_result_packet,
)


_ALLOWED_FINAL_STATES = {
    "BLOCKED_REVIEW_REQUIRED",
    "REVIEW_PACKET_READY",
}
_SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class LifecycleEvent:
    sequence: int
    from_state: str
    to_state: str
    reason: str

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError("lifecycle event sequence must be positive")
        if not self.from_state.strip() or not self.to_state.strip():
            raise ValueError("lifecycle event states are required")
        if not self.reason.strip():
            raise ValueError("lifecycle event reason is required")

    def as_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class LifecycleTrace:
    run_id: str
    correlation_id: str
    state: str
    events: Tuple[LifecycleEvent, ...]
    fail_closed: bool = True
    operator_review_required: bool = True
    automatic_transition_to_approval_allowed: bool = False

    def __post_init__(self) -> None:
        if self.state not in _ALLOWED_FINAL_STATES:
            raise ValueError("invalid final lifecycle state")
        if not self.events:
            raise ValueError("lifecycle trace must contain events")
        if not self.fail_closed or not self.operator_review_required:
            raise ValueError("lifecycle must remain fail-closed and review-gated")
        if self.automatic_transition_to_approval_allowed:
            raise ValueError("automatic approval transition is prohibited")
        expected = tuple(range(1, len(self.events) + 1))
        actual = tuple(event.sequence for event in self.events)
        if actual != expected:
            raise ValueError("lifecycle event sequence is invalid")
        if self.events[-1].to_state != self.state:
            raise ValueError("final lifecycle event does not match state")

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "state": self.state,
            "events": [event.as_dict() for event in self.events],
            "fail_closed": self.fail_closed,
            "operator_review_required": self.operator_review_required,
            "automatic_transition_to_approval_allowed": (
                self.automatic_transition_to_approval_allowed
            ),
        }


@dataclass(frozen=True)
class ValidationRuntimeOutcome:
    request: ValidationRunRequest
    dataset: LoadedValidationDataset
    comparison: ComparisonPacket
    result_packet: ValidationResultPacket
    operator_review_packet: OperatorReviewPacket
    lifecycle: LifecycleTrace
    operator_triggered: bool = True
    local_only: bool = True
    paper_only: bool = True
    network_access_used: bool = False
    external_data_fetch_used: bool = False
    real_execution_used: bool = False
    automatic_approval_used: bool = False
    automatic_archive_used: bool = False

    def __post_init__(self) -> None:
        if not self.operator_triggered:
            raise ValueError("runtime must be Operator-triggered")
        if not self.local_only or not self.paper_only:
            raise ValueError("runtime must remain local and paper-only")
        prohibited = (
            self.network_access_used,
            self.external_data_fetch_used,
            self.real_execution_used,
            self.automatic_approval_used,
            self.automatic_archive_used,
        )
        if any(prohibited):
            raise ValueError("prohibited runtime behavior was enabled")
        if self.request.run_id != self.result_packet.run_id:
            raise ValueError("runtime result run_id mismatch")
        if self.request.correlation_id != self.result_packet.correlation_id:
            raise ValueError("runtime result correlation_id mismatch")
        if self.operator_review_packet.result_packet != self.result_packet:
            raise ValueError("operator review packet result mismatch")
        if self.lifecycle.run_id != self.request.run_id:
            raise ValueError("lifecycle run_id mismatch")
        if self.lifecycle.correlation_id != self.request.correlation_id:
            raise ValueError("lifecycle correlation_id mismatch")

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.request.run_id,
            "correlation_id": self.request.correlation_id,
            "artifact_id": self.request.artifact_id,
            "artifact_version": self.request.artifact_version,
            "operator_trigger_id": self.request.operator_trigger_id,
            "source_path": self.dataset.source_path,
            "source_sha256": self.dataset.source_sha256,
            "comparison": self.comparison.as_dict(),
            "result_packet": self.result_packet.as_dict(),
            "operator_review_packet": self.operator_review_packet.as_dict(),
            "lifecycle": self.lifecycle.as_dict(),
            "operator_triggered": self.operator_triggered,
            "local_only": self.local_only,
            "paper_only": self.paper_only,
            "network_access_used": self.network_access_used,
            "external_data_fetch_used": self.external_data_fetch_used,
            "real_execution_used": self.real_execution_used,
            "automatic_approval_used": self.automatic_approval_used,
            "automatic_archive_used": self.automatic_archive_used,
        }


@dataclass(frozen=True)
class WrittenValidationBundle:
    run_id: str
    correlation_id: str
    output_directory: str
    validation_result_file: str
    operator_review_file: str
    lifecycle_file: str
    manifest_file: str
    validation_result_sha256: str
    operator_review_sha256: str
    lifecycle_sha256: str
    reused_existing_bundle: bool
    operator_review_required: bool = True
    paper_only: bool = True
    archive_status: str = "NOT_ARCHIVED"

    def __post_init__(self) -> None:
        if not self.operator_review_required or not self.paper_only:
            raise ValueError("written bundle must remain paper-only and review-gated")
        if self.archive_status != "NOT_ARCHIVED":
            raise ValueError("runtime output must not be automatically archived")

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "output_directory": self.output_directory,
            "validation_result_file": self.validation_result_file,
            "operator_review_file": self.operator_review_file,
            "lifecycle_file": self.lifecycle_file,
            "manifest_file": self.manifest_file,
            "validation_result_sha256": self.validation_result_sha256,
            "operator_review_sha256": self.operator_review_sha256,
            "lifecycle_sha256": self.lifecycle_sha256,
            "reused_existing_bundle": self.reused_existing_bundle,
            "operator_review_required": self.operator_review_required,
            "paper_only": self.paper_only,
            "archive_status": self.archive_status,
        }


def _event(
    events: list[LifecycleEvent],
    from_state: str,
    to_state: str,
    reason: str,
) -> None:
    events.append(
        LifecycleEvent(
            sequence=len(events) + 1,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
        )
    )


def run_paper_validation(
    *,
    request: ValidationRunRequest,
    registry_entry: ArtifactRegistryEntry,
    allowed_root: Path,
    risk_flags: Iterable[RiskFlag] = (),
    contradictions: Iterable[ContradictionRecord] = (),
) -> ValidationRuntimeOutcome:
    if PAPER_VALIDATION_RUNTIME_BOUNDARY.mode != "paper_validation":
        raise RuntimeError("paper validation runtime boundary is unavailable")
    if not request.operator_trigger_id.strip():
        raise ValueError("operator_trigger_id is required")

    events: list[LifecycleEvent] = []
    _event(events, "CREATED", "INPUT_LOADING", "Operator-triggered run started")

    dataset = load_registered_validation_dataset(
        request=request,
        registry_entry=registry_entry,
        allowed_root=allowed_root,
    )
    _event(
        events,
        "INPUT_LOADING",
        "INPUT_VALIDATED",
        "Registered artifact identity, hash, and window validated",
    )

    comparison = evaluate_candidate(
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        samples=dataset.samples,
        policy=request.policy,
    )
    _event(
        events,
        "INPUT_VALIDATED",
        "METRICS_EVALUATED",
        "Deterministic baseline and candidate comparison completed",
    )

    result_packet = build_validation_result_packet(
        request=request,
        dataset=dataset,
        comparison=comparison,
        risk_flags=risk_flags,
        contradictions=contradictions,
    )
    _event(
        events,
        "METRICS_EVALUATED",
        "RESULT_PACKET_BUILT",
        "Risk and contradiction evidence preserved in result packet",
    )

    operator_review_packet = build_operator_review_packet(result_packet)
    final_state = (
        "BLOCKED_REVIEW_REQUIRED"
        if result_packet.status == "BLOCKED"
        else "REVIEW_PACKET_READY"
    )
    _event(
        events,
        "RESULT_PACKET_BUILT",
        final_state,
        "Operator review packet created without automatic authority escalation",
    )

    lifecycle = LifecycleTrace(
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        state=final_state,
        events=tuple(events),
    )

    return ValidationRuntimeOutcome(
        request=request,
        dataset=dataset,
        comparison=comparison,
        result_packet=result_packet,
        operator_review_packet=operator_review_packet,
        lifecycle=lifecycle,
    )


def _json_bytes(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _verify_existing_file(path: Path, expected: bytes) -> None:
    if not path.is_file():
        raise ValueError(f"existing validation bundle is incomplete: {path.name}")
    actual = path.read_bytes()
    if actual != expected:
        raise ValueError(f"existing validation bundle content mismatch: {path.name}")


def write_validation_runtime_bundle(
    *,
    outcome: ValidationRuntimeOutcome,
    output_root: Path,
) -> WrittenValidationBundle:
    run_id = outcome.request.run_id
    if not _SAFE_RUN_ID.fullmatch(run_id):
        raise ValueError("run_id is unsafe for local output")

    root = output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_directory = root / run_id

    result_payload = _json_bytes(outcome.result_packet.as_dict())
    review_payload = _json_bytes(outcome.operator_review_packet.as_dict())
    lifecycle_payload = _json_bytes(outcome.lifecycle.as_dict())

    result_sha256 = _sha256_bytes(result_payload)
    review_sha256 = _sha256_bytes(review_payload)
    lifecycle_sha256 = _sha256_bytes(lifecycle_payload)

    manifest_payload = _json_bytes(
        {
            "schema_version": "paper_validation_bundle_manifest_v1",
            "run_id": run_id,
            "correlation_id": outcome.request.correlation_id,
            "artifact_id": outcome.request.artifact_id,
            "artifact_version": outcome.request.artifact_version,
            "source_sha256": outcome.dataset.source_sha256,
            "validation_result_sha256": result_sha256,
            "operator_review_sha256": review_sha256,
            "lifecycle_sha256": lifecycle_sha256,
            "status": outcome.result_packet.status,
            "operator_review_required": True,
            "paper_only": True,
            "archive_status": "NOT_ARCHIVED",
            "automatic_approval_allowed": False,
            "automatic_promotion_allowed": False,
            "automatic_baseline_replacement_allowed": False,
            "automatic_learning_activation_allowed": False,
            "real_execution_allowed": False,
        }
    )

    result_path = run_directory / "validation_result.json"
    review_path = run_directory / "operator_review.json"
    lifecycle_path = run_directory / "lifecycle.json"
    manifest_path = run_directory / "manifest.json"

    reused = False
    if run_directory.exists():
        if not run_directory.is_dir():
            raise ValueError("validation output run path is not a directory")
        _verify_existing_file(result_path, result_payload)
        _verify_existing_file(review_path, review_payload)
        _verify_existing_file(lifecycle_path, lifecycle_payload)
        _verify_existing_file(manifest_path, manifest_payload)
        reused = True
    else:
        run_directory.mkdir()
        try:
            _atomic_write(result_path, result_payload)
            _atomic_write(review_path, review_payload)
            _atomic_write(lifecycle_path, lifecycle_payload)
            _atomic_write(manifest_path, manifest_payload)
        except Exception:
            for path in (
                result_path,
                review_path,
                lifecycle_path,
                manifest_path,
            ):
                if path.exists():
                    path.unlink()
            try:
                run_directory.rmdir()
            except OSError:
                pass
            raise

    return WrittenValidationBundle(
        run_id=run_id,
        correlation_id=outcome.request.correlation_id,
        output_directory=str(run_directory),
        validation_result_file=str(result_path),
        operator_review_file=str(review_path),
        lifecycle_file=str(lifecycle_path),
        manifest_file=str(manifest_path),
        validation_result_sha256=result_sha256,
        operator_review_sha256=review_sha256,
        lifecycle_sha256=lifecycle_sha256,
        reused_existing_bundle=reused,
    )
