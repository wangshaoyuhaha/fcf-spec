import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_handoff import build_paper_deployment_handoff_pack
from btc_finance_platform.paper_deployment_handoff import summarize_paper_deployment_handoff


def closeout():
    return {
        "p10_completed": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def summary():
    return {
        "next_stage_allowed": True,
        "paper_only": True,
        "operator_review_required": True,
        "operator_approved": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def test_handoff_ready_when_p10_closeout_and_operator_approved():
    result = build_paper_deployment_handoff_pack("paper-btc-model-v1", closeout(), summary())
    assert result["handoff_status"] == "ready"
    assert result["paper_deployment_handoff_ready"] is True
    assert result["real_world_actions_allowed"] is False


def test_handoff_blocks_without_operator_approval():
    bad_summary = summary()
    bad_summary["operator_approved"] = False
    result = build_paper_deployment_handoff_pack("paper-btc-model-v1", closeout(), bad_summary)
    assert result["handoff_status"] == "blocked"
    assert "check_failed:operator_approved" in result["blocked_reasons"]


def test_handoff_blocks_real_deployment_flag():
    bad_summary = summary()
    bad_summary["deployment_allowed_now"] = True
    result = build_paper_deployment_handoff_pack("paper-btc-model-v1", closeout(), bad_summary)
    assert result["handoff_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["deployment_allowed_now"] is False


def test_handoff_summary_keeps_paper_only_boundary():
    pack = build_paper_deployment_handoff_pack("paper-btc-model-v1", closeout(), summary())
    result = summarize_paper_deployment_handoff(pack)
    assert result["status"] == "ready"
    assert result["paper_only"] is True
    assert result["real_world_actions_allowed"] is False
    assert result["operator_review_required"] is True


def test_invalid_handoff_inputs_are_rejected():
    with pytest.raises(ValueError, match="model_id must be a non-empty string"):
        build_paper_deployment_handoff_pack("", closeout(), summary())
    with pytest.raises(ValueError, match="registry_closeout must be a dict"):
        build_paper_deployment_handoff_pack("paper-btc-model-v1", None, summary())
