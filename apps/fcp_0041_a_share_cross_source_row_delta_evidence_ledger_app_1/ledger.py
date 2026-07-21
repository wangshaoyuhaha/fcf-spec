from __future__ import annotations

from decimal import Decimal

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    instant,
)
from apps.fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_app_1 import (
    SameCalendarCrossSourceCoverageResult,
    SourceRoleDataset,
)
from apps.fcp_0040_a_share_same_calendar_cross_source_field_delta_diagnostic_app_1 import (
    SameCalendarCrossSourceFieldDeltaDiagnostic,
    build_same_calendar_cross_source_field_delta_diagnostic,
)

from .contracts import (
    CLOCK_FIELDS,
    LEDGER_FIELDS,
    NUMERIC_FIELDS,
    TEXT_FIELDS,
    CrossSourceRowDeltaEvidenceLedger,
    RowDeltaEvidenceEntry,
)


def _canonical_numeric(value: object | None) -> str | None:
    if value is None:
        return None
    return canonical_decimal(Decimal(value))


def _entry(
    instrument_id: str,
    trade_date: str,
    field_name: str,
    qmt_value: object | None,
    independent_value: object | None,
) -> RowDeltaEvidenceEntry:
    if field_name in NUMERIC_FIELDS:
        qmt = _canonical_numeric(qmt_value)
        independent = _canonical_numeric(independent_value)
        delta = (
            canonical_decimal(abs(Decimal(qmt) - Decimal(independent)))
            if qmt is not None and independent is not None
            else None
        )
        kind = "EXACT_DECIMAL"
    elif field_name in TEXT_FIELDS:
        qmt = str(qmt_value) if qmt_value is not None else None
        independent = str(independent_value) if independent_value is not None else None
        delta = None
        kind = "EXACT_TEXT"
    else:
        qmt = str(qmt_value) if qmt_value is not None else None
        independent = str(independent_value) if independent_value is not None else None
        if qmt is not None and independent is not None:
            delta = str(
                round(
                    abs(
                        (
                            instant(qmt, "clock")
                            - instant(independent, "clock")
                        ).total_seconds()
                    )
                )
            )
        else:
            delta = None
        kind = "ABS_SECONDS"
    state = (
        "PAIR_INCOMPLETE"
        if qmt is None or independent is None
        else "EXACT_MATCH"
        if qmt == independent
        else "DELTA_PRESENT"
    )
    return RowDeltaEvidenceEntry(
        instrument_id=instrument_id,
        trade_date=trade_date,
        field_name=field_name,
        delta_kind=kind,
        qmt_value=qmt,
        independent_value=independent,
        delta_value=delta,
        comparison_state=state,
    )


def build_cross_source_row_delta_evidence_ledger(
    qmt: SourceRoleDataset,
    independent: SourceRoleDataset,
    coverage: SameCalendarCrossSourceCoverageResult,
    diagnostic: SameCalendarCrossSourceFieldDeltaDiagnostic,
) -> CrossSourceRowDeltaEvidenceLedger:
    if not isinstance(diagnostic, SameCalendarCrossSourceFieldDeltaDiagnostic):
        raise TypeError("diagnostic must be a typed FCP-0040 result")
    recomputed = build_same_calendar_cross_source_field_delta_diagnostic(
        qmt,
        independent,
        coverage,
    )
    if diagnostic != recomputed:
        raise ValueError("ledger inputs disagree with FCP-0040 diagnostic evidence")
    qmt_rows = {
        (item.instrument_id, item.trade_date): item
        for item in qmt.dataset.observations
    }
    independent_rows = {
        (item.instrument_id, item.trade_date): item
        for item in independent.dataset.observations
    }
    overlap = tuple(sorted(set(qmt_rows) & set(independent_rows)))
    entries: list[RowDeltaEvidenceEntry] = []
    for instrument_id, trade_date in overlap:
        left = qmt_rows[(instrument_id, trade_date)]
        right = independent_rows[(instrument_id, trade_date)]
        for field_name in LEDGER_FIELDS:
            entries.append(
                _entry(
                    instrument_id,
                    trade_date,
                    field_name,
                    getattr(left, field_name),
                    getattr(right, field_name),
                )
            )
    evidence = tuple(entries)
    return CrossSourceRowDeltaEvidenceLedger(
        coverage_result_hash=coverage.result_hash,
        artifact_independence_proof_hash=coverage.artifact_independence.proof_hash,
        diagnostic_hash=diagnostic.diagnostic_hash,
        qmt_role_hash=qmt.role_hash,
        independent_role_hash=independent.role_hash,
        overlap_key_count=len(overlap),
        entries=evidence,
        mismatch_entry_count=sum(
            item.comparison_state == "DELTA_PRESENT" for item in evidence
        ),
        incomplete_entry_count=sum(
            item.comparison_state == "PAIR_INCOMPLETE" for item in evidence
        ),
    )
