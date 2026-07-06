"""D4 conflict and inconsistency detection for SIGNAL-VALIDATION-APP-1.

This module detects paper-only evidence conflicts across local sidecar outputs.
It must not create trade instructions, order tickets, position sizing rules,
portfolio actions, future return predictions, or guaranteed performance claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping

from .evidence_matrix import EvidenceMatrix, EvidenceRow


CONFLICT_SEVERITY_VALUES: List[str] = [
    "INFO",
    "LOW",
    "MEDIUM",
    "HIGH",
    "BLOCKING",
]

CONFLICT_TYPE_VALUES: List[str] = [
    "HIGH_SCORE_WITH_DATA_QUALITY_ISSUE",
    "POSITIVE_EXPLANATION_WITH_RISK_FLAG",
    "SCENARIO_BACKTEST_MISMATCH",
    "OPERATOR_REVIEW_MISSING",
    "SOURCE_MISSING_OR_PARTIAL",
    "ARCHIVE_INTEGRITY_GAP",
    "UNKNOWN_CONFLICT",
]


@dataclass(frozen=True)
class SignalConflict:
    """One paper-only signal validation conflict."""

    conflict_id: str
    conflict_type: str
    severity: str
    involved_layers: List[str]
    summary: str
    evidence_refs: List[str] = field(default_factory=list)
    operator_review_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable conflict representation."""

        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type,
            "severity": self.severity,
            "involved_layers": list(self.involved_layers),
            "summary": self.summary,
            "evidence_refs": list(self.evidence_refs),
            "operator_review_required": self.operator_review_required,
            "trade_action_enabled": False,
            "real_execution_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
        }


def _row_has_any(row: EvidenceRow, tokens: Iterable[str]) -> bool:
    haystack = {
        *[value.upper() for value in row.reason_codes],
        *[value.upper() for value in row.risk_flags],
        *[value.upper() for value in row.conflicts],
        row.evidence_state.upper(),
        row.source_status.upper(),
        row.summary.upper(),
    }
    return any(token.upper() in haystack for token in tokens)


def _find_rows(rows: List[EvidenceRow], layer_id: str) -> List[EvidenceRow]:
    return [row for row in rows if row.layer_id == layer_id]


