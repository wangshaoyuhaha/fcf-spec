from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.v2_r38_local_operator_factor_governance_projection_foundation_app_1 import (
    GovernanceProjectionField,
    OperatorFactorGovernanceProjection,
)


SCHEMA_VERSION = "fcf.browser_console.factor_governance_projection.v1"
ARTIFACT_TYPE = "factor_governance_projection"
FIELD_ORIGINS = ("INFERRED", "OBSERVED")


def _required_text(payload: Mapping[str, object], key: str) -> str:
    value = str(payload.get(key, "")).strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def _string_tuple(payload: Mapping[str, object], key: str) -> tuple[str, ...]:
    raw = payload.get(key)
    if not isinstance(raw, list):
        raise ValueError(f"{key} must be an array")
    values = tuple(str(item).strip() for item in raw)
    if any(not item for item in values) or len(set(values)) != len(values):
        raise ValueError(f"{key} values must be nonempty and unique")
    return values


@dataclass(frozen=True)
class RegisteredBrowserGovernanceProjection:
    projection: OperatorFactorGovernanceProjection
    payload: Mapping[str, object]
    artifact_type: str = ARTIFACT_TYPE
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.projection, OperatorFactorGovernanceProjection):
            raise ValueError("browser artifact requires an R38 projection")
        if self.artifact_type != ARTIFACT_TYPE:
            raise ValueError("browser governance artifact type mismatch")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError("browser governance artifact must remain registered and read-only")
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def parse_registered_browser_governance_projection(
    payload: Mapping[str, object],
) -> RegisteredBrowserGovernanceProjection:
    if not isinstance(payload, Mapping):
        raise ValueError("factor governance projection payload must be a mapping")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported factor governance projection schema")
    raw_fields = payload.get("fields")
    if not isinstance(raw_fields, list) or not raw_fields:
        raise ValueError("fields must be a nonempty array")
    fields = []
    for raw in raw_fields:
        if not isinstance(raw, Mapping):
            raise ValueError("every projection field must be an object")
        origin = _required_text(raw, "origin").upper()
        if origin not in FIELD_ORIGINS:
            raise ValueError("projection field origin is not registered")
        fields.append(
            GovernanceProjectionField(
                field_id=_required_text(raw, "field_id"),
                value=_required_text(raw, "value"),
                origin=origin,
                confidence=_required_text(raw, "confidence"),
                source_snapshot_hashes=_string_tuple(raw, "source_snapshot_hashes"),
            )
        )
    projection = OperatorFactorGovernanceProjection(
        projection_id=_required_text(payload, "projection_id"),
        candidate_id=_required_text(payload, "candidate_id"),
        factor_id=_required_text(payload, "factor_id"),
        evidence_series_id=_required_text(payload, "evidence_series_id"),
        market=_required_text(payload, "market"),
        evaluated_at_utc=_required_text(payload, "evaluated_at_utc"),
        state=_required_text(payload, "state"),
        confidence=_required_text(payload, "confidence"),
        fields=tuple(fields),
        reason_codes=_string_tuple(payload, "reason_codes"),
        operator_review_required=payload.get("operator_review_required") is True,
        read_only=payload.get("read_only") is True,
        automatic_approval=payload.get("automatic_approval") is True,
        factor_activation=payload.get("factor_activation") is True,
        action_created=payload.get("action_created") is True,
    )
    if payload.get("projection_hash") != projection.projection_hash:
        raise ValueError("factor governance projection hash mismatch")
    return RegisteredBrowserGovernanceProjection(projection, payload)
