from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.fcp_0042_a_share_cross_source_operator_delta_review_packet_app_1.contracts import (
    FINDING_ORDER,
)


REVIEW_DISPOSITIONS = (
    "REVIEWED_NO_RESOLUTION",
    "DEFERRED_PENDING_EVIDENCE",
    "ESCALATED_FOR_RESEARCH",
)
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")


def safe_identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not SAFE_IDENTIFIER.fullmatch(value):
        raise ValueError(f"{name} must be a safe identifier")
    return value


def registered_utc(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{name} must be an ISO UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{name} must be an ISO UTC timestamp")
    return value


@dataclass(frozen=True)
class OperatorDeltaReviewReceipt:
    packet_hash: str
    ledger_hash: str
    review_id: str
    reviewer_reference: str
    reviewed_at_utc: str
    disposition: str
    packet_review_state: str
    finding_codes: tuple[str, ...]
    field_fact_hashes: tuple[str, ...]
    operator_review_completed: bool = True
    evidence_validated: bool = False
    evidence_rejected: bool = False
    severity_assigned: bool = False
    recommendation_generated: bool = False
    threshold_set: bool = False
    source_ranked: bool = False
    source_selected: bool = False
    evidence_replaced: bool = False
    gap_closed: bool = False
    receipt_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "packet_hash", digest(self.packet_hash, "packet_hash"))
        object.__setattr__(self, "ledger_hash", digest(self.ledger_hash, "ledger_hash"))
        object.__setattr__(self, "review_id", safe_identifier(self.review_id, "review_id"))
        object.__setattr__(
            self,
            "reviewer_reference",
            safe_identifier(self.reviewer_reference, "reviewer_reference"),
        )
        object.__setattr__(
            self,
            "reviewed_at_utc",
            registered_utc(self.reviewed_at_utc, "reviewed_at_utc"),
        )
        if self.disposition not in REVIEW_DISPOSITIONS:
            raise ValueError("review disposition is not registered")
        if self.packet_review_state not in (
            "OPERATOR_CONFIRMATION_REQUIRED",
            "OPERATOR_REVIEW_REQUIRED",
        ):
            raise ValueError("packet review state is not registered")
        findings = tuple(self.finding_codes)
        if not findings or findings != tuple(
            item for item in FINDING_ORDER if item in findings
        ):
            raise ValueError("receipt findings must use closed packet order")
        if len(set(findings)) != len(findings):
            raise ValueError("receipt findings must be unique")
        fact_hashes = tuple(
            digest(item, "field_fact_hash") for item in self.field_fact_hashes
        )
        if not fact_hashes or len(set(fact_hashes)) != len(fact_hashes):
            raise ValueError("receipt requires unique field fact hashes")
        if (
            self.operator_review_completed is not True
            or self.evidence_validated is not False
            or self.evidence_rejected is not False
            or self.severity_assigned is not False
            or self.recommendation_generated is not False
            or self.threshold_set is not False
            or self.source_ranked is not False
            or self.source_selected is not False
            or self.evidence_replaced is not False
            or self.gap_closed is not False
        ):
            raise ValueError("review receipt cannot validate, decide, select, or close")
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(self, "field_fact_hashes", fact_hashes)
        object.__setattr__(
            self,
            "receipt_hash",
            canonical_sha256(
                {
                    "disposition": self.disposition,
                    "field_fact_hashes": list(fact_hashes),
                    "finding_codes": list(findings),
                    "ledger_hash": self.ledger_hash,
                    "packet_hash": self.packet_hash,
                    "packet_review_state": self.packet_review_state,
                    "review_id": self.review_id,
                    "reviewed_at_utc": self.reviewed_at_utc,
                    "reviewer_reference": self.reviewer_reference,
                }
            ),
        )
