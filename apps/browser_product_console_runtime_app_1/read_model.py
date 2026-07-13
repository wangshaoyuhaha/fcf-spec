
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .artifact_index import LoadedConsoleArtifactIndex


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
class ConsoleReadModel:
    correlation_id: str
    candidates: Tuple[StockCandidateCard, ...]
    sections: Mapping[str, Tuple[Mapping[str, Any], ...]]
    source_artifact_ids: Tuple[str, ...]
    paper_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "correlation_id",
            _require_text(self.correlation_id, "correlation_id"),
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
    sections: dict[str, list[Mapping[str, Any]]] = {}

    for artifact in loaded_index.artifacts:
        artifact_type = artifact.registration.artifact_type
        payload = artifact.payload
        sections.setdefault(artifact_type, []).append(payload)

        if artifact_type == "ranked_watchlist":
            raw_candidates = payload.get("candidates")
            if not isinstance(raw_candidates, list):
                raise ValueError("ranked_watchlist candidates must be an array")
            candidates.extend(
                _candidate_from_payload(item)
                for item in raw_candidates
            )

    candidate_keys = tuple(
        (candidate.rank, candidate.symbol)
        for candidate in candidates
    )
    if len(set(candidate_keys)) != len(candidate_keys):
        raise ValueError("candidate rank and symbol identities must be unique")

    ordered_candidates = tuple(
        sorted(candidates, key=lambda item: (item.rank, item.symbol))
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
    )
