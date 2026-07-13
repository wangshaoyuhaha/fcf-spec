from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Tuple

from .domain import (
    EvaluationWindow,
    RegisteredArtifact,
    ValidationRunRequest,
    ValidationSample,
)


@dataclass(frozen=True)
class ArtifactRegistryEntry:
    artifact_id: str
    artifact_version: str
    correlation_id: str
    relative_path: str
    content_sha256: str

    def to_registered_artifact(self) -> RegisteredArtifact:
        return RegisteredArtifact(
            artifact_id=self.artifact_id,
            artifact_version=self.artifact_version,
            correlation_id=self.correlation_id,
            relative_path=self.relative_path,
            content_sha256=self.content_sha256,
        )


@dataclass(frozen=True)
class LoadedValidationDataset:
    artifact: RegisteredArtifact
    window: EvaluationWindow
    samples: Tuple[ValidationSample, ...]
    source_path: str
    source_sha256: str
    operator_review_required: bool = True
    paper_only: bool = True
    read_only_source: bool = True

    def __post_init__(self) -> None:
        if not self.samples:
            raise ValueError("validation dataset must contain samples")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")
        if not self.paper_only or not self.read_only_source:
            raise ValueError("dataset must remain paper-only and read-only")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_local_file(path: Path, allowed_root: Path) -> Path:
    root = allowed_root.resolve(strict=True)
    candidate = path.resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact path is outside the allowed local root") from exc
    if path.is_symlink() or candidate.is_symlink():
        raise ValueError("symbolic links are not allowed for registered artifacts")
    if not candidate.is_file():
        raise ValueError("registered artifact path must be a file")
    return candidate


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array")
    return value


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("registered artifact must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("registered artifact contains invalid JSON") from exc
    return _require_mapping(payload, "artifact")


def _build_window(payload: Mapping[str, Any]) -> EvaluationWindow:
    window = _require_mapping(payload.get("evaluation_window"), "evaluation_window")
    return EvaluationWindow(
        window_id=str(window.get("window_id", "")),
        start_time_utc=str(window.get("start_time_utc", "")),
        decision_cutoff_utc=str(window.get("decision_cutoff_utc", "")),
        observation_cutoff_utc=str(window.get("observation_cutoff_utc", "")),
        end_time_utc=str(window.get("end_time_utc", "")),
    )


def _build_sample(payload: Mapping[str, Any]) -> ValidationSample:
    candidate_value = payload.get("candidate_score")
    return ValidationSample(
        sample_id=str(payload.get("sample_id", "")),
        segment=str(payload.get("segment", "")),
        decision_time_utc=str(payload.get("decision_time_utc", "")),
        outcome_time_utc=str(payload.get("outcome_time_utc", "")),
        baseline_score=float(payload.get("baseline_score")),
        candidate_score=(
            None if candidate_value is None else float(candidate_value)
        ),
        actual_outcome=float(payload.get("actual_outcome")),
        eligible=bool(payload.get("eligible", True)),
        exclusion_reason=str(payload.get("exclusion_reason", "")),
    )


def _validate_window_membership(
    sample: ValidationSample,
    window: EvaluationWindow,
) -> None:
    if sample.decision_time < window.start:
        raise ValueError(
            f"sample {sample.sample_id} decision precedes window start"
        )
    if sample.decision_time > window.decision_cutoff:
        raise ValueError(
            f"sample {sample.sample_id} decision exceeds decision cutoff"
        )
    if sample.outcome_time <= window.decision_cutoff:
        raise ValueError(
            f"sample {sample.sample_id} outcome is not in the observation period"
        )
    if sample.outcome_time > window.observation_cutoff:
        raise ValueError(
            f"sample {sample.sample_id} outcome exceeds observation cutoff"
        )
    if sample.outcome_time > window.end:
        raise ValueError(
            f"sample {sample.sample_id} outcome exceeds window end"
        )


def load_registered_validation_dataset(
    *,
    request: ValidationRunRequest,
    registry_entry: ArtifactRegistryEntry,
    allowed_root: Path,
) -> LoadedValidationDataset:
    artifact = registry_entry.to_registered_artifact()

    if request.artifact_id != artifact.artifact_id:
        raise ValueError("request artifact_id does not match registry")
    if request.artifact_version != artifact.artifact_version:
        raise ValueError("request artifact_version does not match registry")
    if request.correlation_id != artifact.correlation_id:
        raise ValueError("request correlation_id does not match registry")

    source_path = _resolve_local_file(
        allowed_root / artifact.relative_path,
        allowed_root,
    )
    actual_sha256 = sha256_file(source_path)
    if actual_sha256 != artifact.content_sha256:
        raise ValueError("registered artifact SHA-256 mismatch")

    payload = _load_json(source_path)
    expected_identity = {
        "artifact_id": artifact.artifact_id,
        "artifact_version": artifact.artifact_version,
        "correlation_id": artifact.correlation_id,
        "content_type": "paper_validation_samples",
    }
    for field_name, expected_value in expected_identity.items():
        if payload.get(field_name) != expected_value:
            raise ValueError(
                f"artifact {field_name} does not match registered identity"
            )

    window = _build_window(payload)
    if window != request.window:
        raise ValueError("artifact evaluation window does not match request")

    sample_payloads = _require_list(payload.get("samples"), "samples")
    samples = tuple(
        _build_sample(_require_mapping(item, "sample"))
        for item in sample_payloads
    )
    if not samples:
        raise ValueError("artifact samples must not be empty")

    sample_ids = [sample.sample_id for sample in samples]
    if len(set(sample_ids)) != len(sample_ids):
        raise ValueError("artifact sample_id values must be unique")

    for sample in samples:
        _validate_window_membership(sample, window)

    return LoadedValidationDataset(
        artifact=artifact,
        window=window,
        samples=samples,
        source_path=str(source_path),
        source_sha256=actual_sha256,
    )
