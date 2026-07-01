from pathlib import Path

from fcf.regression.global_regression_report_schema import build_global_regression_report
from fcf.regression.global_safe_boundary_checker import (
    REQUIRED_SAFE_BOUNDARY,
    check_global_safe_boundary,
)
from scripts.run_all_smokes import run_all_smokes


DOC = Path("docs/83_p9_global_safe_boundary_checker.md")


def _report():
    return build_global_regression_report(run_all_smokes())


def test_p9_global_safe_boundary_checker_doc_exists():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P9-D4" in text
    assert "global safe boundary checker" in text
    assert "check_global_safe_boundary" in text


def test_p9_global_safe_boundary_checker_valid_report_passes():
    result = check_global_safe_boundary(_report())

    assert result["status"] == "completed"
    assert result["checker"] == "global_safe_boundary_checker"
    assert result["checker_version"] == "0.1.0"
    assert result["ok"] is True
    assert result["violations"] == []
    assert result["ready_for_p9_d5_project_state_checker"] is True


def test_p9_global_safe_boundary_checker_required_keys_pass():
    result = check_global_safe_boundary(_report())

    assert set(result["checks"].keys()) == set(REQUIRED_SAFE_BOUNDARY.keys())

    for key, expected in REQUIRED_SAFE_BOUNDARY.items():
        assert result["checks"][key]["expected"] == expected
        assert result["checks"][key]["actual"] == expected
        assert result["checks"][key]["passed"] is True


def test_p9_global_safe_boundary_checker_accepts_direct_safe_boundary():
    report = _report()
    result = check_global_safe_boundary(report["safe_boundary"])

    assert result["status"] == "completed"
    assert result["ok"] is True
    assert result["violations"] == []


def test_p9_global_safe_boundary_checker_fails_missing_boundary():
    result = check_global_safe_boundary({})

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert result["ready_for_p9_d5_project_state_checker"] is False
    assert len(result["violations"]) == len(REQUIRED_SAFE_BOUNDARY)


def test_p9_global_safe_boundary_checker_fails_real_execution_true():
    report = _report()
    report["safe_boundary"]["real_execution"] = True

    result = check_global_safe_boundary(report)

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert {
        "key": "real_execution",
        "expected": False,
        "actual": True,
    } in result["violations"]


def test_p9_global_safe_boundary_checker_fails_no_real_exchange_api_false():
    report = _report()
    report["safe_boundary"]["no_real_exchange_api"] = False

    result = check_global_safe_boundary(report)

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert {
        "key": "no_real_exchange_api",
        "expected": True,
        "actual": False,
    } in result["violations"]


def test_p9_global_safe_boundary_checker_doc_mentions_all_safety_items():
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
    ]:
        assert item in text
