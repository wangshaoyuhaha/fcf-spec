from pathlib import Path

from scripts.run_multi_asset_guarded_paper_execution_response_smoke import (
    run_smoke as run_response_smoke,
)
from scripts.run_multi_asset_guarded_paper_execution_smoke import (
    run_smoke as run_execution_smoke,
)


ACCEPTANCE_DOC = Path("docs/65_p7_guarded_paper_execution_acceptance.md")


def test_p7_guarded_paper_execution_acceptance_doc_exists():
    assert ACCEPTANCE_DOC.exists()


def test_p7_guarded_paper_execution_acceptance_doc_mentions_core_artifacts():
    text = ACCEPTANCE_DOC.read_text(encoding="utf-8")

    assert "fixtures/paper_orders_multi_asset_guarded.json" in text
    assert "scripts/run_multi_asset_guarded_paper_execution_smoke.py" in text
    assert "scripts/run_multi_asset_guarded_paper_execution_response_smoke.py" in text
    assert "evaluate_paper_execution_policy" in text
    assert "evaluate_paper_execution_risk" in text
    assert "execute_sandbox_order_with_eventstore" in text


def test_p7_guarded_paper_execution_acceptance_doc_mentions_assets_and_branches():
    text = ACCEPTANCE_DOC.read_text(encoding="utf-8")

    for asset_class in ["crypto", "equities", "fx", "commodities"]:
        assert asset_class in text

    for branch in ["fill_success", "sandbox_reject", "policy_deny", "risk_deny"]:
        assert branch in text


def test_p7_guarded_paper_execution_acceptance_execution_smoke_still_completes():
    result = run_execution_smoke()

    assert result["status"] == "completed"
    assert result["case_count"] == 16
    assert result["passed_count"] == 16
    assert result["failed_count"] == 0
    assert result["asset_class_counts"] == {
        "commodities": 4,
        "crypto": 4,
        "equities": 4,
        "fx": 4,
    }
    assert result["branch_counts"] == {
        "fill_success": 4,
        "policy_deny": 4,
        "risk_deny": 4,
        "sandbox_reject": 4,
    }


def test_p7_guarded_paper_execution_acceptance_response_smoke_still_completes():
    result = run_response_smoke()

    assert result["status"] == "completed"
    assert result["case_count"] == 16
    assert result["passed_count"] == 16
    assert result["failed_count"] == 0
    assert result["response_type_counts"] == {
        "paper_fill_success": 4,
        "paper_policy_deny": 4,
        "paper_reject_success": 4,
        "paper_risk_deny": 4,
    }


def test_p7_guarded_paper_execution_acceptance_doc_keeps_safety_boundaries():
    text = ACCEPTANCE_DOC.read_text(encoding="utf-8")

    assert "不接真实交易所 API" in text
    assert "不保存真实 API key" in text
    assert "不读取钱包私钥" in text
    assert "不真实下单" in text
    assert "不允许绕过 policy / risk" in text
    assert "sandbox fill 不是真实成交" in text
    assert "sandbox reject 不是交易所真实拒单" in text
    assert "PolicyDeny 不是交易所真实拒单" in text
    assert "RiskDeny 不是交易所真实拒单" in text
