from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Tuple

from .domain import (
    ObservationRecord,
    ShadowObservationRequest,
)


@dataclass(frozen=True)
class LoadedObservationDataset:
    request: ShadowObservationRequest
    records: Tuple[ObservationRecord, ...]
    source_path: str
    source_sha256: str
    operator_review_required: bool = True
    paper_only: bool = True
    local_only: bool = True
    read_only_source: bool = True

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("observation dataset must contain records")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")
        if not self.paper_only or not self.local_only:
            raise ValueError("dataset must remain paper-only and local-only")
        if not self.read_only_source:
            raise ValueError("source must remain read-only")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_local_file(
    path: Path,
    allowed_root: Path,
) -> Path:
    root = allowed_root.resolve(strict=True)
    if path.is_symlink():
        raise ValueError("symbolic links are not allowed")
    candidate = path.resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            "artifact path is outside the allowed local root"
        ) from exc
    if candidate.is_symlink():
        raise ValueError("symbolic links are not allowed")
    if not candidate.is_file():
        raise ValueError("registered artifact path must be a file")
    return candidate


def _require_mapping(
    value: Any,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _require_list(
    value: Any,
    field_name: str,
) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array")
    return value


def _read_payload(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("artifact must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("artifact contains invalid JSON") from exc
    return _require_mapping(payload, "artifact")


def _build_record(payload: Mapping[str, Any]) -> ObservationRecord:
    candidate = payload.get("candidate_score")
    outcome = payload.get("actual_outcome")
    return ObservationRecord(
        record_id=str(payload.get("record_id", "")),
        correlation_id=str(payload.get("correlation_id", "")),
        segment=str(payload.get("segment", "")),
        decision_time_utc=str(payload.get("decision_time_utc", "")),
        observation_time_utc=str(payload.get("observation_time_utc", "")),
        baseline_score=float(payload.get("baseline_score")),
        candidate_score=(
            None
            if candidate is None
            else float(candidate)
        ),
        actual_outcome=(
            None
            if outcome is None
            else float(outcome)
        ),
        risk_flags=tuple(payload.get("risk_flags", [])),
        contradiction_evidence=tuple(
            payload.get("contradiction_evidence", [])
        ),
    )


def load_registered_observation_dataset(
    request: ShadowObservationRequest,
    allowed_root: Path,
) -> LoadedObservationDataset:
    source = _resolve_local_file(
        allowed_root / request.artifact.relative_path,
        allowed_root,
    )
    actual_sha256 = sha256_file(source)
    if actual_sha256 != request.artifact.content_sha256:
        raise ValueError("registered artifact SHA-256 mismatch")

    payload = _read_payload(source)
    if payload.get("schema_version") != "shadow_observation.v1":
        raise ValueError(
            "schema_version must be shadow_observation.v1"
        )

    artifact = _require_mapping(
        payload.get("artifact"),
        "artifact",
    )
    expected_identity = {
        "artifact_id": request.artifact.artifact_id,
        "artifact_version": request.artifact.artifact_version,
        "correlation_id": request.correlation_id,
    }
    for field_name, expected_value in expected_identity.items():
        if artifact.get(field_name) != expected_value:
            raise ValueError(
                f"artifact {field_name} does not match registration"
            )

    window = _require_mapping(
        payload.get("observation_window"),
        "observation_window",
    )
    expected_window = {
        "window_id": request.window.window_id,
        "decision_time_utc": request.window.decision_time_utc,
        "observation_start_utc": request.window.observation_start_utc,
        "observation_cutoff_utc": request.window.observation_cutoff_utc,
    }
    for field_name, expected_value in expected_window.items():
        if window.get(field_name) != expected_value:
            raise ValueError(
                f"observation window {field_name} does not match request"
            )

    records = tuple(
        _build_record(_require_mapping(item, "record"))
        for item in _require_list(payload.get("records"), "records")
    )
    if not records:
        raise ValueError("observation dataset must contain records")

    record_ids = tuple(record.record_id for record in records)
    if len(set(record_ids)) != len(record_ids):
        raise ValueError("record_id values must be unique")

    for record in records:
        if record.correlation_id != request.correlation_id:
            raise ValueError(
                "record correlation_id must match request correlation_id"
            )
        if record.decision_time > request.window.decision_time:
            raise ValueError(
                "record decision time exceeds registered decision time"
            )
        if not (
            request.window.observation_start
            <= record.observation_time
            <= request.window.observation_cutoff
        ):
            raise ValueError(
                "record observation time is outside the observation window"
            )

    return LoadedObservationDataset(
        request=request,
        records=records,
        source_path=str(source),
        source_sha256=actual_sha256,
    )
