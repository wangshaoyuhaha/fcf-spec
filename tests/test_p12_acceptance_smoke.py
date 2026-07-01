import json
import subprocess
import sys
from pathlib import Path

from scripts.run_p12_acceptance_smoke import run_smoke


OPERATOR_DOC = Path("docs/116_p12_final_operator_delivery_note.md")
ACCEPTANCE_DOC = Path("docs/117_p12_acceptance_smoke.md")


def test_p12_operator_delivery_note_doc_exists_and_mentions_scope():
    text = OPERATOR_DOC.read_text(encoding="utf-8")

    assert OPERATOR_DOC.exists()
    assert "P12-D7" in text
    assert "Final Operator Delivery Note" in text
    assert "paper-only / non-production delivery package" in text
    assert "operator 可以做" in text
    assert "operator 不可以做" in text


def test_p12_operator_delivery_note_mentions_final_commands_and_entrypoints():
    text = OPERATOR_DOC.read_text(encoding="utf-8")

    for item in [
        "python main.py",
        "python scripts/run_p11_release_readiness_package_summary.py",
        "python scripts/run_p12_acceptance_smoke.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "ready_for_p11_d10_bridge_plan true",
        "ready_for_p12_d8_closeout true",
        "handle_dify_global_regression_request",
        "render_operator_review_response",
        "evaluate_regression_stability_gate",
    ]:
        assert item in text


def test_p12_operator_delivery_note_mentions_delivery_checklist():
    text = OPERATOR_DOC.read_text(encoding="utf-8")

    for item in [
        "docs/111_p12_final_non_production_delivery_package.md exists",
        "docs/112_p12_archive_readiness_checklist.md exists",
        "docs/113_p12_final_command_index.md exists",
        "docs/114_p12_final_artifact_manifest.md exists",
        "docs/115_p12_final_safety_boundary_declaration.md exists",
        "docs/116_p12_final_operator_delivery_note.md exists",
        "docs/117_p12_acceptance_smoke.md exists",
        "python scripts/run_p12_acceptance_smoke.py status completed",
        "ready_for_p12_d8_closeout true",
        "python -m pytest -q 全部 passed",
    ]:
        assert item in text


def test_p12_operator_delivery_note_mentions_failed_rules_and_safety():
    text = OPERATOR_DOC.read_text(encoding="utf-8")

    for item in [
        "立即停止",
        "不进入下一阶段",
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


def test_p12_operator_delivery_note_mentions_handoff_statement():
    text = OPERATOR_DOC.read_text(encoding="utf-8")

    for item in [
        "最终交接声明",
        "operator 必须通过人工复核读取结果",
        "operator 不能把任何 passed 结果解释为真实交易信号",
        "operator 不能把任何 passed 结果解释为真实成交",
        "operator 不能连接真实交易所",
        "operator 不能配置真实 API key",
        "operator 不能读取钱包私钥",
        "operator 不能真实下单",
        "operator 不能绕过 policy / risk / safe_boundary",
        "P12-D8",
        "Phase 12 closeout",
    ]:
        assert item in text


def test_p12_acceptance_doc_exists_and_mentions_scope():
    text = ACCEPTANCE_DOC.read_text(encoding="utf-8")

    assert ACCEPTANCE_DOC.exists()
    assert "P12-D7" in text
    assert "Phase 12 Acceptance Smoke" in text
    assert "python scripts/run_p12_acceptance_smoke.py" in text

    for day in ["P12-D1", "P12-D2", "P12-D3", "P12-D4", "P12-D5", "P12-D6", "P12-D7"]:
        assert day in text


def test_p12_acceptance_doc_mentions_outputs_and_targets():
    text = ACCEPTANCE_DOC.read_text(encoding="utf-8")

    for item in [
        "status",
        "runner",
        "runner_version",
        "acceptance_summary",
        "deliverables",
        "components",
        "safe_boundary",
        "status completed",
        "runner p12_acceptance_smoke",
        "runner_version 0.1.0",
        "p11_release_readiness_summary_completed true",
        "ready_for_p11_d10_bridge_plan true",
        "p12_docs_all_present true",
        "ready_for_p12_d8_closeout true",
    ]:
        assert item in text


def test_p12_acceptance_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p12_acceptance_smoke"
    assert result["runner_version"] == "0.1.0"


def test_p12_acceptance_summary_ready_for_closeout():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert summary["phase"] == "P12"
    assert summary["phase_name"] == "Documentation hardening, archive readiness, and final non-production delivery package"
    assert summary["accepted_days"] == ["P12-D1", "P12-D2", "P12-D3", "P12-D4", "P12-D5", "P12-D6", "P12-D7"]
    assert summary["p11_release_readiness_summary_completed"] is True
    assert summary["ready_for_p11_d10_bridge_plan"] is True
    assert summary["p12_docs_all_present"] is True
    assert summary["final_non_production_delivery_package_present"] is True
    assert summary["archive_readiness_checklist_present"] is True
    assert summary["final_command_index_present"] is True
    assert summary["final_artifact_manifest_present"] is True
    assert summary["final_safety_boundary_declaration_present"] is True
    assert summary["final_operator_delivery_note_present"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_p12_d8_closeout"] is True


def test_p12_acceptance_deliverables_and_components():
    result = run_smoke()

    assert result["deliverables"]["deliverable_count"] == 9
    assert result["deliverables"]["present_count"] == 9
    assert result["deliverables"]["all_present"] is True

    assert result["components"]["p11_release_readiness_package_summary"]["status"] == "completed"
    assert result["components"]["p11_release_readiness_package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["components"]["p11_release_readiness_package_summary"]["safe_boundary_ok"] is True
    assert result["components"]["p12_final_delivery_package"]["exists"] is True
    assert result["components"]["p12_final_safety_boundary_declaration"]["exists"] is True


def test_p12_acceptance_safe_boundary():
    result = run_smoke()
    boundary = result["safe_boundary"]

    assert boundary["paper_only"] is True
    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["no_real_exchange_api"] is True
    assert boundary["no_real_order_placement"] is True
    assert boundary["no_exchange_api_key_storage"] is True
    assert boundary["no_wallet_private_key_access"] is True
    assert boundary["no_real_account_balance_read"] is True
    assert boundary["no_real_position_read"] is True
    assert boundary["does_not_claim_real_trade_success"] is True
    assert boundary["operator_review_required"] is True
    assert boundary["auto_live_trading"] is False
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False


def test_p12_acceptance_doc_mentions_safety_boundaries_and_next_step():
    text = ACCEPTANCE_DOC.read_text(encoding="utf-8")

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
        "P12-D8",
        "Phase 12 closeout",
    ]:
        assert item in text


def test_p12_acceptance_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_p12_acceptance_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["acceptance_summary"]["ready_for_p12_d8_closeout"] is True
