from __future__ import annotations


SAFETY = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "trade_action_allowed": False,
    "real_execution_allowed": False,
}

ROWS = (
    ("DATA-APP-1", "data_ingestion_and_quarantine", 10, ()),
    ("DATA-QUALITY-OPS-APP-1", "data_ingestion_and_quarantine", 20, ("DATA-APP-1",)),
    ("STOCK-APP-1", "context_and_interpretation", 30, ("DATA-APP-1",)),
    ("AI-CONTEXT-1", "context_and_interpretation", 40, ("STOCK-APP-1",)),
    ("UI-APP-1", "presentation_and_immutable_archive", 50, ("AI-CONTEXT-1",)),
    ("OPERATOR-REVIEW-APP-1", "governance_and_review_gate", 60, ("UI-APP-1",)),
    ("REPORT-ARCHIVE-APP-1", "presentation_and_immutable_archive", 70, ("OPERATOR-REVIEW-APP-1",)),
    ("DATA-QUALITY-OPS-APP-1", "data_ingestion_and_quarantine", 80, ("REPORT-ARCHIVE-APP-1",)),
    ("MARKET-SCENARIO-APP-1", "context_and_interpretation", 90, ("DATA-QUALITY-OPS-APP-1",)),
    ("BACKTEST-REVIEW-APP-1", "context_and_interpretation", 100, ("MARKET-SCENARIO-APP-1",)),
    ("SIGNAL-VALIDATION-APP-1", "context_and_interpretation", 110, ("BACKTEST-REVIEW-APP-1",)),
    ("MODEL-GOVERNANCE-APP-1", "governance_and_review_gate", 120, ("SIGNAL-VALIDATION-APP-1",)),
    ("WATCHLIST-LIFECYCLE-APP-1", "governance_and_review_gate", 130, ("MODEL-GOVERNANCE-APP-1",)),
    ("PORTFOLIO-REVIEW-APP-1", "governance_and_review_gate", 140, ("WATCHLIST-LIFECYCLE-APP-1",)),
    ("RISK-EXPOSURE-APP-1", "governance_and_review_gate", 150, ("PORTFOLIO-REVIEW-APP-1",)),
    ("DECISION-AUDIT-APP-1", "governance_and_review_gate", 160, ("RISK-EXPOSURE-APP-1",)),
    ("RESEARCH-WORKFLOW-APP-1", "governance_and_review_gate", 170, ("DECISION-AUDIT-APP-1",)),
    ("DASHBOARD-STATUS-APP-1", "presentation_and_immutable_archive", 180, ("RESEARCH-WORKFLOW-APP-1",)),
    ("FINAL-COMPLETION-REVIEW-APP-1", "governance_and_review_gate", 190, ("DASHBOARD-STATUS-APP-1",)),
    ("CONTROL-CENTER-MAINTENANCE-APP-1", "governance_and_review_gate", 200, ("FINAL-COMPLETION-REVIEW-APP-1",)),
    ("DIFY-UI-HANDOFF-APP-1", "presentation_and_immutable_archive", 210, ("CONTROL-CENTER-MAINTENANCE-APP-1",)),
    ("CORRELATION-ID-TRACEABILITY-APP-1", "governance_and_review_gate", 220, ("DIFY-UI-HANDOFF-APP-1",)),
)


def load_completed_sidecar_inventory() -> tuple[dict[str, object], ...]:
    result = []
    for sidecar_id, zone, phase_index, upstream in ROWS:
        row = dict(SAFETY)
        row.update({
            "sidecar_id": sidecar_id,
            "zone": zone,
            "phase_index": phase_index,
            "allowed_upstream_sidecars": upstream,
        })
        result.append(row)
    return tuple(result)


def load_zone_names() -> tuple[str, ...]:
    return tuple(sorted({str(row["zone"]) for row in load_completed_sidecar_inventory()}))
