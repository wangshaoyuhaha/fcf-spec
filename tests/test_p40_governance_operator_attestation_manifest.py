import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_operator_attestation_manifest import build_p40_governance_operator_attestation_manifest, build_p40_operator_attestation_checkpoint, build_p40_operator_attestation_manifest_gate

def test_p40_governance_operator_attestation_manifest_uses_936_baseline():
 result = build_p40_governance_operator_attestation_manifest()
 assert result["phase"] == "P40"
 assert result["step_range"] == "D4-D6"
 assert result["baseline_tests"] == 936
 assert result["operator_attestation_manifest_ready"] is True
 assert result["operator_review_required"] is True

def test_p40_operator_attestation_checkpoint_preserves_boundary():
 result = build_p40_operator_attestation_checkpoint()
 assert result["bridge_preserved"] is True
 assert result["attestation_boundary_preserved"] is True
 assert result["attestation_required"] is True
 assert result["real_world_actions_allowed"] is False

def test_p40_operator_attestation_manifest_gate_blocks_release_deploy():
 result = build_p40_operator_attestation_manifest_gate()
 assert result["ready_for_p40_d7_d9"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
