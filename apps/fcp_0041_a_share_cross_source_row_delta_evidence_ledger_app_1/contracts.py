from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    canonical_sha256,
    decimal_value,
    digest,
    instant,
)
from apps.fcp_0040_a_share_same_calendar_cross_source_field_delta_diagnostic_app_1.contracts import (
    CLOCK_FIELDS,
    NUMERIC_FIELDS,
)


TEXT_FIELDS = ("factor_version", "trading_status")
LEDGER_FIELDS = NUMERIC_FIELDS + TEXT_FIELDS + CLOCK_FIELDS
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE|XBSE)$")
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+\-]*$")


def _safe_value(value: object, name: str) -> str:
    result = str(value).strip()
    if _SAFE_VALUE.fullmatch(result) is None:
        raise ValueError(f"{name} is not a safe canonical value")
    return result


@dataclass(frozen=True)
class RowDeltaEvidenceEntry:
    instrument_id: str
    trade_date: str
    field_name: str
    delta_kind: str
    qmt_value: str | None
    independent_value: str | None
    delta_value: str | None
    comparison_state: str
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        try:
            date.fromisoformat(self.trade_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("trade_date must be an ISO date") from exc
        if self.field_name not in LEDGER_FIELDS:
            raise ValueError("ledger field is not registered")
        expected_kind = (
            "EXACT_DECIMAL"
            if self.field_name in NUMERIC_FIELDS
            else "EXACT_TEXT"
            if self.field_name in TEXT_FIELDS
            else "ABS_SECONDS"
        )
        if self.delta_kind != expected_kind:
            raise ValueError("delta kind disagrees with ledger field")
        qmt = self.qmt_value
        independent = self.independent_value
        delta = self.delta_value
        if self.field_name in NUMERIC_FIELDS:
            qmt = self._canonical_decimal(qmt, "qmt_value")
            independent = self._canonical_decimal(independent, "independent_value")
            expected_delta = (
                canonical_decimal(abs(Decimal(qmt) - Decimal(independent)))
                if qmt is not None and independent is not None
                else None
            )
        elif self.field_name in TEXT_FIELDS:
            qmt = _safe_value(qmt, "qmt_value") if qmt is not None else None
            independent = (
                _safe_value(independent, "independent_value")
                if independent is not None
                else None
            )
            expected_delta = None
        else:
            qmt = self._canonical_clock(qmt, "qmt_value")
            independent = self._canonical_clock(independent, "independent_value")
            expected_delta = (
                str(
                    round(
                        abs(
                            (
                                instant(qmt, "qmt_value")
                                - instant(independent, "independent_value")
                            ).total_seconds()
                        )
                    )
                )
                if qmt is not None and independent is not None
                else None
            )
        expected_state = (
            "PAIR_INCOMPLETE"
            if qmt is None or independent is None
            else "EXACT_MATCH"
            if qmt == independent
            else "DELTA_PRESENT"
        )
        if self.comparison_state != expected_state or delta != expected_delta:
            raise ValueError("ledger comparison evidence is inconsistent")
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "qmt_value", qmt)
        object.__setattr__(self, "independent_value", independent)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "comparison_state": self.comparison_state,
                    "delta_kind": self.delta_kind,
                    "delta_value": delta,
                    "field_name": self.field_name,
                    "independent_value": independent,
                    "instrument_id": instrument,
                    "qmt_value": qmt,
                    "trade_date": self.trade_date,
                }
            ),
        )

    @staticmethod
    def _canonical_decimal(value: str | None, name: str) -> str | None:
        if value is None:
            return None
        return canonical_decimal(decimal_value(value, name))

    @staticmethod
    def _canonical_clock(value: str | None, name: str) -> str | None:
        if value is None:
            return None
        return instant(value, name).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CrossSourceRowDeltaEvidenceLedger:
    coverage_result_hash: str
    artifact_independence_proof_hash: str
    diagnostic_hash: str
    qmt_role_hash: str
    independent_role_hash: str
    overlap_key_count: int
    entries: tuple[RowDeltaEvidenceEntry, ...]
    mismatch_entry_count: int
    incomplete_entry_count: int
    ledger_state: str = "READ_ONLY_REGISTERED_EVIDENCE_ONLY"
    operator_review_required: bool = True
    threshold_set: bool = False
    source_ranked: bool = False
    source_selected: bool = False
    evidence_replaced: bool = False
    ledger_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "coverage_result_hash",
            "artifact_independence_proof_hash",
            "diagnostic_hash",
            "qmt_role_hash",
            "independent_role_hash",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if self.qmt_role_hash == self.independent_role_hash:
            raise ValueError("ledger role hashes must be distinct")
        if (
            isinstance(self.overlap_key_count, bool)
            or not isinstance(self.overlap_key_count, int)
            or self.overlap_key_count <= 0
        ):
            raise ValueError("ledger requires positive overlap")
        entries = tuple(self.entries)
        expected_count = self.overlap_key_count * len(LEDGER_FIELDS)
        if len(entries) != expected_count:
            raise ValueError("ledger entry count disagrees with closed field coverage")
        keys = tuple(
            (item.instrument_id, item.trade_date, LEDGER_FIELDS.index(item.field_name))
            for item in entries
        )
        if keys != tuple(sorted(keys)) or len(set(keys)) != len(keys):
            raise ValueError("ledger entries must be ordered and unique")
        mismatch = sum(item.comparison_state == "DELTA_PRESENT" for item in entries)
        incomplete = sum(item.comparison_state == "PAIR_INCOMPLETE" for item in entries)
        if self.mismatch_entry_count != mismatch or self.incomplete_entry_count != incomplete:
            raise ValueError("ledger state counts disagree with entries")
        if self.ledger_state != "READ_ONLY_REGISTERED_EVIDENCE_ONLY":
            raise ValueError("ledger state is immutable")
        if (
            self.operator_review_required is not True
            or self.threshold_set is not False
            or self.source_ranked is not False
            or self.source_selected is not False
            or self.evidence_replaced is not False
        ):
            raise ValueError("ledger cannot decide, select, or replace evidence")
        object.__setattr__(self, "entries", entries)
        object.__setattr__(
            self,
            "ledger_hash",
            canonical_sha256(
                {
                    "artifact_independence_proof_hash": self.artifact_independence_proof_hash,
                    "coverage_result_hash": self.coverage_result_hash,
                    "diagnostic_hash": self.diagnostic_hash,
                    "entry_hashes": [item.entry_hash for item in entries],
                    "incomplete_entry_count": self.incomplete_entry_count,
                    "independent_role_hash": self.independent_role_hash,
                    "ledger_state": self.ledger_state,
                    "mismatch_entry_count": self.mismatch_entry_count,
                    "overlap_key_count": self.overlap_key_count,
                    "qmt_role_hash": self.qmt_role_hash,
                }
            ),
        )
