import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_entry_audit import build_p32_entry_packet
from btc_finance_platform.paper_next_phase_entry_audit import build_p32_entry_readiness_gate
from btc_finance_platform.paper_next_phase_entry_audit import build_p32_entry_safety_audit


def test_p32_entry_packet_uses_837_baseline():
    packet = build_p32_entry_packet()
    assert packet["phase"] == "P32"
    assert packet["baseline_tests"] == 837
    assert packet["previous_phase"] == "P31"
    assert packet["operator_review_required"] is True


def test_p32_entry_safety_audit_blocks_release_and_deploy():
    audit = build_p32_entry_safety_audit()
    assert audit["passed"] is True
    assert audit["tag_allowed"] is False
    assert audit["release_allowed"] is False
    assert audit["deploy_allowed"] is False
    assert audit["real_money_impact_allowed"] is False


def test_p32_entry_readiness_gate_is_not_release_gate():
    gate = build_p32_entry_readiness_gate()
    assert gate["ready_for_p32_work"] is True
    assert gate["ready_for_release"] is False
    assert gate["ready_for_deploy"] is False
    assert gate["operator_review_required"] is True
