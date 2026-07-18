from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from apps.v2_r39_browser_operator_factor_governance_projection_integration_app_1 import (
    parse_registered_browser_governance_projection,
)


@dataclass(frozen=True)
class BrowserGovernanceFieldPresentationRow:
    field_id: str
    value: str
    origin: str
    confidence: str
    source_snapshot_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.origin not in {"OBSERVED", "INFERRED"}:
            raise ValueError("field presentation origin must be explicit")
        if not self.field_id or not self.value or not self.confidence:
            raise ValueError("field presentation values are required")
        if not self.source_snapshot_hashes:
            raise ValueError("field presentation sources are required")
        object.__setattr__(
            self,
            "source_snapshot_hashes",
            tuple(self.source_snapshot_hashes),
        )


@dataclass(frozen=True)
class BrowserFactorGovernanceFieldPresentation:
    artifact_id: str
    projection_id: str
    candidate_id: str
    factor_id: str
    market: str
    evaluated_at_utc: str
    state: str
    confidence: str
    fields: tuple[BrowserGovernanceFieldPresentationRow, ...]
    reason_codes: tuple[str, ...]
    projection_hash: str
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "artifact_id",
            "projection_id",
            "candidate_id",
            "factor_id",
            "market",
            "evaluated_at_utc",
            "state",
            "confidence",
            "projection_hash",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        if not self.fields or not self.reason_codes:
            raise ValueError("field presentation requires fields and reasons")
        if not all(
            (
                self.registered_artifact_only,
                self.read_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("field presentation safety boundary is required")
        object.__setattr__(self, "fields", tuple(self.fields))
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))


def build_factor_governance_field_presentation(
    artifact_id: str,
    payload: Mapping[str, object],
) -> BrowserFactorGovernanceFieldPresentation:
    registered = parse_registered_browser_governance_projection(payload)
    projection = registered.projection
    rows = tuple(
        BrowserGovernanceFieldPresentationRow(
            field_id=field.field_id,
            value=field.value,
            origin=field.origin,
            confidence=field.confidence,
            source_snapshot_hashes=field.source_snapshot_hashes,
        )
        for field in projection.fields
    )
    return BrowserFactorGovernanceFieldPresentation(
        artifact_id=str(artifact_id).strip(),
        projection_id=projection.projection_id,
        candidate_id=projection.candidate_id,
        factor_id=projection.factor_id,
        market=projection.market,
        evaluated_at_utc=projection.evaluated_at_utc,
        state=projection.state,
        confidence=projection.confidence,
        fields=rows,
        reason_codes=projection.reason_codes,
        projection_hash=projection.projection_hash,
    )
