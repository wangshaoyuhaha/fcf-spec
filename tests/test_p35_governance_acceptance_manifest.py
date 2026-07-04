import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_acceptance_manifest import build_p35_acceptance_checkpoint
from btc_finance_platform.paper_governance_acceptance_manifest import build_p35_acceptance_manifest_gate
from btc_finance_platform.paper_governance_acceptance_manifest import build_p35_governance_acceptance_manifest


def test_p35_governance_acceptance_manifest_uses_876_baseline():
 result = build_p35_governance_acceptance_manifest()
 assert result["phase"] == "P35"
 assert result["step_range"] == "D4-D6"
 assert result["baseline_tests"] == 876
 assert result["previous_step"] == "P35-D1-D3"
 assert result["acceptance_manifest_ready"] is True
 assert result["operator_review_required"] is True


def test_p35_acceptance_checkpoint_preserves_boundary():
 result = build_p35_acceptance_checkpoint()
 assert result["bridge_preserved"] is True
 assert result["operator_boundary_preserved"] is True
 assert result["real_world_actions_allowed"] is False
 assert result["operator_review_required"] is True


def test_p35_acceptance_manifest_gate_blocks_release_deploy():
 result = build_p35_acceptance_manifest_gate()
 assert result["ready_for_p35_d7_d9"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
 assert result["operator_review_required"] is True