def detect_signal_conflicts(matrix: EvidenceMatrix) -> Dict[str, Any]:
    """Detect paper-only conflicts in an evidence matrix."""

    rows = list(matrix.evidence_rows)
    conflicts: List[SignalConflict] = []

    data_quality_rows = _find_rows(rows, "DATA-QUALITY-OPS-APP-1")
    stock_rows = _find_rows(rows, "STOCK-APP-1")
    ai_rows = _find_rows(rows, "AI-CONTEXT-1")
    scenario_rows = _find_rows(rows, "MARKET-SCENARIO-APP-1")
    backtest_rows = _find_rows(rows, "BACKTEST-REVIEW-APP-1")
    operator_rows = _find_rows(rows, "OPERATOR-REVIEW-APP-1")
    archive_rows = _find_rows(rows, "REPORT-ARCHIVE-APP-1")

    if any(row.evidence_state == "SUPPORTED" for row in stock_rows) and any(
        row.evidence_state in {"CONFLICT", "BLOCKED"} or row.risk_flags for row in data_quality_rows
    ):
        conflicts.append(
            SignalConflict(
                conflict_id=f"{matrix.matrix_id}:data-quality-vs-stock",
                conflict_type="HIGH_SCORE_WITH_DATA_QUALITY_ISSUE",
                severity="HIGH",
                involved_layers=["STOCK-APP-1", "DATA-QUALITY-OPS-APP-1"],
                summary="Stock evidence is supported while data quality evidence has risk or blocking signals.",
                evidence_refs=["ranked_watchlist", "data_quality_issue_list"],
            )
        )

    if any(row.evidence_state == "SUPPORTED" for row in ai_rows) and any(
        row.risk_flags or row.evidence_state == "CONFLICT" for row in rows
    ):
        conflicts.append(
            SignalConflict(
                conflict_id=f"{matrix.matrix_id}:ai-positive-vs-risk",
                conflict_type="POSITIVE_EXPLANATION_WITH_RISK_FLAG",
                severity="MEDIUM",
                involved_layers=["AI-CONTEXT-1"],
                summary="AI explanation support exists while one or more risk flags or conflicts remain.",
                evidence_refs=["explanation_report", "risk_flags"],
            )
        )

    if scenario_rows and backtest_rows:
        scenario_supported = any(row.evidence_state == "SUPPORTED" for row in scenario_rows)
        backtest_blocked_or_conflict = any(
            row.evidence_state in {"CONFLICT", "BLOCKED", "PARTIAL", "MISSING"}
            for row in backtest_rows
        )
        if scenario_supported and backtest_blocked_or_conflict:
            conflicts.append(
                SignalConflict(
                    conflict_id=f"{matrix.matrix_id}:scenario-vs-backtest",
                    conflict_type="SCENARIO_BACKTEST_MISMATCH",
                    severity="HIGH",
                    involved_layers=["MARKET-SCENARIO-APP-1", "BACKTEST-REVIEW-APP-1"],
                    summary="Scenario evidence is supportive while backtest review evidence is partial, missing, blocked, or conflicting.",
                    evidence_refs=["market_scenario_review_packet", "backtest_review_packet"],
                )
            )

    if not operator_rows or any(row.evidence_state in {"MISSING", "BLOCKED"} for row in operator_rows):
        conflicts.append(
            SignalConflict(
                conflict_id=f"{matrix.matrix_id}:operator-review-missing",
                conflict_type="OPERATOR_REVIEW_MISSING",
                severity="BLOCKING",
                involved_layers=["OPERATOR-REVIEW-APP-1"],
                summary="Operator review evidence is missing or blocked; validation cannot bypass human review.",
                evidence_refs=["operator_review_record"],
            )
        )

    if any(row.evidence_state in {"MISSING", "PARTIAL", "BLOCKED"} for row in rows):
        conflicts.append(
            SignalConflict(
                conflict_id=f"{matrix.matrix_id}:source-partial",
                conflict_type="SOURCE_MISSING_OR_PARTIAL",
                severity="MEDIUM",
                involved_layers=sorted({row.layer_id for row in rows if row.evidence_state in {"MISSING", "PARTIAL", "BLOCKED"}}),
                summary="One or more source layers are missing, partial, or blocked.",
                evidence_refs=[row.source_id for row in rows if row.evidence_state in {"MISSING", "PARTIAL", "BLOCKED"}],
            )
        )

    if any(_row_has_any(row, ["CHECKSUM_MISSING", "ARCHIVE_GAP", "INTEGRITY_GAP"]) for row in archive_rows):
        conflicts.append(
            SignalConflict(
                conflict_id=f"{matrix.matrix_id}:archive-integrity-gap",
                conflict_type="ARCHIVE_INTEGRITY_GAP",
                severity="MEDIUM",
                involved_layers=["REPORT-ARCHIVE-APP-1"],
                summary="Archive evidence indicates an integrity or checksum coverage gap.",
                evidence_refs=["report_archive_manifest"],
            )
        )

    blocking_count = sum(1 for conflict in conflicts if conflict.severity == "BLOCKING")
    high_count = sum(1 for conflict in conflicts if conflict.severity == "HIGH")

    if blocking_count:
        detection_status = "VALIDATION_BLOCKED"
    elif high_count:
        detection_status = "CONFLICT_DETECTED"
    elif conflicts:
        detection_status = "REVIEW_REQUIRED"
    else:
        detection_status = "NO_CONFLICT_DETECTED"

    return {
        "app_id": "SIGNAL-VALIDATION-APP-1",
        "stage_id": "SIGNAL-VALIDATION-D4",
        "matrix_id": matrix.matrix_id,
        "candidate_id": matrix.candidate_id,
        "detection_status": detection_status,
        "conflict_count": len(conflicts),
        "blocking_conflict_count": blocking_count,
        "high_conflict_count": high_count,
        "conflicts": [conflict.to_dict() for conflict in conflicts],
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
    }


def summarize_conflict_detection(report: Mapping[str, Any]) -> Dict[str, Any]:
    """Return compact D4 conflict detection summary."""

    return {
        "app_id": report["app_id"],
        "stage_id": report["stage_id"],
        "matrix_id": report["matrix_id"],
        "candidate_id": report["candidate_id"],
        "detection_status": report["detection_status"],
        "conflict_count": report["conflict_count"],
        "blocking_conflict_count": report["blocking_conflict_count"],
        "high_conflict_count": report["high_conflict_count"],
        "operator_review_required": True,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
    }
