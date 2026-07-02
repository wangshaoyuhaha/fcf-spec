import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.safe_boundary import assert_safe_boundary, get_safe_boundary
from btc_finance_platform.runtime import run_paper_runtime_check


def test_safe_boundary_assertion_passes():
    assert assert_safe_boundary() is True


def test_safe_boundary_blocks_real_behavior_flags():
    boundary = get_safe_boundary()

    assert boundary["paper_only"] is True
    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["operator_review_required"] is True
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False


def test_paper_runtime_check_returns_ok():
    result = run_paper_runtime_check()

    assert result["ok"] is True
    assert result["project"] == "btc_finance_platform"
    assert result["mode"] == "paper"
    assert result["safe_boundary"]["paper_only"] is True
