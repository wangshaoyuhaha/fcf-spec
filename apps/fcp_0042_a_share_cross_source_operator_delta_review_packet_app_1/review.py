from __future__ import annotations

from apps.fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1 import (
    CrossSourceRowDeltaEvidenceLedger,
)
from apps.fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1.contracts import (
    LEDGER_FIELDS,
)

from .contracts import (
    CrossSourceOperatorDeltaReviewPacket,
    FieldReviewFact,
    expected_findings,
)


def build_cross_source_operator_delta_review_packet(
    ledger: CrossSourceRowDeltaEvidenceLedger,
) -> CrossSourceOperatorDeltaReviewPacket:
    if not isinstance(ledger, CrossSourceRowDeltaEvidenceLedger):
        raise TypeError("ledger must be typed FCP-0041 evidence")
    facts = tuple(
        FieldReviewFact(
            field_name=field_name,
            exact_match_count=sum(
                item.comparison_state == "EXACT_MATCH"
                for item in ledger.entries
                if item.field_name == field_name
            ),
            delta_count=sum(
                item.comparison_state == "DELTA_PRESENT"
                for item in ledger.entries
                if item.field_name == field_name
            ),
            incomplete_count=sum(
                item.comparison_state == "PAIR_INCOMPLETE"
                for item in ledger.entries
                if item.field_name == field_name
            ),
            affected_dates=tuple(
                sorted(
                    {
                        item.trade_date
                        for item in ledger.entries
                        if item.field_name == field_name
                        and item.comparison_state != "EXACT_MATCH"
                    }
                )
            ),
        )
        for field_name in LEDGER_FIELDS
    )
    findings = expected_findings(facts)
    return CrossSourceOperatorDeltaReviewPacket(
        ledger_hash=ledger.ledger_hash,
        diagnostic_hash=ledger.diagnostic_hash,
        coverage_result_hash=ledger.coverage_result_hash,
        artifact_independence_proof_hash=ledger.artifact_independence_proof_hash,
        qmt_role_hash=ledger.qmt_role_hash,
        independent_role_hash=ledger.independent_role_hash,
        overlap_key_count=ledger.overlap_key_count,
        field_facts=facts,
        finding_codes=findings,
        review_state=(
            "OPERATOR_CONFIRMATION_REQUIRED"
            if findings == (
                "ROW_DELTA_LEDGER_REVIEWED",
                "EXACT_CROSS_SOURCE_PARITY_OBSERVED",
            )
            else "OPERATOR_REVIEW_REQUIRED"
        ),
    )
