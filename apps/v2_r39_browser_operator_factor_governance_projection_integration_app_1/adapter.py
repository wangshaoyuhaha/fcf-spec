from __future__ import annotations

from apps.v2_r38_local_operator_factor_governance_projection_foundation_app_1 import (
    OperatorFactorGovernanceProjection,
)

from .contracts import SCHEMA_VERSION


def build_registered_browser_governance_projection_payload(
    projection: OperatorFactorGovernanceProjection,
) -> dict[str, object]:
    if not isinstance(projection, OperatorFactorGovernanceProjection):
        raise ValueError("adapter requires an R38 projection")
    return {
        "schema_version": SCHEMA_VERSION,
        "projection_id": projection.projection_id,
        "projection_hash": projection.projection_hash,
        "candidate_id": projection.candidate_id,
        "factor_id": projection.factor_id,
        "evidence_series_id": projection.evidence_series_id,
        "market": projection.market,
        "evaluated_at_utc": projection.evaluated_at_utc,
        "state": projection.state,
        "confidence": projection.confidence,
        "fields": [
            {
                "field_id": field.field_id,
                "value": field.value,
                "origin": field.origin,
                "confidence": field.confidence,
                "source_snapshot_hashes": list(field.source_snapshot_hashes),
            }
            for field in projection.fields
        ],
        "reason_codes": list(projection.reason_codes),
        "operator_review_required": True,
        "read_only": True,
        "automatic_approval": False,
        "factor_activation": False,
        "action_created": False,
    }
