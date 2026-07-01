from pathlib import Path

from scripts.run_p9_acceptance_smoke import run_smoke


CLOSEOUT_DOC = Path("docs/87_p9_closeout_project_state.md")


def test_p9_closeout_doc_exists():
    assert CLOSEOUT_DOC.exists()


def test_p9_closeout_doc_mentions_phase9_days():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for day in ["P9-D1", "P9-D2", "P9-D3", "P9-D4", "P9-D5", "P9-D6", "P9-D7", "P9-D8"]:
        assert day in text


def test_p9_closeout_doc_mentions_key_artifacts():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for artifact in [
        "scripts/run_all_smokes.py",
        "scripts/run_p9_acceptance_smoke.py",
        "fcf/regression/global_regression_report_schema.py",
        "fcf/regression/global_safe_boundary_checker.py",
        "fcf/regression/project_state_consistency_checker.py",
        "docs/85_p9_ci_safe_regression_command_document.md",
    ]:
        assert artifact in text


def test_p9_closeout_doc_mentions_global_capabilities():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for item in [
        "统一 smoke / regression 入口",
        "P7 regression summary 汇总",
        "P8 portfolio regression summary 汇总",
        "machine-readable global regression report",
        "global safe_boundary checker",
        "PROJECT_STATE / README consistency checker",
        "CI-safe regression command document",
        "Phase 9 acceptance smoke",
    ]:
        assert item in text


def test_p9_closeout_acceptance_smoke_still_completed():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert result["status"] == "completed"
    assert summary["phase"] == "P9"
    assert summary["ready_for_p9_d8_closeout"] is True
    assert summary["run_all_smokes_completed"] is True
    assert summary["global_report_completed"] is True
    assert summary["global_safe_boundary_ok"] is True
    assert summary["project_state_consistency_ok"] is True


def test_p9_closeout_doc_mentions_ci_safe_commands():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    assert "python main.py" in text
    assert "python scripts/run_all_smokes.py" in text
    assert "python scripts/run_p9_acceptance_smoke.py" in text
    assert "python -m pytest -q" in text
    assert "CI 推荐回归命令" in text


def test_p9_closeout_doc_keeps_safety_boundaries():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

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
        "不把 paper execution 伪装成 real execution",
    ]:
        assert item in text
