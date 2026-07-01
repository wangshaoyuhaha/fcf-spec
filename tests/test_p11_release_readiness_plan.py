from pathlib import Path

from scripts.run_p10_dify_safe_package_summary import run_smoke


PLAN_DOC = Path("docs/100_p11_release_readiness_plan.md")


def test_p11_release_readiness_plan_doc_exists():
    assert PLAN_DOC.exists()


def test_p11_release_readiness_plan_mentions_phase11_theme():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "P11-D1" in text
    assert "Phase 11" in text
    assert "Release readiness, operator handoff package, and long-term maintainability" in text
    assert "发布准备、人工操作交接包与长期可维护性" in text


def test_p11_release_readiness_plan_mentions_core_targets():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "release readiness plan",
        "operator handoff package",
        "versioned run commands document",
        "artifact inventory and ownership map",
        "maintenance checklist",
        "regression stability gate",
        "long-term safety boundary checklist",
        "Phase 11 acceptance smoke",
    ]:
        assert item in text


def test_p11_release_readiness_plan_mentions_docs_and_commands():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "docs/101_p11_operator_handoff_package.md",
        "docs/102_p11_versioned_run_commands.md",
        "docs/103_p11_artifact_inventory.md",
        "docs/104_p11_maintenance_checklist.md",
        "docs/105_p11_regression_stability_gate.md",
        "docs/106_p11_long_term_safety_boundary_checklist.md",
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python scripts/run_p10_acceptance_smoke.py",
        "python scripts/run_p10_dify_safe_package_summary.py",
        "python -m pytest -q",
        "handle_dify_global_regression_request",
        "render_operator_review_response",
    ]:
        assert item in text


def test_p11_release_readiness_plan_mentions_route_and_safety():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for day in ["P11-D1", "P11-D2", "P11-D3", "P11-D4", "P11-D5", "P11-D6", "P11-D7", "P11-D8"]:
        assert day in text

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


def test_p11_release_readiness_plan_p10_package_summary_still_ready():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
    assert result["package_summary"]["p10_acceptance_completed"] is True
    assert result["package_summary"]["dify_global_regression_ok"] is True
    assert result["package_summary"]["operator_response_passed"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
