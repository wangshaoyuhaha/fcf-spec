import json
import subprocess
import sys
from pathlib import Path

from scripts.run_final_archive_acceptance_smoke import run_smoke


DOC = Path("docs/126_archive_d6_final_archive_acceptance_smoke.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d6_acceptance_doc_exists_and_mentions_scope():
    text = _text()

    assert DOC.exists()
    assert "Archive-D6" in text
    assert "Final Archive Acceptance Smoke" in text
    assert "final_archive_acceptance_smoke_version = 0.1.0" in text

    for item in [
        "P12 final delivery package summary",
        "ready_for_p12_d10_archive_bridge_plan",
        "Archive-D1 final archive plan",
        "Archive-D2 immutable delivery snapshot checklist",
        "Archive-D3 final release note",
        "Archive-D4 final archive manifest",
        "Archive-D5 final operator archive handoff",
        "safe_boundary",
    ]:
        assert item in text


def test_archive_d6_acceptance_doc_mentions_command_outputs_and_targets():
    text = _text()

    for item in [
        "python scripts/run_final_archive_acceptance_smoke.py",
        "status",
        "runner",
        "runner_version",
        "acceptance_summary",
        "deliverables",
        "components",
        "safe_boundary",
        "ready_for_archive_d7_closeout true",
    ]:
        assert item in text


def test_archive_d6_acceptance_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "final_archive_acceptance_smoke"
    assert result["runner_version"] == "0.1.0"


def test_archive_d6_acceptance_summary_ready_for_closeout():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert summary["phase"] == "Final Archive"
    assert summary["accepted_days"] == [
        "Archive-D1",
        "Archive-D2",
        "Archive-D3",
        "Archive-D4",
        "Archive-D5",
        "Archive-D6",
    ]
    assert summary["p12_final_delivery_package_summary_completed"] is True
    assert summary["ready_for_p12_d10_archive_bridge_plan"] is True
    assert summary["archive_docs_all_present"] is True
    assert summary["final_archive_plan_present"] is True
    assert summary["immutable_delivery_snapshot_checklist_present"] is True
    assert summary["final_release_note_present"] is True
    assert summary["final_archive_manifest_present"] is True
    assert summary["final_operator_archive_handoff_present"] is True
    assert summary["final_archive_acceptance_smoke_present"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_archive_d7_closeout"] is True


def test_archive_d6_acceptance_deliverables_and_components():
    result = run_smoke()

    assert result["deliverables"]["deliverable_count"] == 8
    assert result["deliverables"]["present_count"] == 8
    assert result["deliverables"]["all_present"] is True

    assert result["components"]["p12_final_delivery_package_summary"]["status"] == "completed"
    assert result["components"]["p12_final_delivery_package_summary"]["ready_for_p12_d10_archive_bridge_plan"] is True
    assert result["components"]["p12_final_delivery_package_summary"]["safe_boundary_ok"] is True


def test_archive_d6_acceptance_safe_boundary():
    result = run_smoke()
    boundary = result["safe_boundary"]

    assert boundary["paper_only"] is True
    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["operator_review_required"] is True
    assert boundary["auto_live_trading"] is False
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False


def test_archive_d6_acceptance_doc_mentions_failed_rules_and_safety():
    text = _text()

    for item in [
        "立即停止",
        "不进入 Archive-D7",
        "不进入归档状态",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "不删除测试绕过失败",
        "不修改 safe_boundary 绕过失败",
        "不绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "docs/94_p10_failure_triage_guide.md",
        "不接真实交易所 API",
        "不保存真实 API key",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
    ]:
        assert item in text


def test_archive_d6_acceptance_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_final_archive_acceptance_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["acceptance_summary"]["ready_for_archive_d7_closeout"] is True
