from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1.contracts import (
    CLOCK_FIELDS,
    LEDGER_FIELDS,
    NUMERIC_FIELDS,
    TEXT_FIELDS,
)


FINDING_ORDER = (
    "ROW_DELTA_LEDGER_REVIEWED",
    "EXACT_CROSS_SOURCE_PARITY_OBSERVED",
    "NUMERIC_DELTAS_PRESENT",
    "TEXT_DELTAS_PRESENT",
    "CLOCK_DELTAS_PRESENT",
    "INCOMPLETE_PAIRS_PRESENT",
)


@dataclass(frozen=True)
class FieldReviewFact:
    field_name: str
    exact_match_count: int
    delta_count: int
    incomplete_count: int
    affected_dates: tuple[str, ...]
    fact_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.field_name not in LEDGER_FIELDS:
            raise ValueError("review field is not registered")
        counts = (
            self.exact_match_count,
            self.delta_count,
            self.incomplete_count,
        )
        if any(
            isinstance(item, bool) or not isinstance(item, int) or item < 0
            for item in counts
        ):
            raise ValueError("review fact counts must be nonnegative integers")
        dates = tuple(self.affected_dates)
        if dates != tuple(sorted(set(dates))):
            raise ValueError("affected dates must be ordered and unique")
        try:
            for value in dates:
                date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("affected dates must be ISO dates") from exc
        if len(dates) > self.delta_count + self.incomplete_count:
            raise ValueError("affected dates exceed nonmatching evidence")
        if bool(dates) != bool(self.delta_count + self.incomplete_count):
            raise ValueError("affected dates disagree with nonmatching evidence")
        object.__setattr__(self, "affected_dates", dates)
        object.__setattr__(
            self,
            "fact_hash",
            canonical_sha256(
                {
                    "affected_dates": list(dates),
                    "delta_count": self.delta_count,
                    "exact_match_count": self.exact_match_count,
                    "field_name": self.field_name,
                    "incomplete_count": self.incomplete_count,
                }
            ),
        )


def expected_findings(facts: tuple[FieldReviewFact, ...]) -> tuple[str, ...]:
    result = ["ROW_DELTA_LEDGER_REVIEWED"]
    delta_fields = {item.field_name for item in facts if item.delta_count}
    incomplete = any(item.incomplete_count for item in facts)
    if not delta_fields and not incomplete:
        result.append("EXACT_CROSS_SOURCE_PARITY_OBSERVED")
    if delta_fields & set(NUMERIC_FIELDS):
        result.append("NUMERIC_DELTAS_PRESENT")
    if delta_fields & set(TEXT_FIELDS):
        result.append("TEXT_DELTAS_PRESENT")
    if delta_fields & set(CLOCK_FIELDS):
        result.append("CLOCK_DELTAS_PRESENT")
    if incomplete:
        result.append("INCOMPLETE_PAIRS_PRESENT")
    return tuple(item for item in FINDING_ORDER if item in result)


@dataclass(frozen=True)
class CrossSourceOperatorDeltaReviewPacket:
    ledger_hash: str
    diagnostic_hash: str
    coverage_result_hash: str
    artifact_independence_proof_hash: str
    qmt_role_hash: str
    independent_role_hash: str
    overlap_key_count: int
    field_facts: tuple[FieldReviewFact, ...]
    finding_codes: tuple[str, ...]
    review_state: str
    operator_review_required: bool = True
    severity_assigned: bool = False
    recommendation_generated: bool = False
    threshold_set: bool = False
    source_ranked: bool = False
    source_selected: bool = False
    evidence_replaced: bool = False
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "ledger_hash",
            "diagnostic_hash",
            "coverage_result_hash",
            "artifact_independence_proof_hash",
            "qmt_role_hash",
            "independent_role_hash",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if self.qmt_role_hash == self.independent_role_hash:
            raise ValueError("review packet role hashes must be distinct")
        if (
            isinstance(self.overlap_key_count, bool)
            or not isinstance(self.overlap_key_count, int)
            or self.overlap_key_count <= 0
        ):
            raise ValueError("review packet requires positive overlap")
        facts = tuple(self.field_facts)
        if tuple(item.field_name for item in facts) != LEDGER_FIELDS:
            raise ValueError("review facts must use the closed field order")
        if any(
            item.exact_match_count + item.delta_count + item.incomplete_count
            != self.overlap_key_count
            for item in facts
        ):
            raise ValueError("review fact counts disagree with overlap")
        findings = expected_findings(facts)
        if tuple(self.finding_codes) != findings:
            raise ValueError("review finding codes disagree with facts")
        expected_state = (
            "OPERATOR_CONFIRMATION_REQUIRED"
            if findings == (
                "ROW_DELTA_LEDGER_REVIEWED",
                "EXACT_CROSS_SOURCE_PARITY_OBSERVED",
            )
            else "OPERATOR_REVIEW_REQUIRED"
        )
        if self.review_state != expected_state:
            raise ValueError("review state disagrees with facts")
        if (
            self.operator_review_required is not True
            or self.severity_assigned is not False
            or self.recommendation_generated is not False
            or self.threshold_set is not False
            or self.source_ranked is not False
            or self.source_selected is not False
            or self.evidence_replaced is not False
        ):
            raise ValueError("review packet cannot decide, recommend, or select")
        object.__setattr__(self, "field_facts", facts)
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(
            self,
            "packet_hash",
            canonical_sha256(
                {
                    "artifact_independence_proof_hash": self.artifact_independence_proof_hash,
                    "coverage_result_hash": self.coverage_result_hash,
                    "diagnostic_hash": self.diagnostic_hash,
                    "fact_hashes": [item.fact_hash for item in facts],
                    "finding_codes": list(findings),
                    "independent_role_hash": self.independent_role_hash,
                    "ledger_hash": self.ledger_hash,
                    "overlap_key_count": self.overlap_key_count,
                    "qmt_role_hash": self.qmt_role_hash,
                    "review_state": self.review_state,
                }
            ),
        )
