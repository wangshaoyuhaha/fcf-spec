from pathlib import Path

from fcf.regression.global_regression_report_schema import build_global_regression_report
from fcf.regression.global_safe_boundary_checker import check_global_safe_boundary
from fcf.regression.project_state_consistency_checker import check_project_state_consistency
from scripts.run_all_smokes import run_all_smokes


DOC = Path("docs/85_p9_ci_safe_regression_command_document.md")


def test_p9_ci_safe_regression_command_doc_exists():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P9-D6" in text
    assert "CI-safe regression command document" in text


def test_p9_ci_safe_regression_command_doc_mentions_local_and_ci_commands():
    text = DOC.read_text(encoding="utf-8")

    assert "python main.py" in text
    assert "python scripts/run_all_smokes.py" in text
    assert "python -m pytest -q" in text
    assert "本地完整回归建议运行" in text
    assert "CI 中推荐运行" in text


def test_p9_ci_safe_regression_command_doc_mentions_no_secret_requirements():
    text = DOC.read_text(encoding="utf-8")

    for item in [
        "exchange API key",
        "wallet private key",
        "real account credentials",
        "real broker credentials",
        "CI secret",
        "production deployment permission",
    ]:
        assert item in text


def test_p9_ci_safe_regression_command_doc_mentions_safety_boundary():
    text = DOC.read_text(encoding="utf-8")

    for item in [
        "不接真实交易所 API",
        "不保存真实 API key",
        "不读取钱包私钥",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不声明真实成交",
        "不声明真实资金影响",
        "不配置 CI secret",
        "不做 production deployment",
        "no_real_exchange_api",
        "no_real_order_placement",
        "no_exchange_api_key_storage",
        "no_wallet_private_key_access",
        "no_real_account_balance_read",
        "no_real_position_read",
        "does_not_claim_real_trade_success",
        "ci_secret_required",
        "production_deployment",
    ]:
        assert item in text


def test_p9_ci_safe_regression_command_doc_run_all_smokes_completed():
    result = run_all_smokes()

    assert result["status"] == "completed"
    assert result["counts"] == {
        "total_smoke_count": 2,
        "completed_count": 2,
        "failed_count": 0,
        "ready_count": 2,
    }
    assert result["readiness"]["global_regression_suite_ready"] is True


def test_p9_ci_safe_regression_command_doc_global_safe_boundary_still_passes():
    report = build_global_regression_report(run_all_smokes())
    result = check_global_safe_boundary(report)

    assert result["status"] == "completed"
    assert result["ok"] is True
    assert result["violations"] == []


def test_p9_ci_safe_regression_command_doc_project_state_consistency_still_passes():
    result = check_project_state_consistency()

    assert result["status"] == "completed"
    assert result["ok"] is True
    assert result["violations"] == []
    assert result["ready_for_p9_d6_ci_safe_command_doc"] is True
