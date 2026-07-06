"""D3 evidence matrix schema for SIGNAL-VALIDATION-APP-1.

The evidence matrix describes whether a paper-only candidate has coherent
support across existing sidecar layers. It is a review artifact only.
It must not become a trade instruction, order ticket, position sizing rule,
portfolio action, performance claim, or future return prediction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


ALLOWED_EVIDENCE_STATES: List[str] = [
    "NOT_EVALUATED",
    "SUPPORTED",
    "PARTIAL",
    "CONFLICT",
    "MISSING",
    "BLOCKED",
    "REVIEW_REQUIRED",
]

ALLOWED_EVIDENCE_LAYERS: List[str] = [
    "DATA-APP-1",
    "STOCK-APP-1",
    "AI-CONTEXT-1",
    "OPERATOR-REVIEW-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "DATA-QUALITY-OPS-APP-1",
    "MARKET-SCENARIO-APP-1",
    "BACKTEST-REVIEW-APP-1",
]

REQUIRED_MATRIX_FIELDS: List[str] = [
    "matrix_id",
    "candidate_id",
    "evidence_rows",
    "overall_validation_status",
    "operator_review_required",
    "trade_action_enabled",
    "real_execution_allowed",
]

FORBIDDEN_MATRIX_FIELDS: List[str] = [
    "buy_instruction",
    "sell_instruction",
    "order_instruction",
    "position_size",
    "portfolio_action",
    "future_return_prediction",
    "guaranteed_performance_claim",
    "broker_order_payload",
    "exchange_order_payload",
]


@dataclass(frozen=True)
class EvidenceRow:
    """One paper-only evidence row for one source layer."""

    layer_id: str
    evidence_state: str
    source_id: str
    source_status: str
    summary: str = ""
    reason_codes: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    operator_review_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable row representation."""

        return {
            "layer_id": self.layer_id,
            "evidence_state": self.evidence_state,
            "source_id": self.source_id,
            "source_status": self.source_status,
            "summary": self.summary,
            "reason_codes": list(self.reason_codes),
            "risk_flags": list(self.risk_flags),
            "conflicts": list(self.conflicts),
            "limitations": list(self.limitations),
            "operator_review_required": self.operator_review_required,
            "trade_action_enabled": False,
            "real_execution_allowed": False,
        }


@dataclass(frozen=True)
class EvidenceMatrix:
    """Paper-only evidence matrix for one candidate or review target."""

    matrix_id: str
    candidate_id: str
    evidence_rows: List[EvidenceRow]
    overall_validation_status: str = "NOT_EVALUATED"
    matrix_version: str = "1.0.0"
    operator_review_required: bool = True
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable matrix representation with closed boundaries."""

        return {
            "matrix_id": self.matrix_id,
            "candidate_id": self.candidate_id,
            "matrix_version": self.matrix_version,
            "evidence_rows": [row.to_dict() for row in self.evidence_rows],
            "overall_validation_status": self.overall_validation_status,
            "operator_review_required": self.operator_review_required,
            "operator_review_bypass_allowed": False,
            "notes": list(self.notes),
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "trade_action_enabled": False,
            "buy_button_enabled": False,
            "sell_button_enabled": False,
            "order_button_enabled": False,
            "real_execution_allowed": False,
            "broker_connection_allowed": False,
            "exchange_connection_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
            "p1_p47_core_mutation_allowed": False,
            "p48_core_expansion_allowed": False,
            "source_content_mutation_allowed": False,
            "source_deletion_allowed": False,
            "source_overwrite_allowed": False,
        }


def build_evidence_row(
    *,
    layer_id: str,
    evidence_state: str,
    source_id: str,
    source_status: str,
    summary: str = "",
    reason_codes: Optional[List[str]] = None,
    risk_flags: Optional[List[str]] = None,
    conflicts: Optional[List[str]] = None,
    limitations: Optional[List[str]] = None,
) -> EvidenceRow:
    """Build one validated evidence row."""

    if layer_id not in ALLOWED_EVIDENCE_LAYERS:
        raise ValueError(f"Unsupported evidence layer: {layer_id}")

    if evidence_state not in ALLOWED_EVIDENCE_STATES:
        raise ValueError(f"Unsupported evidence state: {evidence_state}")

    return EvidenceRow(
        layer_id=layer_id,
        evidence_state=evidence_state,
        source_id=source_id,
        source_status=source_status,
        summary=summary,
        reason_codes=list(reason_codes or []),
        risk_flags=list(risk_flags or []),
        conflicts=list(conflicts or []),
        limitations=list(limitations or []),
        operator_review_required=True,
    )


def infer_overall_validation_status(rows: List[EvidenceRow]) -> str:
    """Infer a paper-only validation status from evidence rows."""

    if not rows:
        return "REVIEW_REQUIRED"

    states = {row.evidence_state for row in rows}

    if "BLOCKED" in states:
        return "VALIDATION_BLOCKED"
    if "CONFLICT" in states:
        return "CONFLICT_DETECTED"
    if "MISSING" in states:
        return "EVIDENCE_PARTIAL"
    if "PARTIAL" in states:
        return "EVIDENCE_PARTIAL"
    if states == {"SUPPORTED"}:
        return "EVIDENCE_COMPLETE"

    return "REVIEW_REQUIRED"


def build_evidence_matrix(
    *,
    matrix_id: str,
    candidate_id: str,
    evidence_rows: List[EvidenceRow],
    notes: Optional[List[str]] = None,
) -> EvidenceMatrix:
    """Build a paper-only evidence matrix."""

    return EvidenceMatrix(
        matrix_id=matrix_id,
        candidate_id=candidate_id,
        evidence_rows=list(evidence_rows),
        overall_validation_status=infer_overall_validation_status(evidence_rows),
        operator_review_required=True,
        notes=list(notes or []),
    )


def validate_evidence_matrix_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a serialized evidence matrix payload at schema level."""

    missing_fields = [field_name for field_name in REQUIRED_MATRIX_FIELDS if field_name not in payload]
    forbidden_present = [field_name for field_name in FORBIDDEN_MATRIX_FIELDS if field_name in payload]

    rows = payload.get("evidence_rows", [])
    row_states = [
        row.get("evidence_state", "NOT_EVALUATED")
        for row in rows
        if isinstance(row, Mapping)
    ]
    unsupported_states = [
        state for state in row_states if state not in ALLOWED_EVIDENCE_STATES
    ]

    return {
        "schema_id": "SIGNAL-VALIDATION-D3-EVIDENCE-MATRIX",
        "is_valid": not missing_fields and not forbidden_present and not unsupported_states,
        "missing_fields": missing_fields,
        "forbidden_fields_present": forbidden_present,
        "unsupported_states": unsupported_states,
        "operator_review_required": True,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
    }
