from pathlib import Path

from scripts.run_final_archive_acceptance_smoke import run_smoke as run_archive_smoke
from scripts.run_p12_final_delivery_package_summary import run_smoke as run_p12_summary


DOC = Path("docs/127_archive_d7_final_archive_closeout.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d7_final_archive_closeout_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "Archive-D7" in text
    assert "Final Archive Closeout" in text


def test_archive_d7_final_archive_closeout_mentions_theme_and_completed_days():
    text = _text()

    assert "Final archive readiness, immutable delivery snapshot, and operator archive handoff" in text
    assert "最终归档准备、不可变交付快照与 operator 归档交接" in text

    for day in [
        "Archive-D1",
        "Archive-D2",
        "Archive-D3",
        "Archive-D4",
        "Archive-D5",
        "Archive-D6",
        "Archive-D7",
    ]:
        assert day in text


def test_archive_d7_final_archive_closeout_mentions_final_files():
    text = _text()

    for item in [
        "docs/121_archive_d1_final_archive_plan.md",
        "docs/122_archive_d2_immutable_delivery_snapshot_checklist.md",
        "docs/123_archive_d3_final_release_note.md",
        "docs/124_archive_d4_final_archive_manifest.md",
        "docs/125_archive_d5_final_operator_archive_handoff.md",
        "docs/126_archive_d6_final_archive_acceptance_smoke.md",
        "docs/127_archive_d7_final_archive_closeout.md",
        "scripts/run_final_archive_acceptance_smoke.py",
    ]:
        assert item in text


def test_archive_d7_final_archive_closeout_mentions_final_commands_and_status():
    text = _text()

    for item in [
        "python main.py",
        "python scripts/run_p12_final_delivery_package_summary.py",
        "python scripts/run_final_archive_acceptance_smoke.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
        "ready_for_p12_d10_archive_bridge_plan true",
        "ready_for_archive_d7_closeout true",
        "pytest 全部 passed",
    ]:
        assert item in text


def test_archive_d7_final_archive_closeout_archive_smoke_still_completed():
    result = run_archive_smoke()
    summary = result["acceptance_summary"]

    assert result["status"] == "completed"
    assert result["runner"] == "final_archive_acceptance_smoke"
    assert summary["phase"] == "Final Archive"
    assert summary["p12_final_delivery_package_summary_completed"] is True
    assert summary["ready_for_p12_d10_archive_bridge_plan"] is True
    assert summary["archive_docs_all_present"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_archive_d7_closeout"] is True


def test_archive_d7_final_archive_closeout_p12_summary_still_completed():
    result = run_p12_summary()
    summary = result["package_summary"]

    assert result["status"] == "completed"
    assert summary["phase"] == "P12"
    assert summary["ready_for_p12_d10_archive_bridge_plan"] is True
    assert summary["p12_acceptance_completed"] is True
    assert summary["ready_for_p12_d8_closeout"] is True
    assert summary["p11_release_readiness_summary_completed"] is True
    assert summary["ready_for_p11_d10_bridge_plan"] is True
    assert summary["deliverables_all_present"] is True
    assert summary["safe_boundary_ok"] is True


def test_archive_d7_final_archive_closeout_mentions_capabilities_and_limits():
    text = _text()

    for item in [
        "paper-only local regression",
        "non-production validation",
        "Dify-safe operator review",
        "release readiness review",
        "archive readiness review",
        "immutable delivery snapshot review",
        "final operator archive handoff",
        "long-term audit readability",
        "final non-production delivery preservation",
        "真实交易",
        "真实下单",
        "真实成交声明",
        "真实账户余额读取",
        "真实仓位读取",
        "钱包私钥读取",
        "production deployment",
        "自动实盘交易",
        "绕过人工复核",
        "绕过 policy / risk / safe_boundary",
    ]:
        assert item in text


def test_archive_d7_final_archive_closeout_mentions_post_archive_rules_and_failed_rules():
    text = _text()

    for item in [
        "新建 commit",
        "重新运行 python main.py",
        "重新运行 python scripts/run_p12_final_delivery_package_summary.py",
        "重新运行 python scripts/run_final_archive_acceptance_smoke.py",
        "重新运行 python -m pytest -q",
        "重新更新 PROJECT_STATE.md",
        "重新更新 archive record",
        "重新 push",
        "回改历史 commit",
        "force push 覆盖已归档 commit",
        "删除测试",
        "删除安全边界",
        "删除 failed 停止规则",
        "立即停止",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "docs/94_p10_failure_triage_guide.md",
    ]:
        assert item in text


def test_archive_d7_final_archive_closeout_keeps_safety_boundaries_and_final_statement():
    text = _text()

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
        "不自动实盘交易",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
        "Final Archive 阶段完成",
        "paper-only safe_boundary preserved",
        "operator_review_required true",
        "bypass_operator_review false",
        "bypass_policy_risk_safe_boundary false",
        "这不是 production deployment",
        "这不是 live trading package",
        "这不是 exchange execution package",
        "这不是 wallet custody package",
        "这不是 real-money trading package",
        "所有 passed 只能说明 paper-only / non-production regression passed",
        "所有结果必须经过人工复核",
    ]:
        assert item in text
