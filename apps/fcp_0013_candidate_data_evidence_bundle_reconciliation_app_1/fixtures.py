from pathlib import Path

from .loader import load_candidate_evidence_bundle
from .reconciliation import reconcile_candidate_evidence_bundle


def load_rqdata_candidate_bundle_review(root: Path):
    bundle = load_candidate_evidence_bundle(root)
    return bundle, reconcile_candidate_evidence_bundle(bundle)
