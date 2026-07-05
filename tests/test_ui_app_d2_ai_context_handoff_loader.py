from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sidecars" / "ui_app_1" / "ai_context_handoff_loader.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "ui_app_ai_context_handoff_loader",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_payload():
    return {
        "app_id": "AI-CONTEXT-1",
        "stage_id": "AI-CONTEXT-D6",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "ranked_watchlist": [
            {
                "symbol": "000001.SZ",
                "rank": 1,
                "score_breakdown": {"volume_price": 0.7},
                "reason_codes": ["VOLUME_PRICE_ANOMALY"],
                "risk_flags": ["OPERATOR_REVIEW_REQUIRED"],
            }
        ],
        "explanation_report": {
            "summary": "local read-only explanation",
            "risk_flags": ["OPERATOR_REVIEW_REQUIRED"],
        },
        "operator_review_summary": {
            "required": True,
            "status": "PENDING_OPERATOR_REVIEW",
        },
    }


def test_ui_app_d2_loader_file_exists():
    assert MODULE_PATH.exists()


def test_ui_app_d2_validates_required_payload():
    module = load_module()
    result = module.validate_ai_context_handoff_payload(sample_payload())

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["candidate_count"] == 1
    assert result["operator_review_required"] is True


def test_ui_app_d2_loads_local_json_payload(tmp_path):
    module = load_module()
    path = tmp_path / "ai_context_handoff.json"
    path.write_text(json.dumps(sample_payload()), encoding="utf-8")

    loaded = module.load_ai_context_handoff_payload(path)

    assert loaded["app_id"] == "AI-CONTEXT-1"
    assert loaded["ranked_watchlist"][0]["symbol"] == "000001.SZ"


def test_ui_app_d2_rejects_missing_file(tmp_path):
    module = load_module()
    missing = tmp_path / "missing.json"

    try:
        module.load_ai_context_handoff_payload(missing)
    except module.UIAppHandoffLoadError as exc:
        assert "handoff_payload_not_found" in str(exc)
    else:
        raise AssertionError("expected UIAppHandoffLoadError")


def test_ui_app_d2_rejects_non_json_suffix(tmp_path):
    module = load_module()
    path = tmp_path / "handoff.txt"
    path.write_text("{}", encoding="utf-8")

    try:
        module.load_ai_context_handoff_payload(path)
    except module.UIAppHandoffLoadError as exc:
        assert "handoff_payload_must_be_json" in str(exc)
    else:
        raise AssertionError("expected UIAppHandoffLoadError")


def test_ui_app_d2_rejects_invalid_json(tmp_path):
    module = load_module()
    path = tmp_path / "bad.json"
    path.write_text("{bad json", encoding="utf-8")

    try:
        module.load_ai_context_handoff_payload(path)
    except module.UIAppHandoffLoadError as exc:
        assert "handoff_payload_invalid_json" in str(exc)
    else:
        raise AssertionError("expected UIAppHandoffLoadError")


def test_ui_app_d2_rejects_trade_action_payload():
    module = load_module()
    payload = sample_payload()
    payload["buy_button_allowed"] = True

    result = module.validate_ai_context_handoff_payload(payload)

    assert result["ok"] is False
    assert "forbidden_true:buy_button_allowed" in result["errors"]


def test_ui_app_d2_rejects_operator_review_bypass():
    module = load_module()
    payload = sample_payload()
    payload["operator_review_bypass_allowed"] = True

    result = module.validate_ai_context_handoff_payload(payload)

    assert result["ok"] is False
    assert "forbidden_true:operator_review_bypass_allowed" in result["errors"]


def test_ui_app_d2_rejects_core_mutation():
    module = load_module()
    payload = sample_payload()
    payload["core_mutation_allowed"] = True

    result = module.validate_ai_context_handoff_payload(payload)

    assert result["ok"] is False
    assert "forbidden_true:core_mutation_allowed" in result["errors"]


def test_ui_app_d2_summarizes_valid_payload():
    module = load_module()
    summary = module.summarize_ai_context_handoff_payload(sample_payload())

    assert summary["ok"] is True
    assert summary["panel_ready"] is True
    assert summary["candidate_count"] == 1
    assert summary["operator_review_required"] is True
    assert "summary" in summary["explanation_report_keys"]
