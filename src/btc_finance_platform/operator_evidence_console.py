from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SAFETY_BOUNDARY = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "real_exchange_api": False,
    "real_brokerage_api": False,
    "api_keys_allowed": False,
    "wallet_private_keys_allowed": False,
    "real_orders_allowed": False,
    "real_execution_allowed": False,
    "real_balances_positions_allowed": False,
    "real_money_impact": False,
    "operator_review_required": True,
    "auto_deploy_allowed": False,
}


@dataclass(frozen=True)
class EvidenceSection:
    section_id: str
    title: str
    artifact: str
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "artifact": self.artifact,
            "read_only": self.read_only,
        }


def build_operator_evidence_console_manifest() -> dict[str, Any]:
    sections = [
        EvidenceSection("release_evidence", "Release Evidence Index", "docs/p15_release_evidence_index.md"),
        EvidenceSection("operator_review", "Operator Review History Index", "docs/p15_operator_review_history_index.md"),
        EvidenceSection("learning_memory", "Learning Memory Browser Plan", "docs/p15_learning_memory_browser_plan.md"),
        EvidenceSection("scenario_reports", "Scenario Report Browser Plan", "docs/p15_scenario_report_browser_plan.md"),
        EvidenceSection("patch_review", "Patch Proposal Review Queue", "docs/p15_patch_proposal_review_queue.md"),
        EvidenceSection("safety_regression", "Safety Boundary Regression Report", "docs/p15_safety_boundary_regression_report.md"),
        EvidenceSection("no_deploy_audit", "No-deploy Release Audit", "docs/p15_no_deploy_release_audit.md"),
    ]

    return {
        "type": "operator_evidence_console_manifest",
        "status": "READ_ONLY",
        "release_tag": "v14-learning-engine-paper",
        "release_commit": "5188158",
        "phase": "P16-D1-D3",
        "sections": [section.to_dict() for section in sections],
        "section_count": len(sections),
        "allowed_actions": ["view_evidence", "read_reports", "inspect_paper_summaries"],
        "forbidden_actions": ["trade", "deploy", "enter_api_key", "enter_wallet_private_key", "place_order"],
        "safety_boundary": dict(SAFETY_BOUNDARY),
    }


def summarize_operator_evidence_console(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    data = manifest or build_operator_evidence_console_manifest()
    return {
        "ok": True,
        "type": "operator_evidence_console_summary",
        "status": data["status"],
        "release_tag": data["release_tag"],
        "section_count": data["section_count"],
        "paper_only": data["safety_boundary"]["paper_only"],
        "read_only": data["safety_boundary"]["read_only"],
        "real_trading_enabled": False,
        "deploy_enabled": False,
        "operator_review_required": data["safety_boundary"]["operator_review_required"],
    }
