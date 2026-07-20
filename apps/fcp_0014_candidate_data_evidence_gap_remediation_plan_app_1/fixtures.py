from pathlib import Path

from apps.fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1 import (
    load_rqdata_candidate_bundle_review,
)

from .planner import build_candidate_evidence_gap_remediation_plan


def load_rqdata_candidate_remediation_plan(root: Path):
    bundle, packet = load_rqdata_candidate_bundle_review(root)
    return bundle, packet, build_candidate_evidence_gap_remediation_plan(packet)
