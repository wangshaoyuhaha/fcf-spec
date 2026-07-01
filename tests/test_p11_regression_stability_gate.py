from copy import deepcopy
from pathlib import Path

from fcf.regression.regression_stability_gate import evaluate_regression_stability_gate
from scripts.run_p10_dify_safe_package_summary import run_smoke


DOC = Path("docs/105_p11_regression_stability_gate.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def _package_result():
    return run_smoke()


def test_p11_regression_stability_gate_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P11-D6" in text
    assert "Regression Stability Gate" in text


def test_p11_regression_stability_gate_doc_mentions_version_and_entrypoint():
    text = _text()

    for item in [
        "gate_version = 0.1.0",
        "phase = P11",
        "day = P11-D6",
        "status = active",
        "evaluate_regression_stability_gate",
        "ready_for_p11_d7_acceptance_smoke",
    ]:
        assert item in text


def test_p11_regression_stability_gate_valid_package_passes():
    result = evaluate_regression_stability_gate(_package_result())

    assert result["status"] == "completed"
    assert result["gate"] == "regression_stability_gate"
    assert result["gate_version"] == "0.1.0"
    assert result["ok"] is True
    assert result["violations"] == []
    assert result["ready_for_p11_d7_acceptance_smoke"] is True


def test_p11_regression_stability_gate_all_checks_pass_for_current_package():
    result = evaluate_regression_stability_gate(_package_result())

    assert len(result["checks"]) >= 20
    for check in result["checks"]:
        assert check["passed"] is True


def test_p11_regression_stability_gate_fails_invalid_payload():
    result = evaluate_regression_stability_gate(None)

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert result["ready_for_p11_d7_acceptance_smoke"] is False
    assert len(result["violations"]) > 0


def test_p11_regression_stability_gate_fails_package_not_completed():
    payload = deepcopy(_package_result())
    payload["status"] = "failed"

    result = evaluate_regression_stability_gate(payload)

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert {
        "name": "package_status_completed",
        "actual": "failed",
        "expected": "completed",
    } in result["violations"]


def test_p11_regression_stability_gate_fails_not_ready_for_bridge():
    payload = deepcopy(_package_result())
    payload["package_summary"]["ready_for_p10_d10_bridge_plan"] = False

    result = evaluate_regression_stability_gate(payload)

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert {
        "name": "ready_for_p10_d10_bridge_plan",
        "actual": False,
        "expected": True,
    } in result["violations"]


def test_p11_regression_stability_gate_fails_safe_boundary_violation():
    payload = deepcopy(_package_result())
    payload["safe_boundary"]["real_execution"] = True

    result = evaluate_regression_stability_gate(payload)

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert {
        "name": "safe_boundary_real_execution",
        "actual": True,
        "expected": False,
    } in result["violations"]


def test_p11_regression_stability_gate_doc_mentions_failed_rules_and_safety():
    text = _text()

    for item in [
        "必须停止继续操作",
        "不进入 P11-D7",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "docs/94_p10_failure_triage_guide.md",
        "不接真实交易所 API",
        "不保存真实 API key",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
    ]:
        assert item in text


def test_p11_regression_stability_gate_doc_mentions_next_step():
    text = _text()

    assert "P11-D7" in text
    assert "Phase 11 acceptance smoke" in text
