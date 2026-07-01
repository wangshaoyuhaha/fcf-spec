from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/123_archive_d3_final_release_note.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d3_final_release_note_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "Archive-D3" in text
    assert "Final Release Note" in text


def test_archive_d3_final_release_note_mentions_version_and_scope():
    text = _text()

    for item in [
        "final_release_note_version = 0.1.0",
        "release_mode = non_production",
        "archive_mode = immutable_non_production_snapshot",
        "paper_only = true",
        "phase = Final Archive",
        "day = Archive-D3",
        "status = active",
        "final archive readiness",
        "immutable delivery snapshot record",
        "final operator archive handoff",
        "final non-production delivery preservation",
        "long-term audit readability",
        "paper-only safety preservation",
    ]:
        assert item in text


def test_archive_d3_final_release_note_mentions_release_summary():
    text = _text()

    for item in [
        "final non-production delivery package",
        "paper-only delivery package",
        "Dify-safe operator review package",
        "regression-first validation package",
        "release readiness package",
        "archive readiness package",
        "operator handoff package",
        "production deployment",
        "live trading package",
        "exchange execution package",
        "wallet custody package",
        "real-money trading package",
        "real trade signal package",
        "real fill confirmation package",
    ]:
        assert item in text


def test_archive_d3_final_release_note_mentions_completed_phases():
    text = _text()

    for item in [
        "Phase 1：Build Spine",
        "Phase 2：multi-asset MarketContext",
        "Phase 3：data ingestion and Dify integration",
        "Phase 4：schema hardening and fixture expansion",
        "Phase 5：paper-only sandbox execution",
        "Phase 6：policy / risk deny hardening",
        "Phase 7：guarded paper execution",
        "Phase 8：portfolio guarded paper execution",
        "Phase 9：global paper-only regression suite",
        "Phase 10：Dify-safe paper operations package",
        "Phase 11：release readiness / operator handoff / maintainability package",
        "Phase 12：documentation hardening / archive readiness / final non-production delivery package",
        "Final Archive：final archive readiness and immutable delivery snapshot",
    ]:
        assert item in text


def test_archive_d3_final_release_note_mentions_final_commands_and_state():
    text = _text()

    for item in [
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p10_dify_safe_package_summary.py",
        "python scripts/run_p11_release_readiness_package_summary.py",
        "python scripts/run_p12_acceptance_smoke.py",
        "python scripts/run_p12_final_delivery_package_summary.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
        "ready_for_p11_d10_bridge_plan true",
        "ready_for_p12_d8_closeout true",
        "ready_for_p12_d10_archive_bridge_plan true",
        "pytest 全部 passed",
        "git status --short 干净",
        "commit 已完成",
        "push 已完成",
        "P12 final delivery package summary completed",
        "P12 acceptance smoke completed",
        "safe_boundary_ok true",
    ]:
        assert item in text


def test_archive_d3_final_release_note_mentions_delivery_limitations():
    text = _text()

    for item in [
        "只能用于 paper-only local regression",
        "只能用于 non-production validation",
        "只能用于 Dify-safe operator review",
        "只能用于 release readiness review",
        "只能用于 archive readiness review",
        "只能用于 final operator handoff",
        "只能用于 final non-production delivery preparation",
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


def test_archive_d3_final_release_note_mentions_operator_review_requirement():
    text = _text()

    for item in [
        "operator_review_required true",
        "ready_for_operator_review true",
        "bypass_operator_review false",
        "bypass_policy_risk_safe_boundary false",
        "所有 passed 只能说明 paper-only / non-production regression passed",
        "所有结果不能解释成真实交易信号",
        "所有结果不能解释成真实成交",
        "operator 不能连接真实交易所",
        "operator 不能配置真实 API key",
        "operator 不能读取钱包私钥",
        "operator 不能真实下单",
        "operator 不能绕过 policy / risk / safe_boundary",
    ]:
        assert item in text


def test_archive_d3_final_release_note_mentions_archive_note_and_failed_rules():
    text = _text()

    for item in [
        "archive source branch must be main",
        "archive source remote must be origin/main",
        "archive source commit must be pushed",
        "archive snapshot must have clean git status",
        "archive snapshot must have pytest passed",
        "archive snapshot must include README.md",
        "archive snapshot must include PROJECT_STATE.md",
        "archive snapshot must include docs",
        "archive snapshot must include scripts",
        "archive snapshot must include fcf package",
        "archive snapshot must include fixtures",
        "archive snapshot must include tests",
        "archive snapshot must include final safety boundary declaration",
        "archive snapshot must include final delivery package summary",
        "立即停止",
        "不进入归档状态",
        "不进入下一阶段",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "docs/94_p10_failure_triage_guide.md",
    ]:
        assert item in text


def test_archive_d3_final_release_note_keeps_safety_boundaries():
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
    ]:
        assert item in text


def test_archive_d3_final_release_note_summary_still_ready_and_next_step():
    result = run_smoke()
    text = _text()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p12_d10_archive_bridge_plan"] is True
    assert result["package_summary"]["p12_acceptance_completed"] is True
    assert result["package_summary"]["ready_for_p12_d8_closeout"] is True
    assert result["package_summary"]["p11_release_readiness_summary_completed"] is True
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
    assert "Archive-D4" in text
    assert "final archive manifest" in text
