from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/120_p12_to_final_archive_bridge_plan.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_to_final_archive_bridge_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D10" in text
    assert "Phase 12 to Final Archive Bridge Plan" in text


def test_p12_to_final_archive_bridge_mentions_p12_days():
    text = _text()

    for day in [
        "P12-D1",
        "P12-D2",
        "P12-D3",
        "P12-D4",
        "P12-D5",
        "P12-D6",
        "P12-D7",
        "P12-D8",
        "P12-D9",
        "P12-D10",
    ]:
        assert day in text


def test_p12_to_final_archive_bridge_mentions_final_archive_theme_and_route():
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


def test_p12_to_final_archive_bridge_mentions_candidate_directions():
    text = _text()

    for item in [
        "final archive plan",
        "immutable delivery snapshot checklist",
        "final release note",
        "final archive manifest",
        "final operator archive handoff",
        "final archive acceptance smoke",
        "final archive closeout",
    ]:
        assert item in text


def test_p12_to_final_archive_bridge_mentions_required_commands():
    text = _text()

    for item in [
        "python main.py",
        "python scripts/run_p12_acceptance_smoke.py",
        "python scripts/run_p12_final_delivery_package_summary.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
        "ready_for_p12_d8_closeout true",
        "ready_for_p12_d10_archive_bridge_plan true",
        "pytest 全部 passed",
        "git status --short 干净",
        "commit 已完成",
        "push 已完成",
    ]:
        assert item in text


def test_p12_to_final_archive_bridge_keeps_safety_boundaries():
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


def test_p12_to_final_archive_bridge_summary_still_ready():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p12_d10_archive_bridge_plan"] is True
    assert result["package_summary"]["p12_acceptance_completed"] is True
    assert result["package_summary"]["ready_for_p12_d8_closeout"] is True
    assert result["package_summary"]["p11_release_readiness_summary_completed"] is True
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
