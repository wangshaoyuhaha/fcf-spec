from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .artifact_index import LoadedConsoleArtifactIndex
from apps.v2_r39_browser_operator_factor_governance_projection_integration_app_1 import (
    parse_registered_browser_governance_projection,
)


def _require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _string_tuple(value: object, field_name: str) -> Tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array")
    normalized = tuple(_require_text(item, field_name) for item in value)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} values must be unique")
    return normalized


def _score_breakdown(value: object) -> Mapping[str, float]:
    if not isinstance(value, dict):
        raise ValueError("score_breakdown must be an object")
    normalized = {}
    for key, raw_score in value.items():
        name = _require_text(key, "score_breakdown key")
        score = float(raw_score)
        if not 0.0 <= score <= 100.0:
            raise ValueError("score_breakdown values must be between 0 and 100")
        normalized[name] = score
    return MappingProxyType(dict(sorted(normalized.items())))


@dataclass(frozen=True)
class StockCandidateCard:
    symbol: str
    name: str
    rank: int
    total_score: float
    score_breakdown: Mapping[str, float]
    reason_codes: Tuple[str, ...]
    risk_flags: Tuple[str, ...]
    data_quality_state: str
    confidence_level: str
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _require_text(self.symbol, "symbol"))
        object.__setattr__(self, "name", _require_text(self.name, "name"))
        if int(self.rank) < 1:
            raise ValueError("rank must be positive")
        object.__setattr__(self, "rank", int(self.rank))
        score = float(self.total_score)
        if not 0.0 <= score <= 100.0:
            raise ValueError("total_score must be between 0 and 100")
        object.__setattr__(self, "total_score", score)
        object.__setattr__(
            self,
            "score_breakdown",
            _score_breakdown(dict(self.score_breakdown)),
        )
        object.__setattr__(
            self,
            "reason_codes",
            tuple(self.reason_codes),
        )
        object.__setattr__(
            self,
            "risk_flags",
            tuple(self.risk_flags),
        )
        object.__setattr__(
            self,
            "data_quality_state",
            _require_text(self.data_quality_state, "data_quality_state"),
        )
        object.__setattr__(
            self,
            "confidence_level",
            _require_text(self.confidence_level, "confidence_level"),
        )
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")


@dataclass(frozen=True)
class ConsoleArtifactRecord:
    artifact_id: str
    artifact_type: str
    relative_path: str
    content_sha256: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "artifact_id",
            _require_text(self.artifact_id, "artifact_id"),
        )
        object.__setattr__(
            self,
            "artifact_type",
            _require_text(self.artifact_type, "artifact_type"),
        )
        object.__setattr__(
            self,
            "relative_path",
            _require_text(self.relative_path, "relative_path"),
        )
        digest = _require_text(self.content_sha256, "content_sha256").lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError("content_sha256 must be a SHA-256 digest")
        if not isinstance(self.payload, Mapping):
            raise ValueError("artifact record payload must be a mapping")
        object.__setattr__(self, "content_sha256", digest)
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True)
class ConsoleReadModel:
    correlation_id: str
    candidates: Tuple[StockCandidateCard, ...]
    sections: Mapping[str, Tuple[Mapping[str, Any], ...]]
    source_artifact_ids: Tuple[str, ...]
    artifact_records: Tuple[ConsoleArtifactRecord, ...] = field(
        default_factory=tuple
    )
    paper_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "correlation_id",
            _require_text(self.correlation_id, "correlation_id"),
        )
        object.__setattr__(self, "candidates", tuple(self.candidates))
        object.__setattr__(
            self,
            "source_artifact_ids",
            tuple(self.source_artifact_ids),
        )
        object.__setattr__(
            self,
            "artifact_records",
            tuple(self.artifact_records),
        )
        if len(set(self.source_artifact_ids)) != len(
            self.source_artifact_ids
        ):
            raise ValueError("source_artifact_ids must be unique")
        if self.artifact_records:
            record_ids = tuple(
                record.artifact_id for record in self.artifact_records
            )
            if len(set(record_ids)) != len(record_ids):
                raise ValueError("artifact record ids must be unique")
            if set(record_ids) != set(self.source_artifact_ids):
                raise ValueError(
                    "artifact records must match source_artifact_ids"
                )
        if not self.paper_only or not self.read_only:
            raise ValueError("read model must remain paper-only and read-only")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")


def _candidate_from_payload(value: object) -> StockCandidateCard:
    if not isinstance(value, dict):
        raise ValueError("candidate must be an object")
    return StockCandidateCard(
        symbol=value.get("symbol", ""),
        name=value.get("name", ""),
        rank=int(value.get("rank", 0)),
        total_score=float(value.get("total_score", 0.0)),
        score_breakdown=_score_breakdown(
            value.get("score_breakdown", {})
        ),
        reason_codes=_string_tuple(
            value.get("reason_codes", []),
            "reason_codes",
        ),
        risk_flags=_string_tuple(
            value.get("risk_flags", []),
            "risk_flags",
        ),
        data_quality_state=value.get("data_quality_state", ""),
        confidence_level=value.get("confidence_level", ""),
        operator_review_required=bool(
            value.get("operator_review_required", False)
        ),
    )


def build_console_read_model(
    loaded_index: LoadedConsoleArtifactIndex,
) -> ConsoleReadModel:
    candidates = []
    records = []
    sections: dict[str, list[Mapping[str, Any]]] = {}

    for artifact in loaded_index.artifacts:
        registration = artifact.registration
        artifact_type = registration.artifact_type
        payload = artifact.payload
        if artifact_type == "factor_governance_projection":
            parse_registered_browser_governance_projection(payload)
        sections.setdefault(artifact_type, []).append(payload)
        records.append(
            ConsoleArtifactRecord(
                artifact_id=registration.artifact_id,
                artifact_type=artifact_type,
                relative_path=registration.relative_path,
                content_sha256=registration.content_sha256,
                payload=payload,
            )
        )

        if artifact_type == "ranked_watchlist":
            raw_candidates = payload.get("candidates")
            if not isinstance(raw_candidates, list):
                raise ValueError(
                    "ranked_watchlist candidates must be an array"
                )
            candidates.extend(
                _candidate_from_payload(item)
                for item in raw_candidates
            )

    candidate_keys = tuple(
        (candidate.rank, candidate.symbol)
        for candidate in candidates
    )
    if len(set(candidate_keys)) != len(candidate_keys):
        raise ValueError(
            "candidate rank and symbol identities must be unique"
        )

    ordered_candidates = tuple(
        sorted(candidates, key=lambda item: (item.rank, item.symbol))
    )
    ordered_records = tuple(
        sorted(
            records,
            key=lambda item: (item.artifact_type, item.artifact_id),
        )
    )
    frozen_sections = MappingProxyType(
        {
            key: tuple(value)
            for key, value in sorted(sections.items())
        }
    )

    return ConsoleReadModel(
        correlation_id=loaded_index.index.correlation_id,
        candidates=ordered_candidates,
        sections=frozen_sections,
        source_artifact_ids=tuple(
            artifact.registration.artifact_id
            for artifact in loaded_index.artifacts
        ),
        artifact_records=ordered_records,
    )
