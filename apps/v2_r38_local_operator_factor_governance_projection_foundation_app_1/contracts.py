from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, utc


FIELD_ORIGINS = ("INFERRED", "OBSERVED")
CONFIDENCE_STATES = ("HIGH", "LOW", "MEDIUM", "UNAVAILABLE")
PROJECTION_STATES = (
    "BLOCKED_INTEGRITY",
    "BLOCKED_LIFECYCLE",
    "BLOCKED_MISSING",
    "BLOCKED_VALIDATION",
    "INCOMPLETE",
    "REVIEW_REQUIRED",
)


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True)
class GovernanceProjectionField:
    field_id: str
    value: str
    origin: str
    confidence: str
    source_snapshot_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "field_id", identifier(self.field_id, "field_id"))
        value = str(self.value).strip()
        if not value:
            raise ValueError("projection field value is required")
        object.__setattr__(self, "value", value)
        origin = str(self.origin).strip().upper()
        confidence = str(self.confidence).strip().upper()
        if origin not in FIELD_ORIGINS:
            raise ValueError("projection field origin is not registered")
        if confidence not in CONFIDENCE_STATES:
            raise ValueError("projection field confidence is not registered")
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "confidence", confidence)
        sources = tuple(sorted(str(item).strip().lower() for item in self.source_snapshot_hashes))
        if not sources or len(set(sources)) != len(sources):
            raise ValueError("projection field requires unique source snapshots")
        if any(len(item) != 64 or any(char not in "0123456789abcdef" for char in item) for item in sources):
            raise ValueError("source snapshot hash must be SHA-256")
        object.__setattr__(self, "source_snapshot_hashes", sources)


@dataclass(frozen=True)
class OperatorFactorGovernanceProjection:
    projection_id: str
    candidate_id: str
    factor_id: str
    evidence_series_id: str
    market: str
    evaluated_at_utc: str
    state: str
    confidence: str
    fields: tuple[GovernanceProjectionField, ...]
    reason_codes: tuple[str, ...]
    operator_review_required: bool = True
    read_only: bool = True
    automatic_approval: bool = False
    factor_activation: bool = False
    action_created: bool = False
    projection_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "projection_id",
            "candidate_id",
            "factor_id",
            "evidence_series_id",
            "market",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(
            self,
            "evaluated_at_utc",
            utc(self.evaluated_at_utc, "evaluated_at_utc"),
        )
        state = str(self.state).strip().upper()
        confidence = str(self.confidence).strip().upper()
        if state not in PROJECTION_STATES:
            raise ValueError("projection state is not registered")
        if confidence not in CONFIDENCE_STATES:
            raise ValueError("projection confidence is not registered")
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "confidence", confidence)
        fields = tuple(sorted(self.fields, key=lambda item: item.field_id))
        if not fields or len({item.field_id for item in fields}) != len(fields):
            raise ValueError("projection fields must be nonempty and unique")
        object.__setattr__(self, "fields", fields)
        reasons = tuple(sorted(identifier(item, "reason_code") for item in self.reason_codes))
        if not reasons or len(set(reasons)) != len(reasons):
            raise ValueError("projection requires unique reason codes")
        object.__setattr__(self, "reason_codes", reasons)
        if not self.operator_review_required or not self.read_only:
            raise ValueError("projection must remain read-only and require Operator review")
        if self.automatic_approval or self.factor_activation or self.action_created:
            raise ValueError("projection cannot approve, activate, or create an action")
        object.__setattr__(
            self,
            "projection_hash",
            _digest(
                {
                    "candidate_id": self.candidate_id,
                    "confidence": confidence,
                    "evaluated_at_utc": self.evaluated_at_utc,
                    "evidence_series_id": self.evidence_series_id,
                    "factor_id": self.factor_id,
                    "fields": [
                        [
                            item.field_id,
                            item.value,
                            item.origin,
                            item.confidence,
                            list(item.source_snapshot_hashes),
                        ]
                        for item in fields
                    ],
                    "market": self.market,
                    "projection_id": self.projection_id,
                    "reason_codes": list(reasons),
                    "state": state,
                }
            ),
        )
