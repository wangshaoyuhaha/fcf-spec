import json
import subprocess
import sys
from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/119_p12_post_closeout_final_delivery_package_summary.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_final_delivery_package_summary_doc_exists_and_mentions_scope():
    text = _text()

    assert DOC.exists()
    assert "P12-D9" in text
    assert "Post-closeout Final Delivery Package Summary" in text
    assert "P12 closeout project state" in text
    assert "P12 acceptance smoke" in text
    assert "P11 release readiness package summary" in text
    assert "final non-production delivery package" in text
    assert "archive readiness checklist" in text
    assert "final command index" in text
    assert "final artifact manifest" in text
    assert "final safety boundary declaration" in text
    assert "final operator delivery note" in text


def test_p12_final_delivery_package_summary_command_and_outputs():
    text = _text()

    assert "python scripts/run_p12_final_delivery_package_summary.py" in text

    for item in ["status", "runner", "runner_version", "package_summary", "deliverables", "components", "safe_boundary"]:
        assert item in text


def test_p12_final_delivery_package_summary_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p12_final_delivery_package_summary"
    assert result["runner_version"] == "0.1.0"


def test_p12_final_delivery_package_summary_ready_for_archive_bridge():
    result = run_smoke()
    summary = result["package_summary"]

    assert summary["phase"] == "P12"
    assert summary["post_closeout_final_delivery_package_summary"] is True
    assert summary["p12_acceptance_completed"] is True
    assert summary["ready_for_p12_d8_closeout"] is True
    assert summary["p11_release_readiness_summary_completed"] is True
    assert summary["ready_for_p11_d10_bridge_plan"] is True
    assert summary["deliverables_all_present"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_p12_d10_archive_bridge_plan"] is True


def test_p12_final_delivery_package_summary_deliverables():
    result = run_smoke()
    deliverables = result["deliverables"]

    assert deliverables["deliverable_count"] == 12
    assert deliverables["present_count"] == 12
    assert deliverables["all_present"] is True

    for name, item in deliverables["items"].items():
        assert name
        assert item["path"]
        assert item["exists"] is True


def test_p12_final_delivery_package_summary_components():
    result = run_smoke()
    components = result["components"]

    assert components["p12_acceptance_smoke"]["status"] == "completed"
    assert components["p12_acceptance_smoke"]["ready_for_p12_d8_closeout"] is True
    assert components["p11_release_readiness_package_summary"]["status"] == "completed"
    assert components["p11_release_readiness_package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert components["p11_release_readiness_package_summary"]["safe_boundary_ok"] is True
    assert components["final_non_production_delivery_package"]["exists"] is True
    assert components["p12_closeout_project_state"]["exists"] is True


def test_p12_final_delivery_package_summary_safe_boundary():
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


def test_p12_final_delivery_package_summary_doc_mentions_allowed_forbidden_safety_and_next_step():
    text = _text()

    for item in [
        "paper-only local regression",
        "non-production validation",
        "Dify-safe operator review",
        "release readiness review",
        "archive readiness review",
        "final operator handoff",
        "final non-production delivery preparation",
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
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
        "P12-D10",
        "Phase 12 to final archive bridge plan",
    ]:
        assert item in text


def test_p12_final_delivery_package_summary_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_p12_final_delivery_package_summary.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["package_summary"]["ready_for_p12_d10_archive_bridge_plan"] is True
